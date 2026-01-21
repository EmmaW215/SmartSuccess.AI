# Render 自动部署检查指南

## 🔍 如何检查 Render 是否配置了自动部署

### 方法 1: 在 Render 控制台中检查（推荐）

#### 步骤 1: 访问 Render 服务页面
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 找到并点击你的后端服务：`resume-matcher-backend` 或 `smartsuccess-ai`

#### 步骤 2: 检查服务设置
在服务页面的左侧导航栏中，点击 **"Settings"** 标签

#### 步骤 3: 查看 "Build & Deploy" 部分
在 Settings 页面中，找到 **"Build & Deploy"** 部分，检查以下内容：

**✅ 自动部署已配置的标志：**
- **"Auto-Deploy"** 开关显示为 **"Yes"** 或 **"On"**
- **"Repository"** 显示已连接的 GitHub 仓库：`EmmaW215/SmartSuccess.AI`
- **"Branch"** 显示部署分支：通常是 `main` 或 `master`
- **"Root Directory"** 显示：`resume-matcher-backend`

**❌ 自动部署未配置的标志：**
- **"Auto-Deploy"** 显示为 **"No"** 或 **"Off"**
- **"Repository"** 显示 "Not connected" 或为空
- 或者显示 "Manual deploy only"

#### 步骤 4: 检查部署历史
1. 在服务页面，点击 **"Events"** 或 **"Logs"** 标签
2. 查看最近的部署记录：
   - ✅ **自动部署**：显示 "Deployed from GitHub" 或 "Auto deploy triggered"
   - ❌ **手动部署**：显示 "Manual deploy" 或 "Deployed via dashboard"

### 方法 2: 验证 GitHub 连接

#### 在 Render 控制台中：
1. 进入服务 **Settings** 页面
2. 找到 **"Repository"** 部分
3. 检查：
   - ✅ 如果显示 GitHub 仓库链接：已连接
   - ❌ 如果显示 "Connect repository" 按钮：未连接

### 方法 3: 检查最近的部署触发

#### 在 Render 控制台中：
1. 进入 **"Events"** 或 **"Deployments"** 标签
2. 查看最近的部署记录：
   - **自动部署** 通常显示：
     - "Auto deploy triggered by push to main"
     - "Deployed from GitHub commit: [commit hash]"
     - 或类似消息
   - **手动部署** 显示：
     - "Manual deploy"
     - 或 "Deployed via dashboard"

---

## ⚙️ 如何配置自动部署

如果自动部署未配置，请按以下步骤设置：

### 步骤 1: 连接 GitHub 仓库

1. 在 Render 服务页面的 **Settings** 中
2. 找到 **"Repository"** 部分
3. 点击 **"Connect repository"** 或 **"Change repository"**
4. 选择 GitHub 账户
5. 选择仓库：`EmmaW215/SmartSuccess.AI`
6. 选择分支：`main`
7. 点击 **"Connect"**

### 步骤 2: 配置自动部署设置

1. 在 **Settings** 页面的 **"Build & Deploy"** 部分
2. 找到 **"Auto-Deploy"** 选项
3. 将其设置为 **"Yes"** 或打开开关
4. 确认以下设置：
   - **Branch**: `main`
   - **Root Directory**: `resume-matcher-backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 步骤 3: 保存设置

1. 滚动到页面底部
2. 点击 **"Save Changes"**
3. Render 会自动触发一次部署来测试配置

---

## ✅ 验证自动部署是否工作

### 测试步骤：

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "test: Verify auto-deploy"
   git push origin main
   ```

2. **立即检查 Render Dashboard**
   - 进入服务的 **"Events"** 标签
   - 应该在 1-2 分钟内看到新的部署开始
   - 状态会显示 "Building..." 或 "Deploying..."

3. **观察部署日志**
   - 在 **"Logs"** 标签中
   - 应该看到构建和部署过程
   - 最后显示 "Your service is live 🎉"

4. **检查部署信息**
   - 在 **"Events"** 中查看部署记录
   - 应该显示触发方式为 "Auto deploy" 或 "Deployed from GitHub"

---

## 📋 Render 自动部署检查清单

使用此清单确认配置是否正确：

- [ ] ✅ GitHub 仓库已连接
- [ ] ✅ 部署分支设置为 `main`
- [ ] ✅ Root Directory 设置为 `resume-matcher-backend`
- [ ] ✅ Auto-Deploy 开关已打开（Yes/On）
- [ ] ✅ Build Command 正确：`pip install -r requirements.txt`
- [ ] ✅ Start Command 正确：`uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] ✅ 环境变量已配置（OPENAI_API_KEY, XAI_API_KEY 等）
- [ ] ✅ 最近的部署记录显示 "Auto deploy" 而不是 "Manual deploy"

---

## 🔧 如果自动部署未工作

### 可能的原因和解决方法：

1. **GitHub 连接断开**
   - 重新连接仓库（Settings → Repository → Connect repository）

2. **Auto-Deploy 开关关闭**
   - 打开 Auto-Deploy 开关（Settings → Build & Deploy → Auto-Deploy: Yes）

3. **分支不匹配**
   - 确认分支设置为 `main`（Settings → Branch）

4. **Webhook 问题**
   - Render 会自动设置 GitHub webhook
   - 如果失效，可以尝试重新连接仓库

5. **Render 服务配置错误**
   - 检查 Root Directory 是否正确
   - 确认 Build Command 和 Start Command 正确

---

## 📝 当前项目的 Render 配置

根据 `render.yaml` 文件，当前配置应该是：

```yaml
services:
  - type: web
    name: resume-matcher-backend
    env: python
    rootDir: resume-matcher-backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**注意**: `render.yaml` 文件用于通过 Render CLI 部署，但如果在 Render Dashboard 中手动创建服务，需要确保这些设置在控制台中正确配置。

---

## 🎯 快速检查步骤总结

1. 访问 Render Dashboard
2. 打开后端服务页面
3. 点击 **Settings** 标签
4. 检查 **Build & Deploy** → **Auto-Deploy**: 应该是 **"Yes"**
5. 检查 **Repository**: 应该显示 GitHub 仓库
6. 点击 **Events** 标签查看最近部署：应该看到 "Auto deploy" 记录

---

**更新日期**: 2025-01-17
