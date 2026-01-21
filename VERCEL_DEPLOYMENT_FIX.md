# Vercel 部署问题修复

## 🔍 问题分析

从部署日志看到的问题：
1. **包数量异常**: 移除了 300 个包，只安装了 110 个包
2. **根目录错误**: Vercel 在根目录运行构建，但前端代码在 `resume-matcher-frontend/` 子目录
3. **构建失败**: 因为找不到正确的 package.json 和依赖

## ✅ 已修复

### 更新了 `vercel.json`

**修复前**:
```json
{
  "buildCommand": "npm install && npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs"
}
```

**修复后**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs",
  "rootDirectory": "resume-matcher-frontend"
}
```

### 关键更改

1. **添加 `rootDirectory`**: 指定 `resume-matcher-frontend` 为根目录
2. **简化命令**: 因为设置了 rootDirectory，Vercel 会自动在正确目录运行命令
3. **输出目录**: 使用相对路径 `.next`（相对于 rootDirectory）

## 🔧 在 Vercel 控制台验证

### 方法 1: 通过 vercel.json（推荐）

已更新的 `vercel.json` 会自动配置，无需手动设置。

### 方法 2: 在 Vercel 控制台手动设置

如果 vercel.json 不生效，在 Vercel 项目设置中：

1. **进入项目设置**
   - 访问: https://vercel.com/emma-wangs-projects/resume-matcher-frontend/settings/general

2. **设置 Root Directory**
   - 找到 "Root Directory" 设置
   - 设置为: `resume-matcher-frontend`
   - 保存

3. **重新部署**
   - 在 Deployments 页面点击 "Redeploy"

## 📋 验证清单

部署前检查：
- [x] `vercel.json` 已更新，包含 `rootDirectory`
- [ ] Vercel 项目设置中的 Root Directory 正确
- [ ] 环境变量已配置（NEXT_PUBLIC_BACKEND_URL, NEXT_PUBLIC_GPU_BACKEND_URL）
- [ ] `resume-matcher-frontend/package.json` 存在
- [ ] `resume-matcher-frontend/next.config.ts` 存在

## 🚀 重新部署

1. **提交更改**:
   ```bash
   git add vercel.json
   git commit -m "Fix Vercel deployment: set rootDirectory to resume-matcher-frontend"
   git push origin main
   ```

2. **Vercel 会自动重新部署**

3. **检查部署日志**:
   - 应该看到在 `resume-matcher-frontend` 目录运行构建
   - 应该安装正确的依赖包数量（约 410 个包）

## ⚠️ 其他可能的问题

### 如果仍然失败，检查：

1. **依赖问题**:
   ```bash
   cd resume-matcher-frontend
   npm audit fix
   ```

2. **Next.js 版本兼容性**:
   - 当前版本: 15.5.7
   - 确保所有依赖兼容

3. **环境变量**:
   - 确保 `NEXT_PUBLIC_BACKEND_URL` 已设置
   - 确保 `NEXT_PUBLIC_GPU_BACKEND_URL` 已设置（如果使用 GPU 后端）

---
**修复时间**: 2026-01-21
**状态**: ✅ vercel.json 已更新
