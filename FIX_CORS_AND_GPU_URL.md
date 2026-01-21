# Fix CORS and GPU Backend URL Configuration

## ✅ 已完成的修复

### 1. GPU 后端 CORS 配置已更新

**文件**: `gpu_backend/config/settings.py`

已添加以下允许的来源：
- ✅ `https://smart-success-ai.vercel.app`
- ✅ `https://smartsuccess-ai.vercel.app` (新增)
- ✅ `https://matchwise-ai.vercel.app`
- ✅ `http://localhost:3000`
- ✅ `http://localhost:3001`
- ✅ `http://localhost:8000` (新增)

### 2. 前端代码已配置

**文件**: `resume-matcher-frontend/src/app/utils/requestRouter.ts`

前端代码会从环境变量读取 GPU 后端 URL：
```typescript
const GPU_BACKEND_URL = process.env.NEXT_PUBLIC_GPU_BACKEND_URL || 'https://gpu.smartsuccess.ai';
```

---

## 🔧 需要在 Vercel 中配置

### 步骤 1: 设置环境变量

1. **访问 Vercel Dashboard**
   - https://vercel.com/dashboard
   - 选择项目: `smart-success-ai`

2. **添加环境变量**
   - Settings → Environment Variables
   - **Key**: `NEXT_PUBLIC_GPU_BACKEND_URL`
   - **Value**: `https://your-port-8000-url.cluster3.service-inference.ai`
   - **Environment**: 选择所有环境 (Production, Preview, Development)
   - 点击 **Save**

3. **重新部署**
   - Deployments → 最新部署 → "..." → **Redeploy**

---

## 🔧 需要在 GPU 后端配置

### 步骤 2: 更新 GPU 后端 .env 文件

在 GPU 后端服务器上，编辑 `.env` 文件：

```bash
# 确保包含以下 CORS 配置
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
```

或者通过环境变量设置：
```bash
export ALLOWED_ORIGINS='["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000"]'
```

### 步骤 3: 重启 GPU 后端服务

更新配置后，重启 GPU 后端服务：

```bash
# 如果使用 systemd
sudo systemctl restart smartsuccess-gpu

# 或者如果使用手动启动
# 停止当前服务
pkill -f "uvicorn main:app"

# 重新启动
cd /path/to/gpu_backend
source venv/bin/activate  # 或 conda activate gpu_backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ✅ 验证修复

### 1. 验证 Vercel 环境变量

部署后，在浏览器控制台：
```javascript
console.log(process.env.NEXT_PUBLIC_GPU_BACKEND_URL)
// 应该显示: https://your-port-8000-url.cluster3.service-inference.ai
```

### 2. 测试 GPU 后端连接

在浏览器控制台测试：
```javascript
fetch('https://your-port-8000-url.cluster3.service-inference.ai/health', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('Status:', response.status);
  console.log('Headers:', [...response.headers.entries()]);
  return response.json();
})
.then(data => console.log('Data:', data))
.catch(error => console.error('Error:', error));
```

**期望结果:**
- ✅ Status: 200
- ✅ Headers 包含: `access-control-allow-origin: https://smart-success-ai.vercel.app`
- ✅ Data: `{"status": "healthy", ...}`

### 3. 测试 "Start Interview" 按钮

1. 访问: https://smart-success-ai.vercel.app/interview
2. 点击 "Start Interview" 按钮
3. 检查浏览器控制台:
   - ✅ 不应该有 CORS 错误
   - ✅ GPU 后端健康检查应该成功
   - ✅ 如果 GPU 可用，应该使用 GPU 后端
   - ✅ 如果 GPU 不可用，应该回退到 Render 后端

---

## 🐛 故障排除

### 如果仍有 CORS 错误

1. **检查 GPU 后端是否运行**
   ```bash
   curl https://your-port-8000-url.cluster3.service-inference.ai/health
   ```

2. **检查响应头**
   ```bash
   curl -I https://your-port-8000-url.cluster3.service-inference.ai/health
   ```
   应该看到: `Access-Control-Allow-Origin: https://smart-success-ai.vercel.app`

3. **检查 GPU 后端日志**
   - 查看 GPU 后端服务器的日志
   - 确认 CORS 中间件已加载
   - 确认 `ALLOWED_ORIGINS` 配置正确

### 如果仍有 422 错误

422 错误来自 Render 后端，与 GPU 后端无关。可能原因：
- 请求格式不匹配
- 缺少必需字段
- 数据验证失败

**临时解决方案**: 如果 GPU 后端配置正确，系统应该优先使用 GPU 后端，避免 422 错误。

---

## 📝 配置检查清单

- [ ] Vercel 环境变量 `NEXT_PUBLIC_GPU_BACKEND_URL` 已设置
- [ ] Vercel 应用已重新部署
- [ ] GPU 后端 `.env` 文件包含正确的 `ALLOWED_ORIGINS`
- [ ] GPU 后端服务已重启
- [ ] GPU 后端健康检查端点可访问
- [ ] 浏览器控制台没有 CORS 错误
- [ ] "Start Interview" 按钮正常工作

---

## 🔗 相关文件

- GPU 后端 CORS 配置: `gpu_backend/config/settings.py` (第 28-35 行)
- GPU 后端 CORS 中间件: `gpu_backend/main.py` (第 150-156 行)
- 前端请求路由: `resume-matcher-frontend/src/app/utils/requestRouter.ts` (第 10 行)
