# CORS and 422 Error Analysis & Fix Guide

## 🔴 错误分析

### 错误 1: CORS Policy Error (主要问题)

**错误信息:**
```
Access to fetch at 'https://your-port-8000-url.cluster3.service-inference.ai/health' 
from origin 'https://smart-success-ai.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**根本原因:**
1. **占位符 URL**: Vercel 环境变量 `NEXT_PUBLIC_GPU_BACKEND_URL` 被设置为占位符值 `your-port-8000-url.cluster3.service-inference.ai`，而不是实际的 GPU 后端 URL
2. **404 错误**: 这个占位符 URL 返回 404，说明它不是一个有效的端点

**问题位置:**
- Vercel Environment Variables: `NEXT_PUBLIC_GPU_BACKEND_URL`
- 当前值: `your-port-8000-url.cluster3.service-inference.ai` ❌
- 应该是: 你的实际 GPU 后端 URL (例如: `https://xxxxx-8000-xxxxx.cluster3.service-inference.ai`) ✅

---

### 错误 2: 422 Unprocessable Content (次要问题)

**错误信息:**
```
POST https://smartsuccess-ai.onrender.com/api/interview/start 422 (Unprocessable Content)
❌ API Error: Failed to start interview: 422
```

**可能原因:**
1. **请求格式问题**: Render 后端期望的请求格式与前端发送的不匹配
2. **缺少必需字段**: 请求中可能缺少某些必需的数据字段
3. **数据验证失败**: 后端验证逻辑拒绝了请求

---

## ✅ 修复方案

### 修复 1: 更新 Vercel 环境变量 (必须)

**步骤:**

1. **找到你的实际 GPU 后端 URL**
   - 登录 Inference.ai 控制台
   - 进入你的 GPU 服务
   - 在 "HTTP Ports" 部分找到端口 8000 的 URL
   - 格式应该类似: `https://xxxxx-8000-xxxxx.cluster3.service-inference.ai`

2. **在 Vercel 中更新环境变量**
   - 访问: https://vercel.com/dashboard
   - 选择项目: `smart-success-ai` 或相关项目
   - 进入 **Settings** → **Environment Variables**
   - 找到 `NEXT_PUBLIC_GPU_BACKEND_URL`
   - 更新为你的实际 GPU 后端 URL
   - 确保选择正确的环境 (Production, Preview, Development)
   - 点击 **Save**

3. **重新部署**
   - 在 Vercel Dashboard 中
   - 进入 **Deployments**
   - 点击最新部署的 **"..."** 菜单
   - 选择 **"Redeploy"**
   - 或者推送一个新的 commit 触发自动部署

---

### 修复 2: 验证 GPU 后端 CORS 配置 (检查)

**GPU 后端 CORS 配置已正确设置:**
- ✅ 已包含 `https://smart-success-ai.vercel.app` 在允许的来源列表中
- ✅ CORS 中间件已正确配置

**如果仍有 CORS 问题，检查:**
1. 确认 GPU 后端服务正在运行
2. 测试健康检查端点:
   ```bash
   curl https://your-actual-gpu-backend-url/health
   ```
3. 检查响应头是否包含:
   ```
   Access-Control-Allow-Origin: https://smart-success-ai.vercel.app
   ```

---

### 修复 3: 解决 422 错误 (调查)

**步骤:**

1. **检查 Render 后端日志**
   - 登录 Render Dashboard
   - 查看后端服务的日志
   - 查找 422 错误的详细信息

2. **检查请求格式**
   - 查看前端代码中 `/api/interview/start` 的请求格式
   - 对比 Render 后端期望的格式

3. **常见 422 原因:**
   - 缺少 `user_id` 字段
   - 请求体格式错误 (应该是 FormData 或 JSON)
   - 字段验证失败

**临时解决方案:**
- 如果 GPU 后端 URL 正确配置后，系统应该自动使用 GPU 后端
- 422 错误可能只在 Render 后端出现，GPU 后端可能工作正常

---

## 🔍 验证步骤

### 1. 验证环境变量已更新

在浏览器控制台检查:
```javascript
console.log(process.env.NEXT_PUBLIC_GPU_BACKEND_URL)
// 应该显示实际的 URL，而不是占位符
```

### 2. 测试 GPU 后端连接

在浏览器控制台:
```javascript
fetch('https://your-actual-gpu-backend-url/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

### 3. 检查网络请求

在浏览器 DevTools → Network 标签:
- 查找对 GPU 后端的请求
- 检查请求 URL 是否正确
- 检查响应头是否包含 CORS 头

---

## 📝 快速修复清单

- [ ] 1. 在 Inference.ai 找到实际的 GPU 后端 URL (端口 8000)
- [ ] 2. 在 Vercel 更新 `NEXT_PUBLIC_GPU_BACKEND_URL` 环境变量
- [ ] 3. 重新部署 Vercel 应用
- [ ] 4. 验证 GPU 后端健康检查端点可访问
- [ ] 5. 测试 "Start Interview" 按钮
- [ ] 6. 如果仍有 422 错误，检查 Render 后端日志

---

## 🚨 重要提示

1. **占位符 URL 必须替换**: `your-port-8000-url.cluster3.service-inference.ai` 不是有效 URL
2. **环境变量更新后需要重新部署**: Vercel 不会自动重新构建，需要手动触发
3. **GPU 后端必须运行**: 确保 GPU 后端服务在 Inference.ai 上正在运行
4. **CORS 配置已正确**: GPU 后端已配置允许来自 Vercel 的请求

---

## 🔗 相关文件

- GPU 后端 CORS 配置: `gpu_backend/main.py` (第 150-156 行)
- 前端请求路由: `resume-matcher-frontend/src/app/utils/requestRouter.ts` (第 10 行)
- GPU 后端设置: `gpu_backend/config/settings.py` (第 28-33 行)
