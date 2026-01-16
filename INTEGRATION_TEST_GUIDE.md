# SmartSuccess.AI + MatchWise AI 集成测试指南

## 📋 测试前准备

1. ✅ **确认 MatchWise AI 已配置允许 iframe 嵌入**
   - 检查 MatchWise AI 的 `next.config.ts` 中是否配置了 `Content-Security-Policy` 和 `X-Frame-Options`
   - 确认允许的域名包含 SmartSuccess.AI 的生产环境域名

2. ✅ **启动 SmartSuccess.AI 开发服务器**
   ```bash
   cd resume-matcher-frontend
   npm run dev
   ```
   - 访问: http://localhost:3000

3. ✅ **打开浏览器开发者工具**
   - 按 `F12` 打开开发者工具
   - 切换到 **Console** 标签查看日志
   - 切换到 **Network** 标签查看网络请求

---

## 🧪 测试清单

### 1. iframe 加载测试 ✅

#### 测试步骤：
1. 访问 SmartSuccess.AI 主页 (http://localhost:3000)
2. 查看中间主内容区域
3. 观察浏览器控制台

#### 预期结果：
- ✅ iframe 正常加载 MatchWise AI 页面
- ✅ 控制台显示: `✅ MatchWise AI iframe loaded successfully`
- ✅ 中间区域显示 MatchWise AI 的完整内容
- ✅ 没有 "MatchWise AI Integration Pending" 错误消息

#### 失败情况处理：
- ❌ 如果 15 秒后仍未加载，显示错误消息
- ❌ 控制台显示: `⚠️ MatchWise AI iframe failed to load within timeout (15s)`
- ✅ 显示友好的错误提示和"Open MatchWise AI (New Tab)"按钮

---

### 2. 消息通信测试 ✅

#### 测试步骤：
1. iframe 加载完成后（约 0.5 秒后）
2. 查看浏览器控制台日志

#### 预期结果（开发环境）：
- ✅ 控制台显示: `📤 Sent message to MatchWise AI: { action: 'getLoginStatus' }`
- ✅ 控制台显示: `📤 Sent message to MatchWise AI: { action: 'hideVisitorCounter' }`
- ✅ 如果 MatchWise AI 响应，显示: `📨 Message received from MatchWise AI: ...`

#### 消息发送确认：
- ✅ `getLoginStatus` - 查询登录状态
- ✅ `hideVisitorCounter` - 隐藏访客计数器

---

### 3. 登录状态同步测试 ✅

#### 测试场景 A：未登录用户

**测试步骤：**
1. 访问 SmartSuccess.AI 主页
2. 查看左侧菜单栏底部
3. 查看右侧工具栏底部

**预期结果：**
- ✅ 左侧显示: "Sign in with Google" 按钮
- ✅ 右侧显示: "MatchWise Guest" 状态
- ✅ 控制台可能显示: `✅ Login status updated: Guest`

#### 测试场景 B：已登录用户

**测试步骤：**
1. 在 MatchWise AI iframe 中点击 "Sign in with Google"
2. 完成登录流程
3. 观察 SmartSuccess.AI 左侧菜单栏和右侧工具栏

**预期结果：**
- ✅ 左侧菜单栏显示用户信息（姓名、邮箱）
- ✅ 右侧工具栏显示: "MatchWise Connected" + 用户信息
- ✅ 控制台显示: `✅ User logged in to MatchWise: { userInfo }`
- ✅ 登录状态实时同步到 SmartSuccess.AI

#### 测试场景 C：登出用户

**测试步骤：**
1. 在 MatchWise AI iframe 中点击登出
2. 观察 SmartSuccess.AI 界面变化

**预期结果：**
- ✅ 左侧菜单栏恢复为 "Sign in with Google" 按钮
- ✅ 右侧工具栏显示: "MatchWise Guest" 状态
- ✅ 控制台显示: `👋 User logged out from MatchWise`

---

### 4. 登录按钮功能测试 ✅

#### 测试场景 A：左侧菜单栏登录按钮

**测试步骤：**
1. 确认用户未登录状态
2. 点击左侧菜单栏底部的 "Sign in with Google" 按钮
3. 观察 iframe 中是否显示登录弹窗

**预期结果：**
- ✅ iframe 中显示 MatchWise AI 的登录弹窗
- ✅ 控制台显示: `📤 Sent message to MatchWise AI: { action: 'showLoginModal', message: '...' }`

#### 测试场景 B：右侧工具栏登录按钮

**测试步骤：**
1. 确认用户未登录状态
2. 点击右侧工具栏底部的 "Sign in to MatchWise" 按钮
3. 观察 iframe 中是否显示登录弹窗

**预期结果：**
- ✅ iframe 中显示 MatchWise AI 的登录弹窗
- ✅ 如果 iframe 未加载，则在新标签页中打开 MatchWise AI（fallback）

---

### 5. 功能访问控制测试 ✅

#### 测试场景 A：Mock Interview 按钮（未登录）

**测试步骤：**
1. 确认用户未登录状态
2. 点击左侧菜单栏的 "🎤 Mock Interview" 按钮
3. 观察是否触发登录弹窗

**预期结果：**
- ✅ iframe 中显示登录弹窗
- ✅ 提示信息: "Please sign in to access SmartSuccess.AI Mock Interview features"
- ✅ 控制台显示消息发送日志

#### 测试场景 B：Mock Interview 按钮（已登录）

**测试步骤：**
1. 先登录 MatchWise AI
2. 点击左侧菜单栏的 "🎤 Mock Interview" 按钮
3. 观察页面跳转

**预期结果：**
- ✅ 直接跳转到 `/interview` 页面
- ✅ 不再显示登录弹窗
- ✅ 页面正常加载

#### 测试场景 C：My Records 按钮（未登录）

**测试步骤：**
1. 确认用户未登录状态
2. 点击左侧菜单栏的 "📁 My Records" 按钮
3. 观察是否触发登录弹窗

**预期结果：**
- ✅ iframe 中显示登录弹窗
- ✅ 提示信息: "Please sign in to access SmartSuccess.AI My Records features"
- ✅ 控制台显示消息发送日志

#### 测试场景 D：My Records 按钮（已登录）

**测试步骤：**
1. 先登录 MatchWise AI
2. 点击左侧菜单栏的 "📁 My Records" 按钮
3. 观察页面跳转

**预期结果：**
- ✅ 直接跳转到 `/dashboard` 页面
- ✅ 不再显示登录弹窗
- ✅ 页面正常加载

---

### 6. 访客计数器隐藏测试 ✅

#### 测试步骤：
1. iframe 加载完成后
2. 查看 MatchWise AI iframe 中的内容
3. 观察访客计数器是否已隐藏

**预期结果：**
- ✅ MatchWise AI 页面中的访客计数器组件已隐藏
- ✅ 控制台显示: `📤 Sent message to MatchWise AI: { action: 'hideVisitorCounter' }`
- ✅ MatchWise AI 正确响应并隐藏计数器

---

### 7. 跨域消息安全测试 ✅

#### 测试步骤：
1. 打开浏览器控制台
2. 尝试从其他域名发送消息（测试用）

**预期结果：**
- ✅ 只有来自 `https://matchwise-ai.vercel.app` 的消息被接受
- ✅ 其他域名的消息被忽略（控制台显示: `🚫 Message from unauthorized origin: ...`）
- ✅ 安全性验证通过

---

## 📊 测试结果记录

### 测试日期: _______________

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 1. iframe 加载 | ⬜ | |
| 2. 消息通信 | ⬜ | |
| 3. 登录状态同步（未登录） | ⬜ | |
| 3. 登录状态同步（已登录） | ⬜ | |
| 3. 登录状态同步（登出） | ⬜ | |
| 4. 登录按钮功能 | ⬜ | |
| 5. Mock Interview（未登录） | ⬜ | |
| 5. Mock Interview（已登录） | ⬜ | |
| 5. My Records（未登录） | ⬜ | |
| 5. My Records（已登录） | ⬜ | |
| 6. 访客计数器隐藏 | ⬜ | |
| 7. 跨域消息安全 | ⬜ | |

---

## 🔍 故障排查

### 问题 1: iframe 无法加载

**症状：** 显示 "MatchWise AI Integration Pending" 错误消息

**可能原因：**
- MatchWise AI 的 CSP 配置不正确
- MatchWise AI 的 X-Frame-Options 限制
- 网络连接问题

**解决方案：**
1. 检查 MatchWise AI 的 `next.config.ts` 配置
2. 检查浏览器控制台是否有 CORS 错误
3. 尝试直接访问 MatchWise AI 网站确认是否正常

---

### 问题 2: 消息通信不工作

**症状：** 控制台没有消息发送/接收日志

**可能原因：**
- iframe 未完全加载
- postMessage 格式不正确
- origin 验证失败

**解决方案：**
1. 确认 iframe 已加载（检查 `iframeLoaded` 状态）
2. 检查消息格式是否正确：`{ action: 'xxx' }` 或 `{ type: 'xxx' }`
3. 确认 `MATCHWISE_URL` 常量正确：`https://matchwise-ai.vercel.app`

---

### 问题 3: 登录状态不同步

**症状：** 在 MatchWise AI 中登录后，SmartSuccess.AI 界面未更新

**可能原因：**
- MatchWise AI 未发送登录状态消息
- 消息监听器未正确设置
- origin 验证失败

**解决方案：**
1. 检查 MatchWise AI 是否实现了 `useParentMessage` hook
2. 检查浏览器控制台是否有消息接收日志
3. 确认 `onAuthStateChanged` 监听器正在发送消息

---

### 问题 4: 功能按钮不响应

**症状：** 点击按钮无反应

**可能原因：**
- 事件处理函数未绑定
- JavaScript 错误
- 状态未正确更新

**解决方案：**
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认按钮的 `onClick` 处理函数正确绑定
3. 检查 React DevTools 中的组件状态

---

## ✅ 代码验证清单

### SmartSuccess.AI 端代码检查：

- [x] **iframe 配置** ✅
  - [x] `src` 设置为 `https://matchwise-ai.vercel.app`
  - [x] `allow` 属性包含必要的权限
  - [x] `sandbox` 属性设置正确
  - [x] `onLoad` 和 `onError` 处理函数

- [x] **消息监听** ✅
  - [x] `useEffect` 监听 `window.message` 事件
  - [x] origin 验证（只接受来自 MatchWise AI 的消息）
  - [x] 消息类型处理（loginStatus, loginSuccess, logout）
  - [x] 清理函数（removeEventListener）

- [x] **消息发送** ✅
  - [x] `checkMatchwiseLoginStatus()` - 查询登录状态
  - [x] `showMatchwiseLogin()` - 显示登录弹窗
  - [x] `hideMatchwiseVisitorCounter()` - 隐藏访客计数器
  - [x] 所有函数都有 origin 验证和错误处理

- [x] **状态管理** ✅
  - [x] `matchwiseLoginStatus` - 登录状态
  - [x] `iframeError` - iframe 错误状态
  - [x] `iframeLoaded` - iframe 加载状态

- [x] **功能访问控制** ✅
  - [x] `handleMockInterviewClick()` - Mock Interview 按钮逻辑
  - [x] `handleMyRecordsClick()` - My Records 按钮逻辑
  - [x] 登录检查逻辑正确

- [x] **UI 组件** ✅
  - [x] 左侧菜单栏显示登录状态
  - [x] 右侧工具栏显示 MatchWise 连接状态
  - [x] 错误提示消息友好且有用

---

## 🎯 测试完成标准

### 必须通过：
- ✅ iframe 能够正常加载 MatchWise AI
- ✅ 消息通信工作正常（发送和接收）
- ✅ 登录状态能够实时同步
- ✅ 功能访问控制正常工作
- ✅ 访客计数器已隐藏
- ✅ 跨域消息安全验证通过

### 功能完整性：
- ✅ 所有按钮响应正常
- ✅ 所有状态更新正确
- ✅ 错误处理友好
- ✅ 用户体验流畅

---

## 📝 测试记录模板

```
测试日期: 2025-01-XX
测试人员: _______________
测试环境: 开发环境 / 生产环境

测试结果总结:
_______________________________________________________
_______________________________________________________
_______________________________________________________

发现的问题:
1. ___________________________________________________
2. ___________________________________________________
3. ___________________________________________________

已修复问题:
1. ___________________________________________________
2. ___________________________________________________
3. ___________________________________________________

待处理问题:
1. ___________________________________________________
2. ___________________________________________________
3. ___________________________________________________

测试结论:
[ ] 通过 - 所有功能正常工作
[ ] 部分通过 - 存在已知问题，但不影响主要功能
[ ] 失败 - 存在严重问题，需要修复

备注:
_______________________________________________________
_______________________________________________________
```

---

**测试完成后，请填写测试记录并确认所有功能正常工作！** ✅
