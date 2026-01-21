# 部署验证指南 - 逐步检查清单

本指南将帮助您逐步验证三个关键配置：

1. ✅ Render后端服务的Interview/RAG服务状态
2. ✅ 生产环境环境变量配置
3. ✅ MatchWise AI iframe嵌入权限设置

---

## 🔍 第一部分：验证Render后端服务的Interview/RAG服务状态

### 步骤 1.1：访问Render Dashboard

1. **打开浏览器**，访问：https://dashboard.render.com
2. **登录**您的Render账户
3. **找到服务**：在服务列表中查找 `resume-matcher-backend` 服务

### 步骤 1.2：检查服务运行状态

**检查点：**
- ✅ **服务状态**应该显示为 "Live"（绿色）
- ✅ **最近部署**应该显示为 "Successful"
- ⚠️ 如果是 "Failed" 或 "Building"，需要查看日志

**操作：**
1. 点击服务名称进入详情页面
2. 查看页面顶部的状态指示器
3. 记录当前状态：`[填写：Live / Failed / Building]`

### 步骤 1.3：检查部署日志

**目的：**确认Interview/RAG服务是否正确加载

**操作：**
1. 在服务详情页面，点击 **"Logs"** 标签
2. 滚动到日志底部（最新日志）
3. **查找关键日志信息：**

**✅ 成功标志：**
```
✅ Interview services initialized successfully
```

**❌ 失败标志：**
```
Warning: Interview services not available: ...
Warning: Could not initialize interview services: ...
```

**记录结果：**
- [ ] 看到了 "Interview services initialized successfully"？
- [ ] 看到了任何错误信息？（如果有，复制错误信息）

### 步骤 1.4：测试Interview服务状态API

**目的：**直接测试后端API确认服务可用性

**操作：**

#### 方法 A：使用浏览器
1. **打开浏览器**，访问以下URL：
   ```
   https://smartsuccess-ai.onrender.com/api/interview/status
   ```

2. **期望返回的JSON：**
   ```json
   {
     "available": true,
     "services": {
       "rag": true,
       "interview": true,
       "feedback": true
     }
   }
   ```

3. **实际返回结果：**
   ```json
   [在这里粘贴实际返回的JSON]
   ```

#### 方法 B：使用命令行（curl）
```bash
curl https://smartsuccess-ai.onrender.com/api/interview/status
```

**记录结果：**
- [ ] API返回了正确的JSON？
- [ ] `available` 字段是 `true`？
- [ ] `rag`, `interview`, `feedback` 都是 `true`？
- [ ] 如果返回错误，错误信息是什么？

### 步骤 1.5：检查服务依赖

**目的：**确认RAG服务需要的依赖是否安装

**操作：**
1. 在Render服务详情页面，点击 **"Logs"** 标签
2. 查找构建日志（Build Logs）部分
3. **查找关键信息：**

**✅ 应该看到：**
```
Successfully installed groq-...
Successfully installed numpy-...
```

**检查点：**
- [ ] `groq` 包是否成功安装？
- [ ] `numpy` 包是否成功安装？
- [ ] 是否有任何包安装失败？

### 步骤 1.6：测试完整Interview API流程

**目的：**确认Interview服务可以正常启动会话

**操作：**

#### 使用命令行测试（curl）：
```bash
# 1. 启动面试会话
curl -X POST https://smartsuccess-ai.onrender.com/api/interview/start \
  -F "user_id=demo-user-test"
```

**期望返回：**
```json
{
  "session_id": "...",
  "message": "Welcome to your Mock Interview!...",
  "section": "greeting"
}
```

**记录结果：**
- [ ] 成功返回了 `session_id`？
- [ ] 成功返回了 `message`？
- [ ] 如果有错误，错误信息是什么？

---

## 🔐 第二部分：验证生产环境环境变量配置

### 步骤 2.1：访问Render环境变量设置

**操作：**
1. 在Render Dashboard中，进入 `resume-matcher-backend` 服务
2. 点击左侧菜单的 **"Environment"** 选项
3. 查看当前配置的环境变量列表

