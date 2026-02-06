# 📊 企业财报智能分析系统

基于 Dify + Vue 3 的企业财报智能分析与决策支持系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dify](https://img.shields.io/badge/Dify-Powered-orange.svg)](https://dify.ai/)

## ✨ 功能特性

- 🚀 **实时流式输出** - AI 分析结果边生成边显示，无需等待
- 📄 **PDF 智能解析** - 支持拖拽上传，自动提取财报内容
- 🤖 **RAG 智能问答** - 基于文档内容的精准分析
- 📝 **Markdown 渲染** - 专业的格式化输出，支持表格、列表、代码块
- 🎨 **现代化 UI** - Vue 3 + TailwindCSS，响应式设计
- 🔄 **Thinking 过滤** - 自动过滤 AI 思考过程，只显示最终结果
- 📊 **数据可视化** - ECharts 图表支持（可扩展）

## 🏗️ 系统架构

```
前端 (Vue 3 + Vite + TailwindCSS)
    ↓ SSE 流式通信
FastAPI 后端 (Python)
    ↓ API 调用
Dify 工作流引擎
    ↓
LLM (Kimi-K2.5 / 其他模型)
Dify API (工作流 + 知识库)
    ↓
LLM (GPT-4 / Claude / 国产大模型)
```

## 快速开始

### 1. 启动 Dify

```bash
cd dify/docker
docker-compose up -d
```

访问 http://localhost 完成初始化配置。

### 2. 在 Dify 中创建工作流

#### 创建知识库
1. 进入 Dify 控制台 → 知识库
2. 创建新知识库 "企业财报知识库"
3. 配置切分策略：
   - 切分方式：自动
   - 分段长度：500 tokens
   - 重叠长度：50 tokens

#### 创建工作流应用
1. 创建新应用 → 选择"工作流"
2. 添加节点：

**输入节点**
- `file` (文件类型)
- `question` (文本类型)
- `company_name` (文本类型，可选)

**文档提取器节点**
- 输入：`file`
- 输出：`document_text`

**知识库检索节点**
- 知识库：选择刚创建的知识库
- 查询变量：`question`
- Top K：3

**LLM 节点**
- 模型：GPT-4 或其他
- 系统提示词：
```
你是一个专业的财务分析师。基于用户上传的财报文档和检索到的相关信息，进行深入分析。

分析要求：
1. 提取关键财务指标（营收、净利润、ROE、资产负债率等）
2. 分析盈利能力、偿债能力、运营效率
3. 识别潜在风险和机会
4. 提供具体的数据支撑
5. 引用原文时标注来源

输出格式：
{
  "analysis": "详细分析文本",
  "chart_data": {
    "title": "图表标题",
    "xAxis": ["2020", "2021", "2022", "2023"],
    "series": [
      {
        "name": "营收",
        "type": "line",
        "data": [100, 120, 150, 180]
      }
    ]
  },
  "sources": [
    {"content": "引用内容", "page": 页码}
  ]
}
```

**输出节点**
- `analysis` (文本)
- `chart_data` (JSON)
- `sources` (数组)

3. 发布工作流，获取 API Key

### 3. 配置后端

```bash
cd pdf-rag-system/backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入 Dify API Key
```

`.env` 文件内容：
```env
DIFY_API_URL=http://localhost/v1
DIFY_API_KEY=your-dify-api-key-here
DIFY_API_KEY=app-你的API密钥
```

### 4. 启动服务

```bash
# 启动后端
python main.py
```

### 4. 启动 Vue 前端（推荐）

```bash
cd frontend-vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

### 5. 或使用原版前端

```bash
cd frontend
python -m http.server 3000
```

访问 http://localhost:3000

## 使用说明

1. **上传 PDF**：拖拽或点击上传财报 PDF 文件
2. **输入问题**：输入你想分析的问题（如"分析盈利能力"）
3. **开始分析**：点击按钮，等待 AI 分析
4. **查看结果**：
   - 文字分析报告
   - 可视化图表（如有）
   - 引用来源追溯

## API 接口

### 上传 PDF
```bash
POST /api/upload-pdf
Content-Type: multipart/form-data

file: <PDF文件>
```

### 分析文档
```bash
POST /api/analyze
Content-Type: application/json

{
  "file_id": "文件ID",
  "question": "分析问题",
  "company_name": "公司名称（可选）"
}
```

### 多轮对话
```bash
POST /api/chat
Content-Type: application/json

{
  "file_id": "文件ID",
  "message": "对话内容",
  "conversation_id": "会话ID（可选）"
}
```

## 进阶配置

### 自定义图表类型

修改 Dify 工作流的 LLM 输出，支持更多图表：

```json
{
  "chart_data": {
    "type": "radar",  // line, bar, pie, radar, scatter
    "title": "财务健康度雷达图",
    "indicator": [
      {"name": "盈利能力", "max": 100},
      {"name": "偿债能力", "max": 100},
      {"name": "运营效率", "max": 100}
    ],
    "series": [{
      "type": "radar",
      "data": [{"value": [80, 70, 90]}]
    }]
  }
}
```

### 添加自定义工具

在 Dify 工作流中添加 HTTP 请求节点，调用外部 API：

```python
# 示例：财务指标计算 API
@app.post("/api/calculate-ratios")
async def calculate_ratios(data: dict):
    revenue = data.get('revenue')
    net_profit = data.get('net_profit')
    
    return {
        "profit_margin": net_profit / revenue * 100,
        "roe": calculate_roe(data),
        "debt_ratio": calculate_debt_ratio(data)
    }
```

## 部署到生产环境

### Docker 部署

```bash
# 构建镜像
docker build -t pdf-rag-system .

# 运行容器
docker run -d -p 8000:8000 \
  -e DIFY_API_URL=http://dify:80/v1 \
  -e DIFY_API_KEY=your-key \
  pdf-rag-system
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend;
        index index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## 常见问题

**Q: 上传失败？**
A: 检查 Dify API Key 是否正确，Dify 服务是否运行

**Q: 分析结果不准确？**
A: 优化 Dify 工作流的 Prompt，增加知识库内容

**Q: 图表不显示？**
A: 确保 LLM 输出的 chart_data 格式正确

## 技术栈

- **前端**: HTML5, TailwindCSS, ECharts
- **后端**: FastAPI, Python 3.10+
- **AI**: Dify, OpenAI GPT-4
- **数据库**: PostgreSQL (Dify 内置)
- **向量库**: Qdrant (Dify 内置)

## 许可证

MIT License
