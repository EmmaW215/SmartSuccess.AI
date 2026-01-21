# Vercel 部署检查清单

## ✅ 已修复的问题

### 问题: 构建在错误的目录运行
- **原因**: Vercel 在根目录运行构建，但前端代码在 `resume-matcher-frontend/` 子目录
- **修复**: 在 `vercel.json` 中添加 `rootDirectory: "resume-matcher-frontend"`

## 📋 部署前检查清单

### 1. Vercel 配置 ✅

- [x] `vercel.json` 已更新，包含 `rootDirectory`
- [ ] 在 Vercel 控制台验证 Root Directory 设置

**验证步骤**:
1. 访问: https://vercel.com/emma-wangs-projects/resume-matcher-frontend/settings/general
2. 检查 "Root Directory" 是否为 `resume-matcher-frontend`
3. 如果不是，手动设置为 `resume-matcher-frontend`

### 2. 环境变量配置

**必需的环境变量**:

- [ ] `NEXT_PUBLIC_BACKEND_URL`
  - 值: `https://smartsuccess-ai.onrender.com`
  - 环境: Production, Preview, Development

- [ ] `NEXT_PUBLIC_GPU_BACKEND_URL` (如果使用 GPU 后端)
  - 值: `https://your-gpu-backend-8000-url.cluster3.service-inference.ai`
  - 环境: Production, Preview, Development

**配置位置**:
- https://vercel.com/emma-wangs-projects/resume-matcher-frontend/settings/environment-variables

### 3. 代码检查

- [x] `resume-matcher-frontend/package.json` 存在
- [x] `resume-matcher-frontend/next.config.ts` 存在
- [x] `resume-matcher-frontend/src/` 目录存在

### 4. 依赖检查

从日志看到有 1 个 high severity vulnerability，建议修复：

```bash
cd resume-matcher-frontend
npm audit fix
```

## 🚀 部署步骤

### 步骤 1: 提交更改

```bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI
git add vercel.json
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

### 步骤 2: 在 Vercel 控制台验证

1. **检查 Root Directory**:
   - Settings → General → Root Directory
   - 应该是: `resume-matcher-frontend`

2. **检查环境变量**:
   - Settings → Environment Variables
   - 确保所有必需变量已设置

3. **触发重新部署**:
   - Deployments → 点击最新部署的 "..." → Redeploy

### 步骤 3: 验证部署

部署成功后检查：
- [ ] 构建日志显示在 `resume-matcher-frontend` 目录运行
- [ ] 安装的包数量正确（约 410 个包）
- [ ] 构建成功完成
- [ ] 网站可以正常访问

## 🔍 故障排除

### 如果构建仍然失败

1. **检查构建日志**:
   - 查看完整的错误信息
   - 确认是否在正确的目录运行

2. **验证 Root Directory**:
   - 在 Vercel 控制台手动设置
   - 确保与 `vercel.json` 一致

3. **检查依赖**:
   - 运行 `npm audit fix` 修复漏洞
   - 确保所有依赖版本兼容

4. **清除构建缓存**:
   - 在 Vercel 部署设置中清除缓存
   - 重新部署

## 📊 预期构建日志

**成功的构建应该显示**:
```
Cloning github.com/EmmaW215/SmartSuccess.AI
Detected Next.js version: 15.5.7
Running "npm install" in resume-matcher-frontend
up to date, audited 410 packages
Running "npm run build"
✓ Compiled successfully
```

**不应该看到**:
- "removed 300 packages" (这表明在错误的目录)
- 找不到 package.json 的错误
- 模块未找到的错误

---
**修复提交**: `4ff99e6` (如果已推送)
**状态**: ✅ vercel.json 已修复，等待推送和重新部署
