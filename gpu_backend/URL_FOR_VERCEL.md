# Vercel 环境变量 URL 配置

## ❌ 不要使用这个 URL

```
jupyter-labs-8888-1769018572503320273.cluster3.service-inference.ai?token=28g4I0zfE5913vjG
```

**原因**:
- 这是 JupyterLab（端口 8888），不是 GPU 后端
- GPU 后端运行在端口 8000
- 包含 token 参数，API 不需要

## ✅ 正确的 URL（基于你的 JupyterLab URL）

根据你的 JupyterLab URL 格式，端口 8000 的 URL 可能是以下之一：

### 选项 1（最可能）:
```
https://deployment-1066-1587-1769018572503320273-8000.cluster3.service-inference.ai
```

### 选项 2:
```
https://1769018572503320273-8000.cluster3.service-inference.ai
```

### 选项 3:
```
https://gpu-backend-8000-1769018572503320273.cluster3.service-inference.ai
```

## 🔍 如何确认正确的 URL

### 方法 1: 在 Inference.ai 控制台查找（最准确）

1. 登录 Inference.ai
2. 进入你的项目 Overview 页面
3. 查找 "HTTP Ports" 或 "Exposed Ports" 部分
4. 找到端口 **:8000** 的条目
5. 复制对应的 HTTPS URL

### 方法 2: 测试候选 URL

在终端中测试每个候选 URL：

```bash
# 测试选项 1
curl https://deployment-1066-1587-1769018572503320273-8000.cluster3.service-inference.ai/health

# 测试选项 2
curl https://1769018572503320273-8000.cluster3.service-inference.ai/health

# 测试选项 3
curl https://gpu-backend-8000-1769018572503320273.cluster3.service-inference.ai/health
```

**成功的响应**:
```json
{
    "status": "healthy",
    "gpu_available": true,
    "gpu_memory_free": 44.95,
    "gpu_memory_total": 47.99,
    "models_loaded": {
        "embedding": true,
        "prerag": true
    },
    "version": "1.0.0"
}
```

## 📝 在 Vercel 中配置

### 步骤

1. **进入 Vercel 项目设置**
   - 打开你的 Vercel 项目
   - 点击 "Settings" → "Environment Variables"

2. **添加环境变量**
   - **Key**: `NEXT_PUBLIC_GPU_BACKEND_URL`
   - **Value**: `https://deployment-1066-1587-1769018572503320273-8000.cluster3.service-inference.ai`
     （使用你测试成功的 URL）
   - **Environment**: 选择所有环境（Production, Preview, Development）

3. **保存并重新部署**
   - 点击 "Save"
   - Vercel 会自动触发重新部署

## ✅ 验证配置

### 1. 测试 URL（在浏览器或终端）

```bash
curl https://your-gpu-backend-url/health
```

应该返回健康状态 JSON。

### 2. 在前端验证

部署后，在前端代码中测试：

```javascript
const gpuBackendUrl = process.env.NEXT_PUBLIC_GPU_BACKEND_URL;
console.log('GPU Backend URL:', gpuBackendUrl);

fetch(`${gpuBackendUrl}/health`)
  .then(res => res.json())
  .then(data => {
    console.log('GPU Backend Status:', data);
    if (data.status === 'healthy') {
      console.log('✅ Connection successful!');
    }
  })
  .catch(err => {
    console.error('❌ Connection failed:', err);
  });
```

## ⚠️ 重要提示

1. **使用 HTTPS**: 生产环境必须使用 HTTPS
2. **端口 8000**: 确保是端口 8000，不是 8888
3. **无 token**: 不要包含 `?token=...` 参数
4. **无尾部斜杠**: URL 末尾不要有 `/`
5. **测试连接**: 配置后务必测试 URL 是否可访问

## 🔧 如果找不到端口 8000 的 URL

### 可能的原因

1. **端口未暴露**: Inference.ai 可能没有自动暴露端口 8000
2. **需要配置**: 可能需要在 Inference.ai 控制台手动配置端口映射

### 解决方案

1. **检查 Inference.ai 服务配置**
   - 查看是否有端口映射/端口转发设置
   - 确认端口 8000 是否已配置为 HTTP 端口

2. **联系 Inference.ai 支持**
   - 请求暴露端口 8000 的公共 HTTPS URL
   - 提供你的服务 ID: `1769018572503320273`

3. **使用 Cloudflare Tunnel（如果可用）**
   - 如果 Inference.ai 支持，可以设置 Cloudflare Tunnel

## 📋 快速检查清单

- [ ] 在 Inference.ai 控制台找到端口 8000 的 URL
- [ ] 测试 URL 可以访问 `/health` 端点
- [ ] URL 格式正确（HTTPS，端口 8000，无 token）
- [ ] 在 Vercel 中设置 `NEXT_PUBLIC_GPU_BACKEND_URL`
- [ ] 选择所有环境（Production, Preview, Development）
- [ ] 保存并重新部署
- [ ] 验证前端可以连接到 GPU 后端

---
**当前状态**: GPU 后端正在端口 8000 运行 ✅
**下一步**: 在 Inference.ai 控制台找到端口 8000 的公共 URL