### 步骤 2.2：检查必需的环境变量

**参考清单：**对照下面的清单，确认每个变量都已设置

#### ✅ 必需的环境变量：

| 变量名 | 说明 | 是否设置 | 备注 |
|--------|------|---------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | ⬜ | 用于主要AI服务 |
| `XAI_API_KEY` | xAI (Grok) API密钥 | ⬜ | 备用AI服务 |
| `GROQ_API_KEY` | Groq API密钥 | ⬜ | **Interview服务必需** |
| `STRIPE_SECRET_KEY` | Stripe支付密钥 | ⬜ | 用户订阅管理 |
| `STRIPE_WEBHOOK_SECRET` | Stripe Webhook密钥 | ⬜ | 支付回调 |
| `ALLOWED_ORIGINS` | 允许的CORS来源 | ⬜ | 前端域名 |
| `PYTHON_VERSION` | Python版本 | ⬜ | 应该是 3.11.0 |

**记录结果：**
- [ ] `OPENAI_API_KEY` 已设置？
- [ ] `XAI_API_KEY` 已设置？
- [ ] `GROQ_API_KEY` 已设置？（**特别重要 - Interview服务需要**）
- [ ] `STRIPE_SECRET_KEY` 已设置？
- [ ] `STRIPE_WEBHOOK_SECRET` 已设置？
- [ ] `ALLOWED_ORIGINS` 已设置？
- [ ] `PYTHON_VERSION` 已设置？

### 步骤 2.3：验证ALLOWED_ORIGINS配置

**目的：**确认前端域名已正确配置

**操作：**
1. 点击 `ALLOWED_ORIGINS` 变量查看其值
2. **应该包含以下域名：**
   ```
   https://smart-success-ai.vercel.app,https://matchwise-ai.vercel.app,http://localhost:3000
   ```

**检查点：**
- [ ] 包含 `https://smart-success-ai.vercel.app`？
- [ ] 包含 `https://matchwise-ai.vercel.app`？
- [ ] 包含 `http://localhost:3000`（用于本地开发）？

**记录实际值：**
```
[在这里粘贴ALLOWED_ORIGINS的实际值]
```

### 步骤 2.4：检查Firebase服务账户密钥

**目的：**确认Firebase配置正确

**操作：**
1. 在Render服务详情页面，点击 **"Settings"** 标签
2. 滚动到 **"Secret Files"** 部分
3. **检查：**
   - [ ] 是否存在 `serviceAccountKey.json` 文件？
   - [ ] 文件大小是否正确（通常 > 0 KB）？

**如果没有配置：**
- 需要从Firebase控制台下载服务账户密钥
- 在Render的Secret Files部分上传该文件

### 步骤 2.5：验证环境变量格式

**常见错误检查：**

#### ❌ 错误示例：
- `Groq_API_Key` (错误的大小写)
- `OPENAI_API_KEY=` (空值)
- 包含多余的空格或引号

#### ✅ 正确格式：
- 变量名全部大写
- 变量值不包含引号（除非是JSON字符串）
- 没有多余的空格

**检查点：**
- [ ] 所有变量名都是全大写？
- [ ] 变量值没有多余的空格？
- [ ] 变量值没有不必要的引号？

### 步骤 2.6：测试API密钥有效性

**目的：**确认API密钥是有效的，不是过期或错误的

**操作：**

#### 测试OPENAI_API_KEY：
在Render Logs中查看是否有以下错误：
```
OPENAI_API_KEY not set in environment variables
OpenAI API request failed: ...
```

#### 测试GROQ_API_KEY（Interview服务必需）：
如果Interview服务初始化失败，通常是因为缺少GROQ_API_KEY。

**检查点：**
- [ ] 日志中是否有API密钥相关的错误？
- [ ] 如果有错误，具体错误信息是什么？

---

## 🖼️ 第三部分：验证MatchWise AI iframe嵌入权限设置

### 步骤 3.1：确认MatchWise AI部署URL

