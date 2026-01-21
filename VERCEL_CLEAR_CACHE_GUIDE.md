# Vercel 清除构建缓存并重新部署指南

## 🎯 方法 1: 通过 Vercel Dashboard (推荐)

### 步骤：

1. **登录 Vercel Dashboard**
   - 访问: https://vercel.com/dashboard
   - 登录你的账户

2. **选择项目**
   - 在项目列表中找到 `matchwise-ai` 或 `smart-success-ai`
   - 点击项目名称进入项目详情页

3. **清除构建缓存**
   - 点击顶部菜单的 **"Deployments"** 标签
   - 找到最新的部署记录
   - 点击部署记录右侧的 **"..."** (三个点菜单)
   - 选择 **"Redeploy"** 或 **"Redeploy with Cache Cleared"**
   - 如果看到 **"Clear Cache and Redeploy"** 选项，选择它

4. **或者使用 Settings 清除缓存**
   - 进入项目 → **Settings** → **General**
   - 滚动到底部找到 **"Clear Build Cache"** 按钮
   - 点击清除缓存
   - 然后手动触发新的部署

### 手动触发新部署：
- 在 **Deployments** 页面
- 点击右上角的 **"Redeploy"** 按钮
- 选择最新的 commit
- 点击 **"Redeploy"**

---

## 🎯 方法 2: 通过 Vercel CLI

### 安装 Vercel CLI (如果未安装):
```bash
npm install -g vercel
```

### 清除缓存并重新部署:
```bash
# 1. 登录 Vercel
vercel login

# 2. 进入项目目录
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/resume-matcher-frontend

# 3. 清除缓存并部署
vercel --prod --force

# 或者只清除缓存
vercel env pull  # 这会触发重新构建
```

---

## 🎯 方法 3: 通过 Git Push (自动触发)

### 最简单的方法：
1. **创建一个空提交来触发新部署:**
   ```bash
   cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI
   git commit --allow-empty -m "Trigger Vercel rebuild with cleared cache"
   git push origin main
   ```

2. **Vercel 会自动:**
   - 检测到新的 commit
   - 清除旧的构建缓存
   - 开始新的构建和部署

---

## 🎯 方法 4: 在 Vercel 项目设置中清除

1. **进入项目 Settings**
   - Vercel Dashboard → 你的项目 → **Settings**

2. **清除 Build Cache**
   - 在 **General** 标签页
   - 找到 **"Build Cache"** 部分
   - 点击 **"Clear Build Cache"** 按钮
   - 确认操作

3. **触发新部署**
   - 回到 **Deployments** 页面
   - 点击 **"Redeploy"** 按钮

---

## 🔍 验证缓存已清除

### 检查构建日志：
1. 进入 **Deployments** 页面
2. 点击最新的部署
3. 查看 **Build Logs**
4. 应该看到类似信息：
   ```
   Cloning github.com/EmmaW215/matchwise-ai (Branch: main, Commit: xxxxx)
   Restored build cache from previous deployment
   ```
   如果缓存已清除，可能会看到：
   ```
   No build cache found - starting fresh build
   ```

---

## ⚠️ 注意事项

1. **清除缓存后首次构建会较慢**
   - 所有依赖需要重新下载
   - 构建时间可能增加 2-3 分钟

2. **环境变量不会受影响**
   - 清除缓存不会删除环境变量
   - 环境变量在 Vercel Settings 中管理

3. **推荐操作顺序**
   - 先清除缓存
   - 再触发新部署
   - 等待构建完成
   - 验证部署成功

---

## 🚀 快速操作 (推荐)

**最快的方法：**
1. Vercel Dashboard → 你的项目
2. Deployments → 点击最新部署的 **"..."** 菜单
3. 选择 **"Redeploy"** → 勾选 **"Use existing Build Cache"** 的相反选项
4. 点击 **"Redeploy"**

或者：

```bash
# 在项目目录执行
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI
git commit --allow-empty -m "Clear cache and redeploy"
git push origin main
```

---

## 📞 如果遇到问题

- 检查 Vercel 构建日志中的错误信息
- 确认 GitHub 仓库连接正常
- 验证环境变量配置正确
- 查看 Vercel Status: https://www.vercel-status.com/
