from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List
import json
from dotenv import load_dotenv
import re
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import dateutil.parser

from database import get_db, init_db, User, Stock, ChatHistory, HotspotNews
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas import UserCreate, UserLogin, UserResponse, Token
from file_upload import upload_file_to_dify
from economic_data import EconomicDataService
from deepseek_service import DeepSeekService
from chat_history_service import ChatHistoryService
from hotspot_service import HotspotService
import uuid

# 加载 .env 文件
load_dotenv()

# 环境变量
DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

app = FastAPI(title="PDF RAG Analysis System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup_event():
    init_db()

print(f"[启动] DIFY_API_URL: {DIFY_API_URL}")
print(f"[启动] DIFY_API_KEY: {DIFY_API_KEY[:20]}..." if DIFY_API_KEY else "[启动] DIFY_API_KEY: 未设置")

# 初始化DeepSeek服务
deepseek_service = DeepSeekService(DEEPSEEK_API_KEY)

# 初始化热点服务
hotspot_service = HotspotService()

# 创建全局httpx客户端用于Dify API调用,复用连接以提高性能
dify_http_client = None

async def get_dify_client():
    """获取或创建Dify HTTP客户端"""
    global dify_http_client
    if dify_http_client is None:
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0)
        dify_http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=5.0),
            limits=limits,
            http2=False  # 禁用HTTP/2,使用HTTP/1.1可能更稳定
        )
    return dify_http_client

class AnalysisRequest(BaseModel):
    file_id: str
    question: str
    style: Optional[str] = "专业分析"