**操作：**
1. **确认MatchWise AI的生产环境URL：**
   - 根据代码，应该是：`https://matchwise-ai.vercel.app`
   - 如果不同，记录实际URL：`[填写实际URL]`

### 步骤 3.2：检查SmartSuccess.AI中的iframe配置

**文件位置：** `resume-matcher-frontend/src/app/page.tsx`

**操作：**
1. 打开文件：`resume-matcher-frontend/src/app/page.tsx`
2. **查找以下代码行（约第34行）：**
   ```typescript
   const MATCHWISE_URL = 'https://matchwise-ai.vercel.app';
   ```
3. **确认：**
   - [ ] URL是否正确？
   - [ ] URL是否与MatchWise AI的实际部署URL一致？

**记录当前值：**
```
MATCHWISE_URL = [填写当前值]
```

### 步骤 3.3：检查MatchWise AI的next.config.ts配置

**⚠️ 重要：**这一步需要在MatchWise AI项目中完成

**操作：**
1. **访问MatchWise AI项目**（如果可能）
2. **检查 `next.config.ts` 文件**
3. **应该包含以下配置：**

```typescript
const nextConfig: NextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' https://smart-success-ai.vercel.app https://smartsuccess-ai.vercel.app;",
          },
          {
            key: 'X-Frame-Options',
            value: 'ALLOW-FROM https://smart-success-ai.vercel.app',
          },
        ],
      },
    ];
  },
};
```

**检查点：**
- [ ] MatchWise AI的`next.config.ts`是否配置了`frame-ancestors`？
- [ ] 是否包含了`https://smart-success-ai.vercel.app`域名？
- [ ] 如果无法访问MatchWise AI代码，需要联系MatchWise AI团队确认配置

### 步骤 3.4：测试iframe加载

**操作：**

#### 方法 A：在浏览器中测试
1. **访问SmartSuccess.AI主页：**
   ```
   https://smart-success-ai.vercel.app
   ```

