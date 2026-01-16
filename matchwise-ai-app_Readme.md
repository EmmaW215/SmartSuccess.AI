# MatchWise AI - 完整技术栈与实现细节文档

## 📋 项目概述

**MatchWise AI**（GitHub: [matchwise-ai](https://github.com/EmmaW215/matchwise-ai)）是一个 AI 驱动的简历匹配与求职辅助平台，提供简历分析、匹配评分、求职信生成和模拟面试功能。

**Vercel 项目**: [matchwise-ai-app](https://vercel.com/emma-wangs-projects/matchwise-ai-app)

---

## 一、技术架构

### 1. 前端技术栈

| 技术 | 版本/配置 | 用途 |
|------|----------|------|
| **Next.js** | 15.5.7 | React 框架（App Router） |
| **React** | 19.1.0 | UI 库 |
| **TypeScript** | 5.8.3 | 类型安全开发 |
| **Tailwind CSS** | 4.x | 实用优先的 CSS 框架 |
| **React Markdown** | 10.1.0 | Markdown 渲染 |
| **Turbopack** | - | 快速开发构建工具 |
| **ESLint** | 9.x | 代码质量检查 |

**部署平台**: Vercel
- **主域名**: https://matchwise-ai.vercel.app/
- **备用域名**: https://resume-update-frontend.vercel.app/
- **Vercel 项目**: https://vercel.com/emma-wangs-projects/matchwise-ai-app

### 2. 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | >=0.109.0 | 高性能 Python Web 框架 |
| **Python** | 3.9+ | 后端编程语言 |
| **Uvicorn** | Standard | ASGI 服务器 |
| **aiohttp** | Latest | 异步 HTTP 客户端/服务器 |
| **PyPDF2** | Latest | PDF 文本提取 |
| **python-docx** | Latest | DOCX 文档处理 |
| **BeautifulSoup4** | Latest | HTML/XML 网页抓取 |
| **OpenAI SDK** | >=1.0.0 | GPT API 调用 |
| **Groq** | >=0.4.0 | 快速 LLM 推理（面试功能） |
| **Playwright** | Latest | 浏览器自动化（可选） |
| **Firebase Admin** | >=6.2.0 | Firebase 服务端 SDK |
| **Stripe** | Latest | 支付处理 |
| **Pydantic** | >=2.5.0 | 数据验证 |

**部署平台**: Render
- **API 端点**: https://resume-matcher-backend-rrrw.onrender.com
- **健康检查**: https://resume-matcher-backend-rrrw.onrender.com/health

### 3. AI 服务集成

**三层 AI 服务架构（自动故障转移）**：

```
1. OpenAI GPT-3.5-turbo (Primary)
   ↓ (失败时)
2. xAI Grok-3 (Fallback)
   ↓ (失败时)
3. Local Mock AI (Emergency Backup)
```

**实现逻辑**：
```python
async def call_ai_api(prompt, system_prompt):
    try:
        return await call_openai_api(prompt, system_prompt)
    except:
        try:
            return await call_xai_api(prompt, system_prompt)
        except:
            return generate_mock_ai_response(prompt, system_prompt)
```

---

## 二、核心功能实现

### 1. 简历分析系统

#### 1.1 文档处理

- **PDF 解析**: PyPDF2 提取文本内容
- **DOCX 解析**: python-docx 提取段落文本
- **支持格式**: `.pdf`, `.doc`, `.docx`
- **错误处理**: 格式验证与异常捕获

#### 1.2 工作描述抓取

- **方法**: BeautifulSoup4 + Requests
- **User-Agent**: 模拟浏览器请求头
- **超时设置**: 10 秒
- **错误处理**: 抓取失败时提示用户手动输入

**实现代码**：
```python
def extract_text_from_url(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...'
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator=" ", strip=True)
```

### 2. AI 分析流程

#### 2.1 六步分析流程

**1. 工作摘要生成**
- 提取：技能要求、职责、资格
- 输出：结构化工作摘要

**2. 简历匹配表**
- 对比：简历技能 vs 工作要求
- 状态：✅Strong / ✅Moderate-strong / ⚠️Partial / ❌Lack
- 输出：Markdown 表格格式

**3. 匹配度评分**
- **公式**: `Match Score = (Sum of weights) / (Total items)`
- **权重**: Strong=1.0, Moderate-strong=0.8, Partial=0.5, Lack=0.0
- **输出**: 百分比（保留两位小数）

**4. 优化简历摘要**
- 基于原始简历与职位要求
- 优化技能与经验描述
- **限制**: 1700 字符以内

**5. 优化工作经历**
- 修改最新工作经历
- **格式**: 项目符号列表
- **限制**: 最多 7 条

**6. 求职信生成**
- **格式**: 正式商务信函
- **内容**: 个人优势、匹配度、热情表达
- **语调**: 自信、诚实、专业

#### 2.2 API 端点

```http
POST /api/compare

Request:
  - job_url: string (工作描述 URL)
  - resume: File (PDF/DOCX 文件)

Response:
{
  "job_summary": string,
  "resume_summary": string (Markdown table),
  "match_score": number (0-100),
  "tailored_resume_summary": string,
  "tailored_work_experience": string[],
  "cover_letter": string
}
```

### 3. 前端 UI 实现

#### 3.1 主页面组件

- **文件上传**: 拖拽 + 点击选择
- **表单验证**: URL 格式、文件类型
- **加载状态**: 处理中提示
- **错误处理**: 友好错误信息
- **结果展示**: 6 个分析部分

#### 3.2 访客计数器

- **存储**: JSON 文件（后端）
- **API**: `GET/POST /api/visitor/count`
- **前端**: 实时显示访客数
- **管理**: 密码保护的 Admin 面板

---

## 三、扩展功能（本地开发版本）

基于本地代码，项目已扩展以下功能：

### 1. RAG（检索增强生成）系统

**技术栈**：
- ChromaDB / 轻量级向量存储
- OpenAI Embeddings (text-embedding-3-small)
- 文档分块与向量化

**实现文件**：
- `services/embedding_service.py` - 嵌入生成
- `services/vector_store.py` - 向量存储
- `services/rag_service.py` - RAG 查询逻辑

### 2. 模拟面试系统

**功能**：
- 语音面试（Web Speech API）
- 面试状态机（问候、菜单、自我介绍、技术、软技能）
- 个性化问题生成（基于 RAG）
- STAR 评分反馈

**API 端点**：
```
POST /api/interview/build-context
POST /api/interview/start
POST /api/interview/message
GET  /api/interview/session/{session_id}
POST /api/interview/analyze-response
GET  /api/interview/feedback/{session_id}
GET  /api/interview/status
GET  /api/interview/analytics/{user_id}
```

### 3. 用户管理系统

- **Firebase Authentication**: Google OAuth 登录
- **Firebase Firestore**: 用户数据存储
- **Stripe 集成**: 订阅管理
- **使用限制**: 免费/付费层级

**API 端点**：
```
GET  /api/user/status
GET  /api/user/can-generate
POST /api/user/use-trial
POST /api/create-checkout-session
POST /api/stripe-webhook
```

---

## 四、部署架构

### 前端部署（Vercel）

```
GitHub Repository
    ↓ (Auto Deploy)
Vercel Platform
    ↓
Edge Network (CDN)
    ↓
User Browser
```

**配置**：
- **自动部署**: GitHub push 触发
- **环境变量**: `NEXT_PUBLIC_BACKEND_URL`
- **构建**: Next.js 自动构建
- **域名**: 自定义域名支持

### 后端部署（Render）

```
GitHub Repository
    ↓ (Auto Deploy)
Render Platform
    ↓
FastAPI Server
    ↓
API Endpoints
```

**配置**：
- **环境变量**:
  - `OPENAI_API_KEY`
  - `XAI_API_KEY`
  - `GROQ_API_KEY`
  - `ALLOWED_ORIGINS`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `FIREBASE_CREDENTIALS`
- **健康检查**: `/health` 端点
- **自动重启**: 崩溃恢复

---

## 五、安全特性

### 1. CORS 配置
- 白名单域名
- 支持多前端域名
- 开发环境支持

### 2. 输入验证
- 文件类型检查
- URL 格式验证
- 文件大小限制

### 3. 错误处理
- 异常捕获
- 用户友好错误信息
- 日志记录

### 4. API 密钥管理
- 环境变量存储
- 不在代码中硬编码
- 服务端验证

---

## 六、性能优化

### 1. 异步处理
- FastAPI async/await
- aiohttp 异步 HTTP
- 非阻塞 AI 调用

### 2. 缓存策略
- 响应缓存（可选）
- 向量存储缓存

### 3. CDN
- Vercel Edge Network
- 静态资源加速

### 4. 故障转移
- 三层 AI 服务
- 自动切换
- 服务不中断

---

## 七、项目文件结构

```
matchwise-ai/
├── resume-matcher-frontend/     # Next.js 前端
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx        # 主页面
│   │       ├── layout.tsx       # 布局
│   │       ├── globals.css      # 全局样式
│   │       ├── components/      # React 组件
│   │       │   └── SimpleVisitorCounter.tsx
│   │       ├── api/             # API 路由
│   │       │   └── visitor-count/
│   │       ├── admin/           # 管理页面
│   │       │   └── visitor-stats/
│   │       ├── interview/       # 面试页面（扩展）
│   │       │   └── page.tsx
│   │       ├── dashboard/       # 仪表板（扩展）
│   │       │   └── page.tsx
│   │       └── demo/             # 演示页面
│   │           └── page.tsx
│   ├── public/                  # 静态资源
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── eslint.config.js
│
├── resume-matcher-backend/      # FastAPI 后端
│   ├── main.py                 # 主应用（999行，18个端点）
│   ├── requirements.txt        # Python 依赖
│   ├── services/               # 服务层（扩展）
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── rag_service.py
│   │   ├── interview_service.py
│   │   └── feedback_service.py
│   ├── models/                 # 数据模型（扩展）
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── prompts/                # 提示模板（扩展）
│   │   ├── __init__.py
│   │   └── interview_prompts.py
│   ├── visitor_count.json      # 访客计数存储
│   └── test_connection.py      # 连接测试
│
└── README.md                   # 项目文档
```

---

## 八、API 端点总览

### 核心端点（基础版本）

| 方法 | 端点 | 功能 |
|------|------|------|
| `POST` | `/api/compare` | 简历对比分析 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/` | 根端点 |

### 访客统计端点

| 方法 | 端点 | 功能 |
|------|------|------|
| `GET` | `/api/visitor/count` | 获取访客数 |
| `POST` | `/api/visitor/increment` | 增加访客数 |

### 用户管理端点（扩展）

| 方法 | 端点 | 功能 |
|------|------|------|
| `GET` | `/api/user/status` | 获取用户状态 |
| `GET` | `/api/user/can-generate` | 检查生成权限 |
| `POST` | `/api/user/use-trial` | 使用试用 |

### 支付端点（扩展）

| 方法 | 端点 | 功能 |
|------|------|------|
| `POST` | `/api/create-checkout-session` | 创建 Stripe 支付会话 |
| `POST` | `/api/stripe-webhook` | Stripe Webhook 处理 |

### 面试端点（扩展）

| 方法 | 端点 | 功能 |
|------|------|------|
| `POST` | `/api/interview/build-context` | 构建 RAG 上下文 |
| `POST` | `/api/interview/start` | 开始面试会话 |
| `POST` | `/api/interview/message` | 发送面试消息 |
| `GET` | `/api/interview/session/{session_id}` | 获取会话详情 |
| `POST` | `/api/interview/analyze-response` | 分析回答 |
| `GET` | `/api/interview/feedback/{session_id}` | 获取反馈 |
| `GET` | `/api/interview/status` | 获取面试状态 |
| `GET` | `/api/interview/analytics/{user_id}` | 用户分析数据 |

**总计**: 18 个 API 端点

---

## 九、技术亮点

1. **三层 AI 故障转移**: 确保服务可用性
2. **异步架构**: FastAPI + aiohttp 提升性能
3. **类型安全**: TypeScript + Pydantic 数据验证
4. **模块化设计**: 服务层分离，易于扩展
5. **生产就绪**: 完善的错误处理、日志、监控

---

## 十、成本估算

| 服务 | 免费额度 | 预计成本 |
|------|---------|---------|
| **Vercel** | 100GB 带宽 | $0 |
| **Render** | 750 小时/月 | $0 |
| **OpenAI API** | - | ~$5-10/月 |
| **xAI API** | - | ~$0-5/月 |
| **Groq API** | 6K 请求/天 | $0（免费层） |
| **Firebase** | Spark 计划 | $0 |

**总计**: 约 **$0-20/月**（MVP 阶段）

---

## 十一、环境变量配置

### 前端环境变量（.env.local）

```env
NEXT_PUBLIC_BACKEND_URL=https://resume-matcher-backend-rrrw.onrender.com
```

### 后端环境变量（Render）

```env
# AI 服务
OPENAI_API_KEY=sk-xxx
XAI_API_KEY=xxx
GROQ_API_KEY=gsk_xxx

# CORS
ALLOWED_ORIGINS=https://matchwise-ai.vercel.app,https://resume-update-frontend.vercel.app

# 支付
STRIPE_SECRET_KEY=sk_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Firebase
FIREBASE_CREDENTIALS={...}  # JSON 格式
```

---

## 十二、开发指南

### 前端开发

```bash
cd resume-matcher-frontend
npm install
npm run dev  # 使用 Turbopack
```

### 后端开发

```bash
cd resume-matcher-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 十三、总结

**MatchWise AI** 是一个功能完整的 AI 求职辅助平台，包含：

✅ **核心功能**: 简历分析、匹配评分、求职信生成  
✅ **扩展功能**: RAG、模拟面试、用户管理  
✅ **技术栈**: Next.js 15.5.7 + FastAPI + AI 服务  
✅ **部署**: Vercel + Render  
✅ **架构**: 模块化、可扩展、生产就绪  

项目已具备从 MVP 到完整产品的技术基础，可继续扩展更多功能。

---

## 参考资料

- **GitHub 仓库**: https://github.com/EmmaW215/matchwise-ai
- **Vercel 项目**: https://vercel.com/emma-wangs-projects/matchwise-ai-app
- **前端部署**: https://matchwise-ai.vercel.app/
- **后端 API**: https://resume-matcher-backend-rrrw.onrender.com

---

**文档版本**: 1.0  
**最后更新**: 2025年1月  
**维护者**: Emma Wang
