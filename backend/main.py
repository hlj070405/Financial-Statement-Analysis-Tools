from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import os
from typing import Optional
import json
from dotenv import load_dotenv
import re

# 加载 .env 文件
load_dotenv()

app = FastAPI(title="PDF RAG Analysis System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")

print(f"[启动] DIFY_API_URL: {DIFY_API_URL}")
print(f"[启动] DIFY_API_KEY: {DIFY_API_KEY[:20]}..." if DIFY_API_KEY else "[启动] DIFY_API_KEY: 未设置")

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

@app.post("/api/chat")
async def chat_with_document(file_id: str, message: str, conversation_id: Optional[str] = None):
    """与文档进行多轮对话"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            headers = {
                'Authorization': f'Bearer {DIFY_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "inputs": {
                    "file": file_id
                },
                "query": message,
                "response_mode": "streaming",
                "user": "default-user"
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = await client.post(
                f"{DIFY_API_URL}/chat-messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                  detail=f"对话失败: {response.text}")
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