2. **打开浏览器开发者工具：**
   - Chrome/Edge: `F12` 或 `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: `F12` 或 `Ctrl+Shift+I`

3. **检查Console标签：**
   - ✅ 应该看到：`✅ MatchWise AI iframe loaded successfully`
   - ❌ 如果看到错误：
     ```
     ❌ MatchWise AI iframe failed to load
     MatchWise AI Integration Pending
     ```

4. **检查Network标签：**
   - 查找对 `matchwise-ai.vercel.app` 的请求
   - 检查响应状态码：
     - ✅ `200` = 成功
     - ❌ `403`, `404`, `X-Frame-Options Deny` = 失败

**记录结果：**
- [ ] iframe成功加载？
- [ ] Console中是否有错误信息？
- [ ] Network请求状态码是什么？

### 步骤 3.5：检查iframe错误处理

**目的：**确认SmartSuccess.AI正确处理iframe加载失败的情况

**操作：**
1. 在SmartSuccess.AI主页，如果iframe加载失败
2. **应该看到错误提示：**
   ```
   MatchWise AI Integration Pending
   MatchWise AI needs to be configured to allow iframe embedding...
   ```

**检查点：**
- [ ] 错误提示是否清晰？
- [ ] 是否有"在新标签页打开"的链接？

### 步骤 3.6：测试跨域消息通信

**目的：**确认postMessage通信正常工作

**操作：**
1. **在SmartSuccess.AI主页**，打开浏览器开发者工具
2. **切换到Console标签**
3. **查找以下消息（开发环境）：**
   ```
   📨 Message received from MatchWise AI: loginStatus
   ✅ Login status updated: Guest
   ```

4. **测试登录功能：**
   - 点击左侧菜单栏的 "Guest User Sign In" 按钮
   - 应该触发MatchWise AI的登录弹窗

**检查点：**
- [ ] Console中能看到消息通信日志？
- [ ] 点击登录按钮能触发弹窗？
- [ ] 如果有错误，具体错误信息是什么？

### 步骤 3.7：检查CORS配置

**目的：**确认MatchWise AI允许SmartSuccess.AI的请求

**操作：**
1. **访问MatchWise AI主页**（如果可以）
2. **打开浏览器开发者工具**
3. **检查Network标签中的请求**
4. **查看响应头（Response Headers）：**

**应该包含：**
```
Access-Control-Allow-Origin: https://smart-success-ai.vercel.app
Content-Security-Policy: frame-ancestors 'self' https://smart-success-ai.vercel.app
X-Frame-Options: ALLOW-FROM https://smart-success-ai.vercel.app
```

**检查点：**
- [ ] 响应头中包含正确的CORS配置？
- [ ] `frame-ancestors`包含SmartSuccess.AI域名？
- [ ] 如果没有这些头部，需要配置MatchWise AI的服务器

---

## 📋 验证结果汇总

### ✅ 第一部分：Render后端服务状态

**服务状态：** `[填写：Live / Failed / Building]`

**Interview服务状态：**
```json
[在这里粘贴 /api/interview/status 的返回结果]
```

**发现的问题：**
- [ ] 无问题
- [ ] 服务未运行
- [ ] 服务初始化失败
- [ ] API测试失败
- [ ] 其他问题：`[描述]`

---

### ✅ 第二部分：环境变量配置

**已设置的环境变量：**
- [ ] `OPENAI_API_KEY` ✅ / ❌
- [ ] `XAI_API_KEY` ✅ / ❌
- [ ] `GROQ_API_KEY` ✅ / ❌ ⚠️ **特别重要**
- [ ] `STRIPE_SECRET_KEY` ✅ / ❌
- [ ] `STRIPE_WEBHOOK_SECRET` ✅ / ❌
- [ ] `ALLOWED_ORIGINS` ✅ / ❌

**ALLOWED_ORIGINS实际值：**
```
[填写实际值]
```

**发现的问题：**
- [ ] 无问题
- [ ] 缺少必需的环境变量
- [ ] 环境变量格式错误
- [ ] API密钥无效
- [ ] 其他问题：`[描述]`

---

### ✅ 第三部分：MatchWise AI iframe权限

**MatchWise AI URL：** `[填写URL]`

**iframe加载状态：**
- [ ] ✅ 成功加载
- [ ] ❌ 加载失败

**Console错误信息：**
```
[如果有错误，在这里粘贴]
```

**发现的问题：**
- [ ] 无问题
- [ ] iframe无法加载
- [ ] 缺少CORS配置
- [ ] 缺少Content-Security-Policy
- [ ] postMessage通信失败
- [ ] 其他问题：`[描述]`

---

## 🛠️ 常见问题解决方案

### 问题 1：Interview服务初始化失败

**可能原因：**
- 缺少 `GROQ_API_KEY` 环境变量
- Groq API密钥无效
- 依赖包安装失败

**解决方案：**
1. 在Render Environment中检查 `GROQ_API_KEY` 是否设置
2. 确认API密钥有效（在Groq控制台验证）
3. 重新部署服务

### 问题 2：iframe无法加载

**可能原因：**
- MatchWise AI未配置 `frame-ancestors`
- X-Frame-Options阻止嵌入
- CORS配置不正确

**解决方案：**
1. 联系MatchWise AI团队，确认 `next.config.ts` 配置
2. 添加SmartSuccess.AI域名到 `frame-ancestors`
3. 重新部署MatchWise AI

### 问题 3：环境变量不生效

**可能原因：**
- 环境变量格式错误
- 服务未重新部署

**解决方案：**
1. 检查变量名大小写（必须全大写）
2. 确认变量值没有多余空格
3. 在Render中手动触发重新部署

---

## ✅ 完成验证检查

完成所有步骤后，请确认：

- [ ] 第一部分：Render后端服务状态 ✅
- [ ] 第二部分：环境变量配置 ✅
- [ ] 第三部分：MatchWise AI iframe权限 ✅

**如有问题，请记录具体错误信息，方便后续排查。**

---

**文档版本：** 1.0  
**最后更新：** 2025-01-12  
**维护者：** SmartSuccess.AI 开发团队
