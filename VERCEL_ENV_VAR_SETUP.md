# Vercel Environment Variable Setup Guide

## 🔧 配置 NEXT_PUBLIC_GPU_BACKEND_URL

### 步骤：

1. **访问 Vercel Dashboard**
   - 登录: https://vercel.com/dashboard
   - 选择项目: `smart-success-ai` 或相关项目

2. **进入环境变量设置**
   - 点击项目 → **Settings** → **Environment Variables**

3. **添加/更新环境变量**
   - **Key**: `NEXT_PUBLIC_GPU_BACKEND_URL`
   - **Value**: `https://your-port-8000-url.cluster3.service-inference.ai`
   - **Environment**: 选择所有环境 (Production, Preview, Development)
   - 点击 **Save**

4. **重新部署**
   - 进入 **Deployments** 页面
   - 点击最新部署的 **"..."** 菜单
   - 选择 **"Redeploy"**
   - 或者推送一个新的 commit 触发自动部署

## ✅ 验证配置

部署后，在浏览器控制台检查：
```javascript
console.log(process.env.NEXT_PUBLIC_GPU_BACKEND_URL)
// 应该显示: https://your-port-8000-url.cluster3.service-inference.ai
```

## 🔍 测试连接

在浏览器控制台测试：
```javascript
fetch('https://your-port-8000-url.cluster3.service-inference.ai/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

如果看到 CORS 错误，说明 GPU 后端需要更新 CORS 配置。

## 📝 注意事项

1. **环境变量名称**: 必须以 `NEXT_PUBLIC_` 开头才能在客户端访问
2. **重新部署**: 更新环境变量后必须重新部署才能生效
3. **URL 格式**: 确保 URL 以 `https://` 开头，且没有尾随斜杠