class AnalysisResponse(BaseModel):
    analysis: str
    chart_data: Optional[dict] = None
    sources: Optional[list] = None

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """上传 PDF 文件到 Dify"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    try:
        contents = await file.read()
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            files = {'file': (file.filename, contents, 'application/pdf')}
            headers = {'Authorization': f'Bearer {DIFY_API_KEY}'}
            
            # Dify 文件上传 API
            response = await client.post(
                f"{DIFY_API_URL}/files/upload",
                headers=headers,
                files=files,
                data={'user': 'default-user'}
            )
            
            if response.status_code != 200 and response.status_code != 201:
                error_detail = f"Dify 上传失败 (状态码: {response.status_code}): {response.text}"
                print(f"ERROR: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            result = response.json()
            file_id = result.get("id") or result.get("file_id")
            
            if not file_id:
                raise HTTPException(status_code=500, detail=f"无法获取文件ID: {result}")
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "message": "上传成功"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"上传失败: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/analyze")
async def analyze_document(request: AnalysisRequest):
    """调用 Dify 工作流分析文档 - 流式响应"""
    
    async def generate_stream():
        try:
            print(f"[分析请求] file_id: {request.file_id}, question: {request.question[:50]}..., style: {request.style}")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                headers = {
                    'Authorization': f'Bearer {DIFY_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                # Dify 工作流的文件输入格式
                file_input = {
                    "transfer_method": "local_file",
                    "upload_file_id": request.file_id,
                    "type": "document"
                }
                
                payload = {
                    "inputs": {
                        "input": request.question,
                        "files": file_input,
                        "style": request.style
                    },
                    "response_mode": "streaming",
                    "user": "default-user"
                }
                
                print(f"[调用 Dify] URL: {DIFY_API_URL}/workflows/run")
                
                async with client.stream(
                    'POST',
                    f"{DIFY_API_URL}/workflows/run",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status_code != 200:
                        error_msg = f"分析失败 (状态码: {response.status_code})"
                        print(f"ERROR: {error_msg}")
                        yield f"data: {{\"error\": \"{error_msg}\"}}\n\n"
                        return
                    
                    print(f"[Dify 响应] Status: {response.status_code} - 开始流式接收")
                    
                    full_text = ""
                    in_thinking = False
                    
                    async for line in response.aiter_lines():
                        if not line or line.startswith(':'):
                            continue
                        
                        if line.startswith('data: '):
                            data_str = line[6:]
                            
                            try:
                                data = json.loads(data_str)
                                event = data.get('event')
                                
                                # 处理不同的事件类型
                                if event == 'workflow_started':
                                    print(f"[工作流启动] run_id: {data.get('workflow_run_id')}")
                                    yield f"data: {{\"type\": \"start\"}}\n\n"
                                
                                elif event == 'node_started':
                                    node_type = data.get('data', {}).get('node_type')
                                    print(f"[节点启动] {node_type}")
                                
                                elif event == 'text_chunk' or event == 'agent_thought':
                                    # 提取文本内容
                                    text = data.get('data', {}).get('text', '')
                                    
                                    if text:
                                        full_text += text
                                        
                                        # 检测 thinking 标签
                                        if '<thinking>' in text:
                                            in_thinking = True
                                        if '</thinking>' in text:
                                            in_thinking = False
                                            continue
                                        
                                        # 只发送非 thinking 内容
                                        if not in_thinking and '<thinking>' not in text:
                                            # 清理可能残留的 thinking 标签
                                            clean_text = re.sub(r'</?thinking>', '', text)
                                            if clean_text.strip():
                                                # 转义 JSON 字符串
                                                escaped_text = json.dumps(clean_text)[1:-1]
                                                yield f"data: {{\"type\": \"text\", \"content\": \"{escaped_text}\"}}\n\n"
                                
                                elif event == 'workflow_finished':
                                    # 清理完整文本中的 thinking 内容
                                    clean_full_text = re.sub(r'<thinking>.*?</thinking>', '', full_text, flags=re.DOTALL)
                                    clean_full_text = clean_full_text.strip()
                                    
                                    print(f"[分析完成] 原始长度: {len(full_text)}, 清理后: {len(clean_full_text)}")
                                    yield f"data: {{\"type\": \"done\", \"total_length\": {len(clean_full_text)}}}\n\n"
                                
                                elif event == 'error':
                                    error_msg = data.get('data', {}).get('message', '未知错误')
                                    print(f"ERROR: {error_msg}")
                                    yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
                            
                            except json.JSONDecodeError:
                                continue
        
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR: 流式处理异常: {error_msg}")
            import traceback
            traceback.print_exc()
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    files: Optional[list] = None
    style: Optional[str] = "专业分析"
    save_history: Optional[bool] = True

@app.post("/api/chat")
async def chat_with_ai(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """智能对话接口 - 支持财务分析、舆情追踪等 (Dify Workflow模式 - 流式响应)"""
    import time
    func_start = time.time()
    print(f"[{func_start:.3f}] 进入 chat_with_ai 函数")
    
    # 如果没有conversation_id，生成一个新的
    conversation_id = request.conversation_id or str(uuid.uuid4())
    is_new_conversation = not request.conversation_id
    
    print(f"\n{'='*60}")
    print(f"收到聊天请求 - 用户: {current_user.username}")
    print(f"会话ID: {conversation_id} {'(新会话)' if is_new_conversation else '(继续会话)'}")
    print(f"消息: {request.message[:100]}...")
    print(f"文件: {request.files}")
    print(f"风格: {request.style}")
    print(f"{'='*60}\n")
    
    async def generate_stream():
        # import time (already imported in outer scope if we move it, but keeping inner for safety)
        import time 
        try:
            start_time = time.time()
            print(f"[{start_time:.3f}] 开始生成流式响应 (距离函数开始: {start_time - func_start:.3f}秒)...")
            
            # 立即发送一个初始事件,让前端知道连接已建立
            yield f"data: {json.dumps({'type': 'connected', 'message': '已连接到服务器'})}\n\n"
            
            # 使用全局客户端复用连接
            client = await get_dify_client()
            headers = {
                'Authorization': f'Bearer {DIFY_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Dify Workflow API 使用 /workflows/run 端点
            payload = {
                "inputs": {
                    "input": request.message,
                    "style": request.style or "专业分析"
                },
                "response_mode": "streaming",
                "user": current_user.username
            }
            
            # 如果有文件,添加到inputs中
            if request.files and len(request.files) > 0:
                file = request.files[0]
                file_id = file.get("file_id") or file.get("id")
                if file_id:
                    file_obj = {
                        "type": file.get("type", "document"),
                        "transfer_method": "local_file",
                        "upload_file_id": file_id
                    }
                    payload["inputs"]["files"] = file_obj
                    print(f"添加文件到请求: {file_id}")
                else:
                    print("警告: 文件对象中没有找到file_id或id字段")
            
            print(f"[{time.time():.3f}] 发送请求到 Dify: {DIFY_API_URL}/workflows/run")
            print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            request_start = time.time()
            # 发送流式请求
            async with client.stream(
                'POST',
                f"{DIFY_API_URL}/workflows/run",
                headers=headers,
                json=payload
            ) as response:
                connection_time = time.time() - request_start
                print(f"[{time.time():.3f}] 收到 Dify 响应状态码: {response.status_code} (连接耗时: {connection_time:.2f}秒)")
                
                if response.status_code != 200:
                    error_detail = await response.aread()
                    error_msg = f'Dify工作流执行失败: {error_detail.decode()}'
                    print(f"错误: {error_msg}")
                    yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                    return
                
                # 逐行读取SSE流
                has_streamed_text = False
                first_event_received = False
                
                print(f"[{time.time():.3f}] 开始读取 Dify 流式响应...")
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data_str = line[6:]  # 去掉 'data: ' 前缀
                        
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                event = data.get('event')
                                
                                if not first_event_received:
                                    first_event_time = time.time() - request_start
                                    print(f"[{time.time():.3f}] 收到首个事件: {event} (Dify处理耗时: {first_event_time:.2f}秒)")
                                    first_event_received = True
                                else:
                                    print(f"[{time.time():.3f}] 收到事件: {event}")
                                
                                # 处理不同的事件类型
                                if event == 'workflow_started':
                                    print("工作流已启动")
                                    yield f"data: {json.dumps({'type': 'start', 'data': data})}\n\n"
                                
                                elif event == 'node_started':
                                    node_title = data.get('data', {}).get('title', 'unknown')
                                    print(f"节点启动: {node_title}")
                                    yield f"data: {json.dumps({'type': 'node_start', 'data': data})}\n\n"
                                
                                elif event == 'node_finished':
                                    node_title = data.get('data', {}).get('title', 'unknown')
                                    print(f"节点完成: {node_title}")
                                    yield f"data: {json.dumps({'type': 'node_finish', 'data': data})}\n\n"
                                
                                elif event == 'text_chunk':
                                    # 文本块 - 逐字输出
                                    text = data.get('data', {}).get('text', '')
                                    if text:
                                        has_streamed_text = True
                                        print(f"文本块: {text[:20]}..." if len(text) > 20 else f"文本块: {text}")
                                        yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"
                                
                                elif event == 'workflow_finished':
                                    print("工作流完成")
                                    # 工作流完成
                                    # 如果没有流式输出文本，尝试从outputs中获取完整文本
                                    if not has_streamed_text:
                                        print("未收到流式文本块,尝试从outputs提取完整文本")
                                        outputs = data.get('data', {}).get('outputs', {})
                                        if outputs and 'text' in outputs:
                                            text = outputs['text']
                                            if text:
                                                print(f"从outputs提取到文本,长度: {len(text)}")
                                                yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"
                                    else:
                                        print(f"已流式输出文本")
                                    
                                    yield f"data: {json.dumps({'type': 'finish', 'data': data})}\n\n"
                                    yield "data: [DONE]\n\n"
                                    print("流式响应完成\n")
                                
                                elif event == 'error':
                                    error_msg = data.get('message', '未知错误')
                                    print(f"Dify错误: {error_msg}")
                                    yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                                    
                            except json.JSONDecodeError as je:
                                print(f"JSON解析错误: {je}, 数据: {data_str[:100]}")
                                continue
        
        except Exception as e:
            print(f"流式生成异常: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Conversation-ID": conversation_id
        }
    )

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """上传文件到Dify"""
    try:
        result = await upload_file_to_dify(
            file=file,
            dify_api_url=DIFY_API_URL,
            dify_api_key=DIFY_API_KEY,
            user=current_user.username
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/api/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/api/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

# ==================== 聊天历史管理API ====================

@app.get("/api/chat/history")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的聊天历史列表"""
    history = ChatHistoryService.get_user_chat_history(db, current_user.id)
    return {"history": history}

