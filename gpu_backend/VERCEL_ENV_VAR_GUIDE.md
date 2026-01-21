# Vercel 环境变量配置指南

## ❌ 不要使用的 URL

**错误示例**:
```
jupyter-labs-8888-1769018572503320273.cluster3.service-inference.ai?token=28g4I0zfE5913vjG
```

**为什么错误**:
- 这是 JupyterLab 的 URL（端口 8888）
- GPU 后端运行在端口 8000
- 包含 JupyterLab 的 token，API 不需要
- 不是 GPU 后端服务的 URL

## ✅ 正确的 URL 格式

`NEXT_PUBLIC_GPU_BACKEND_URL` 应该是：

```
https://your-service-8000-xxxxx.cluster3.service-inference.ai
```

**特征**:
- 端口应该是 **8000**（不是 8888）
- 应该是 **HTTPS** 协议
- **不应该**包含 `?token=...` 参数
- 应该是 GPU 后端服务的 URL

## 🔍 如何找到正确的 URL

### 方法 1: 在 Inference.ai 控制台查找（推荐）

1. **登录 Inference.ai 控制台**
   - 访问你的 Inference.ai 项目

2. **进入 Overview 页面**
   - 找到你的服务实例

3. **查找 "HTTP Ports" 部分**
   - 应该会显示所有暴露的端口
   - 查找端口 **:8000** 的条目

4. **复制 URL**
   - 格式类似：`https://your-service-8000-xxxxx.cluster3.service-inference.ai`
   - 或者：`https://xxxxx-8000.cluster3.service-inference.ai`

### 方法 2: 根据 JupyterLab URL 推断

如果你有 JupyterLab URL：
```
jupyter-labs-8888-1769018572503320273.cluster3.service-inference.ai
```

端口 8000 的 URL 可能是：
```
https://your-service-8000-1769018572503320273.cluster3.service-inference.ai
```

或者：
```
https://1769018572503320273-8000.cluster3.service-inference.ai
```

**注意**: 这只是推测，最好在 Inference.ai 控制台确认。

### 方法 3: 测试不同的 URL 格式

尝试以下格式的 URL，测试哪个可以访问：

```bash
# 格式 1
curl https://your-service-8000-1769018572503320273.cluster3.service-inference.ai/health

# 格式 2
curl https://1769018572503320273-8000.cluster3.service-inference.ai/health

# 格式 3
curl https://gpu-backend-8000-1769018572503320273.cluster3.service-inference.ai/health
```

**成功的响应应该是**:
```json
{
    "status": "healthy",
    "gpu_available": true,
    ...
}
```

## 📝 在 Vercel 中配置

### 步骤

1. **登录 Vercel**
   - 进入你的项目设置

2. **进入 Environment Variables**
   - Settings → Environment Variables

3. **添加变量**
   - **Key**: `NEXT_PUBLIC_GPU_BACKEND_URL`
   - **Value**: `https://your-service-8000-xxxxx.cluster3.service-inference.ai`
   - **Environment**: Production, Preview, Development（全选）

4. **保存并重新部署**
   - 保存后，Vercel 会自动重新部署

## ✅ 验证配置

### 1. 测试 URL 可访问性

在浏览器或终端中测试：

```bash
curl https://your-gpu-backend-url/health
```

应该返回：
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

### 2. 在前端代码中验证

在前端代码中，`NEXT_PUBLIC_GPU_BACKEND_URL` 应该可以这样使用：

```typescript
const gpuBackendUrl = process.env.NEXT_PUBLIC_GPU_BACKEND_URL;

// 测试连接
fetch(`${gpuBackendUrl}/health`)
  .then(res => res.json())
  .then(data => console.log('GPU Backend Status:', data));
```

## 🔧 如果找不到端口 8000 的 URL

### 选项 1: 检查端口是否暴露

在 Inference.ai 控制台：
1. 检查服务配置
2. 确认端口 8000 是否已配置为 HTTP 端口
3. 如果没有，需要添加端口映射

### 选项 2: 使用 Cloudflare Tunnel（如果可用）

如果 Inference.ai 支持，可以设置 Cloudflare Tunnel 来暴露端口 8000。

### 选项 3: 联系 Inference.ai 支持

如果无法找到端口 8000 的 URL，联系 Inference.ai 支持团队：
- 请求暴露端口 8000 的 HTTP URL
- 提供你的服务 ID 或实例 ID

## 📋 检查清单

- [ ] 在 Inference.ai 控制台找到端口 8000 的 HTTP URL
- [ ] URL 格式正确（HTTPS，端口 8000，无 token）
- [ ] 测试 URL 可以访问 `/health` 端点
- [ ] 在 Vercel 中设置 `NEXT_PUBLIC_GPU_BACKEND_URL`
- [ ] 重新部署 Vercel 应用
- [ ] 验证前端可以连接到 GPU 后端

## ⚠️ 重要提示

1. **不要使用 JupyterLab URL**: 端口 8888 是 JupyterLab，不是 GPU 后端
2. **确保是 HTTPS**: 生产环境应该使用 HTTPS
3. **不要包含 token**: API 服务不需要 JupyterLab 的 token
4. **测试连接**: 配置后务必测试 URL 是否可访问

---
**当前状态**: GPU 后端正在端口 8000 运行
**下一步**: 在 Inference.ai 控制台找到端口 8000 的公共 URL
