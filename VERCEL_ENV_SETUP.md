# Vercel 环境变量配置指南

## 📋 必需的环境变量

### `NEXT_PUBLIC_BACKEND_URL`
- **用途**: 指定后端 API 服务器地址
- **值**: `https://smartsuccess-ai.onrender.com`
- **环境**: Production, Preview, Development（全选）
- **说明**: 这是 SmartSuccess.AI 项目的统一后端 URL，所有前端页面都使用此变量

## 🔧 在 Vercel 中配置步骤

1. 进入 Vercel 项目设置
   - 访问: https://vercel.com/emma-wangs-projects/resume-matcher-frontend/settings/environment-variables

2. 添加环境变量
   - 点击 "Add Environment Variable" 按钮
   - 变量名: `NEXT_PUBLIC_BACKEND_URL`
   - 值: `https://smartsuccess-ai.onrender.com`
   - 选择环境: 勾选 "Production", "Preview", "Development"

3. 删除不需要的变量（如果存在）
   - `KV_URL`
   - `KV_REST_API_READ_ONLY_TOKEN`
   - `REDIS_URL`
   - `KV_REST_API_TOKEN`
   - `KV_REST_API_URL`
   
   这些是 KV/Redis 相关变量，本项目不使用。

4. 保存并重新部署
   - 保存环境变量后，Vercel 会自动触发新的部署
   - 或者手动在 Deployments 页面点击 "Redeploy"

## ✅ 验证配置

部署后，检查以下页面是否正常工作：
- 主页 (Home): 嵌入 MatchWise AI iframe
- Mock Interview (`/interview`): 使用 `${BACKEND_URL}/api/interview/*`
- My Dashboard (`/dashboard`): 使用 `${BACKEND_URL}/api/interview/analytics/*`
- Visitor Counter: 使用 `${BACKEND_URL}/api/visitor/*`

## 📝 代码中的使用

所有前端文件都使用统一的后端 URL：

```typescript
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://smartsuccess-ai.onrender.com";
```

**使用此变量的文件**:
- `resume-matcher-frontend/src/app/interview/page.tsx`
- `resume-matcher-frontend/src/app/dashboard/page.tsx`
- `resume-matcher-frontend/src/app/components/SimpleVisitorCounter.txt`

## 🔄 更新日期
2025-01-12