@app.get("/api/chat/history/{conversation_id}")
def get_chat_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取特定会话的消息历史"""
    chat = ChatHistoryService.get_chat_messages(db, conversation_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="会话不存在")
    return chat

@app.delete("/api/chat/history/{conversation_id}")
def delete_chat_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天历史"""
    success = ChatHistoryService.delete_chat(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "删除成功"}

@app.post("/api/chat/save")
async def save_chat_manually(
    conversation_id: str,
    message: str,
    response: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动保存聊天记录(用于前端在流式响应结束后调用)"""
    await ChatHistoryService.save_or_update_chat(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id,
        message=message,
        response=response,
        deepseek_service=deepseek_service,
        is_first_message=False
    )
    return {"message": "保存成功", "conversation_id": conversation_id}

# ==================== AKShare经济数据API ====================

@app.get("/api/economic/stock/realtime/{symbol}")
def get_stock_realtime(symbol: str, current_user: User = Depends(get_current_user)):
    """获取股票实时行情"""
    data = EconomicDataService.get_stock_realtime(symbol)
    return data

@app.get("/api/economic/stock/news/{symbol}")
def get_stock_news(symbol: str, limit: int = 10, current_user: User = Depends(get_current_user)):
    """获取股票新闻"""
    news = EconomicDataService.get_stock_news(symbol, limit)
    return {"news": news}

@app.get("/api/economic/stock/financial/{symbol}")
def get_financial_indicators(symbol: str, current_user: User = Depends(get_current_user)):
    """获取财务指标"""
    data = EconomicDataService.get_financial_indicators(symbol)
    return data

@app.get("/api/economic/stock/history/{symbol}")
def get_stock_history(
    symbol: str, 
    period: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取股票历史行情"""
    history = EconomicDataService.get_stock_history(symbol, period, start_date, end_date)
    return {"history": history}

@app.get("/api/economic/macro/cpi")
def get_macro_cpi(current_user: User = Depends(get_current_user)):
    """获取CPI数据"""
    data = EconomicDataService.get_macro_cpi()
    return data

@app.get("/api/economic/macro/gdp")
def get_macro_gdp(current_user: User = Depends(get_current_user)):
    """获取GDP数据"""
    data = EconomicDataService.get_macro_gdp()
    return data

@app.get("/api/economic/industry/ranking")
def get_industry_ranking(current_user: User = Depends(get_current_user)):
    """获取行业板块排名"""
    ranking = EconomicDataService.get_industry_ranking()
    return {"ranking": ranking}

@app.get("/api/economic/stock/search")
def search_stock(keyword: str, limit: int = 10, current_user: User = Depends(get_current_user)):
    """搜索股票"""
    stocks = EconomicDataService.search_stock(keyword, limit=limit)
    return {"stocks": stocks}


@app.post("/api/economic/stock/sync")
def sync_stock_list(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """同步全量股票列表到本地数据库"""
    result = EconomicDataService.sync_stock_list(db)
    return result


@app.get("/api/economic/stock/search_local")
def search_stock_local(keyword: str, limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """从本地数据库模糊搜索股票"""
    q = keyword.strip()
    if not q:
        return {"stocks": []}

    stocks = (
        db.query(Stock)
        .filter((Stock.name.like(f"%{q}%")) | (Stock.code.like(f"%{q}%")))
        .order_by(Stock.code.asc())
        .limit(limit)
        .all()
    )

    return {
        "stocks": [
            {"code": s.code, "name": s.name}
            for s in stocks
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ==================== 热点新闻API ====================

@app.get("/api/hotspot/categories")
def get_hotspot_categories(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """获取分类热点新闻"""
    result = hotspot_service.get_categorized_news(limit_per_category=limit)
    return result

@app.get("/api/hotspot/news")
def get_hotspot_news(
    category: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从数据库获取热点新闻"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    query = db.query(HotspotNews).filter(HotspotNews.date == today)
    
    if category:
        query = query.filter(HotspotNews.category == category)
    
    news = query.order_by(HotspotNews.rank.asc()).limit(limit).all()
    
    return {
        "success": True,
        "news": [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "source_name": n.source_name,
                "category": n.category,
                "rank": n.rank,
                "url": n.url,
                "first_seen": n.first_seen.isoformat() if n.first_seen else None,
                "last_seen": n.last_seen.isoformat() if n.last_seen else None,
                "appear_count": n.appear_count
            }
            for n in news
        ],
        "count": len(news)
    }

@app.get("/api/hotspot/search")
def search_hotspot_news(
    keyword: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """搜索热点新闻"""
    result = hotspot_service.search_news(keyword, limit)
    return result

@app.post("/api/hotspot/sync")
async def sync_hotspot_news(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """同步热点新闻到数据库"""
    from datetime import datetime
    
    # 获取分类新闻
    result = hotspot_service.get_categorized_news(limit_per_category=50)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "同步失败"))
    
    today = datetime.now().strftime("%Y-%m-%d")
    synced_count = 0
    updated_count = 0
    
    for category, news_list in result["categories"].items():
        for news_item in news_list:
            # 检查是否已存在
            existing = db.query(HotspotNews).filter(
                HotspotNews.title == news_item["title"],
                HotspotNews.source == news_item["source"],
                HotspotNews.date == today
            ).first()
            
            if existing:
                # 更新
                existing.rank = news_item["rank"]
                existing.last_seen = datetime.now()
                existing.appear_count += 1
                updated_count += 1
            else:
                # 新增
                first_seen_time = datetime.now()
                # 尝试使用 news_item 中的 first_time
                if news_item.get("first_time"):
                    try:
                        # 尝试解析 ISO 格式或其他格式，这里假设是字符串
                        # 如果是 TrendRadar 返回的时间戳或格式化字符串
                        # 简单的尝试转换，失败则回退到当前时间
                        import dateutil.parser
                        parsed_time = dateutil.parser.parse(str(news_item["first_time"]))
                        first_seen_time = parsed_time
                    except:
                        pass

                new_news = HotspotNews(
                    title=news_item["title"],
                    source=news_item["source"],
                    source_name=news_item["source_name"],
                    category=category,
                    rank=news_item["rank"],
                    url=news_item.get("url", ""),
                    mobile_url=news_item.get("mobile_url", ""),
                    first_seen=first_seen_time,
                    last_seen=datetime.now(),
                    appear_count=1,
                    date=today
                )
                db.add(new_news)
                synced_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "synced": synced_count,
        "updated": updated_count,
        "total": synced_count + updated_count,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
