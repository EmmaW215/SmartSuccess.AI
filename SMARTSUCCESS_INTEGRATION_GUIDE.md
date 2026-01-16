# SmartSuccess.AI 集成完整指南

## 📋 概述

本文档详细说明如何让 MatchWise AI 与 SmartSuccess.AI 的集成完全工作。需要**两边都进行配置**才能实现无缝集成。

---

## ✅ MatchWise AI 端（已完成）

### 已实现的功能

1. ✅ **Iframe 嵌入配置** - `next.config.ts` 已配置允许 SmartSuccess.AI 域名嵌入
2. ✅ **跨域通信 Hook** - `useParentMessage.ts` 已实现消息监听和响应
3. ✅ **登录弹窗组件** - `LoginModal.tsx` 已创建
4. ✅ **访客计数器隐藏** - `VisitorCounter.tsx` 已支持隐藏功能
5. ✅ **主页面集成** - `page.tsx` 已集成所有功能
6. ✅ **登录状态通知** - 自动向父页面发送登录状态变化

### MatchWise AI 端需要做的（部署相关）

#### 1. 部署到生产环境

```bash
# 在 resume-matcher-frontend 目录下
cd resume-matcher-frontend
npm run build
# 部署到 Vercel 或其他平台
```

#### 2. 确认部署后的 URL

- 确保 MatchWise AI 的生产环境 URL 已确定
- 例如：`https://matchwise-ai.vercel.app`

#### 3. 更新允许的域名（如果需要）

如果 SmartSuccess.AI 使用不同的域名，需要更新以下文件：

**文件**: `resume-matcher-frontend/src/app/hooks/useParentMessage.ts`

```typescript
const allowedOrigins = [
  'https://smartsuccess-ai.vercel.app',  // 生产环境
  'https://your-smartsuccess-domain.com', // 如果有其他域名
  'http://localhost:3000', // 开发环境
];
```

**文件**: `resume-matcher-frontend/next.config.ts`

```typescript
{
  key: 'Content-Security-Policy',
  value: "frame-ancestors 'self' https://smartsuccess-ai.vercel.app https://your-smartsuccess-domain.com;",
}
```

#### 4. 测试清单

在部署前，请测试以下功能：

- [ ] 在浏览器中直接访问 MatchWise AI，确保功能正常
- [ ] 检查控制台是否有错误
- [ ] 测试登录/登出功能
- [ ] 确认访客计数器正常显示

---

## 🔧 SmartSuccess.AI 端需要做的

### 1. 在 Home 页面嵌入 MatchWise AI iframe

**位置**: SmartSuccess.AI 的 Home 页面中间区域

**代码示例**:

```tsx
// 在 SmartSuccess.AI 的 Home 页面组件中
import { useEffect, useRef, useState } from 'react';

export default function HomePage() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [matchwiseLoginStatus, setMatchwiseLoginStatus] = useState<{
    isLoggedIn: boolean;
    userInfo: any;
  } | null>(null);

  // MatchWise AI 的 URL（需要替换为实际的生产环境 URL）
  const MATCHWISE_URL = 'https://matchwise-ai.vercel.app'; // 替换为实际 URL

  // 监听来自 MatchWise AI iframe 的消息
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 安全检查：只接受来自 MatchWise AI 的消息
      if (event.origin !== MATCHWISE_URL) {
        return;
      }

      // 处理登录状态更新
      if (event.data.type === 'loginStatus') {
        setMatchwiseLoginStatus({
          isLoggedIn: event.data.isLoggedIn,
          userInfo: event.data.userInfo,
        });
      }

      // 处理登录成功通知
      if (event.data.type === 'loginSuccess') {
        setMatchwiseLoginStatus({
          isLoggedIn: true,
          userInfo: event.data.userInfo,
        });
        // 可以在这里显示成功提示
        console.log('User logged in to MatchWise:', event.data.userInfo);
      }

      // 处理登出通知
      if (event.data.type === 'logout') {
        setMatchwiseLoginStatus({
          isLoggedIn: false,
          userInfo: null,
        });
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // 查询 MatchWise AI 的登录状态
  const checkMatchwiseLoginStatus = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { action: 'getLoginStatus' },
        MATCHWISE_URL
      );
    }
  };

  // 显示 MatchWise AI 登录弹窗
  const showMatchwiseLogin = (message?: string) => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { action: 'showLoginModal', message },
        MATCHWISE_URL
      );
    }
  };

  // 隐藏 MatchWise AI 的访客计数器
  const hideMatchwiseVisitorCounter = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { action: 'hideVisitorCounter' },
        MATCHWISE_URL
      );
    }
  };

  // 页面加载时查询登录状态并隐藏访客计数器
  useEffect(() => {
    // 等待 iframe 加载完成
    const timer = setTimeout(() => {
      checkMatchwiseLoginStatus();
      hideMatchwiseVisitorCounter();
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="home-page">
      {/* 左侧菜单栏 */}
      <aside className="left-sidebar">
        {/* 你的左侧菜单内容 */}
      </aside>

      {/* 中间区域 - MatchWise AI */}
      <main className="main-content">
        <iframe
          ref={iframeRef}
          src={MATCHWISE_URL}
          style={{
            width: '100%',
            height: '100vh',
            border: 'none',
            display: 'block',
          }}
          title="MatchWise AI"
          allow="camera; microphone; geolocation"
        />
      </main>

      {/* 右侧工具栏 */}
      <aside className="right-sidebar">
        {/* 你的右侧工具栏内容 */}
        
        {/* 可选：显示 MatchWise AI 登录状态 */}
        {matchwiseLoginStatus && (
          <div className="matchwise-status">
            {matchwiseLoginStatus.isLoggedIn ? (
              <div>
                <p>✅ Logged in to MatchWise</p>
                <p>{matchwiseLoginStatus.userInfo?.displayName || matchwiseLoginStatus.userInfo?.email}</p>
              </div>
            ) : (
              <button onClick={() => showMatchwiseLogin('Please sign in to use MatchWise features')}>
                Sign in to MatchWise
              </button>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}
```

### 2. 控制功能访问（未登录用户）

在 SmartSuccess.AI 中，当用户尝试访问需要登录的功能时：

```tsx
// 示例：在某个功能按钮点击时
const handleFeatureClick = () => {
  if (!matchwiseLoginStatus?.isLoggedIn) {
    // 显示 MatchWise AI 的登录弹窗
    showMatchwiseLogin('Please sign in to use this feature');
    return;
  }
  
  // 继续执行功能
  // ...
};
```

### 3. 样式调整（可选）

确保 iframe 的样式适合你的布局：

```css
.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.main-content iframe {
  width: 100%;
  height: 100%;
  border: none;
}
```

### 4. 错误处理

添加 iframe 加载错误处理：

```tsx
const [iframeError, setIframeError] = useState(false);

<iframe
  ref={iframeRef}
  src={MATCHWISE_URL}
  onError={() => setIframeError(true)}
  onLoad={() => setIframeError(false)}
  // ...
/>

{iframeError && (
  <div className="error-message">
    Failed to load MatchWise AI. Please refresh the page.
  </div>
)}
```

---

## 🧪 测试步骤

### 1. 本地开发测试

#### MatchWise AI 端：
```bash
cd resume-matcher-frontend
npm run dev
# 运行在 http://localhost:3000
```

#### SmartSuccess.AI 端：
```bash
# 在你的 SmartSuccess.AI 项目中
# 将 MATCHWISE_URL 设置为 'http://localhost:3000'
# 运行开发服务器
```

### 2. 测试清单

#### 基础功能测试：
- [ ] iframe 能够正常加载 MatchWise AI
- [ ] MatchWise AI 页面在 iframe 中正常显示
- [ ] 没有控制台错误

#### 消息通信测试：
- [ ] SmartSuccess.AI 发送 `hideVisitorCounter` 消息，访客计数器隐藏
- [ ] SmartSuccess.AI 发送 `getLoginStatus` 消息，能收到登录状态
- [ ] SmartSuccess.AI 发送 `showLoginModal` 消息，登录弹窗显示

#### 登录状态同步测试：
- [ ] 在 MatchWise AI 中登录，SmartSuccess.AI 能收到 `loginStatus` 和 `loginSuccess` 消息
- [ ] 在 MatchWise AI 中登出，SmartSuccess.AI 能收到 `loginStatus` 消息（isLoggedIn: false）
- [ ] SmartSuccess.AI 能正确显示登录状态

#### 功能访问控制测试：
- [ ] 未登录用户尝试访问功能时，能触发登录弹窗
- [ ] 登录后，功能可以正常使用

### 3. 生产环境测试

1. **部署 MatchWise AI** 到生产环境
2. **更新 SmartSuccess.AI** 中的 `MATCHWISE_URL` 为生产环境 URL
3. **部署 SmartSuccess.AI** 到生产环境
4. **进行完整的功能测试**

---

## 🔍 故障排查

### 问题 1: iframe 无法加载

**症状**: iframe 显示空白或错误

**解决方案**:
1. 检查浏览器控制台的错误信息
2. 确认 `next.config.ts` 中的 `Content-Security-Policy` 配置正确
3. 确认 SmartSuccess.AI 的域名在允许列表中
4. 检查 MatchWise AI 的 URL 是否正确

### 问题 2: postMessage 不工作

**症状**: 消息无法发送或接收

**解决方案**:
1. 打开浏览器开发者工具，查看 Console 标签
2. 检查是否有 origin 验证失败的警告
3. 确认 `allowedOrigins` 数组包含正确的域名
4. 确认消息格式正确：`{ action: 'xxx' }` 或 `{ type: 'xxx' }`

### 问题 3: 登录状态不同步

**症状**: 登录后 SmartSuccess.AI 没有收到通知

**解决方案**:
1. 检查 `useParentMessage.ts` 中的 `onAuthStateChanged` 监听器
2. 确认 `window.parent.postMessage` 被正确调用
3. 在 SmartSuccess.AI 端添加消息监听器日志，查看是否收到消息
4. 确认 iframe 已完全加载后再发送消息

### 问题 4: 访客计数器没有隐藏

**症状**: 收到 `hideVisitorCounter` 消息但计数器仍然显示

**解决方案**:
1. 检查 `VisitorCounter` 组件的 `isVisible` prop 是否正确传递
2. 确认 `useParentMessage` hook 中的 `hideVisitorCounter` 处理函数被调用
3. 检查页面组件中的 `showVisitorCounter` 状态是否正确更新

---

## 📝 消息协议参考

### SmartSuccess.AI → MatchWise AI

```typescript
// 显示登录弹窗
{
  action: 'showLoginModal',
  message?: string  // 可选提示信息
}

// 查询登录状态
{
  action: 'getLoginStatus'
}

// 隐藏访客计数器
{
  action: 'hideVisitorCounter'
}
```

### MatchWise AI → SmartSuccess.AI

```typescript
// 登录状态响应
{
  type: 'loginStatus',
  isLoggedIn: boolean,
  userInfo: {
    uid: string,
    displayName: string | null,
    email: string | null,
    photoURL: string | null,
  } | null
}

// 登录成功通知
{
  type: 'loginSuccess',
  userInfo: {
    uid: string,
    displayName: string | null,
    email: string | null,
    photoURL: string | null,
  }
}

// 登出通知（通过 loginStatus 的 isLoggedIn: false 实现）
```

---

## 🚀 部署检查清单

### MatchWise AI 端：
- [ ] 代码已提交到 Git
- [ ] 已部署到生产环境
- [ ] 确认生产环境 URL
- [ ] 测试生产环境功能正常
- [ ] 确认 `next.config.ts` 中的域名配置正确

### SmartSuccess.AI 端：
- [ ] 已添加 iframe 嵌入代码
- [ ] 已添加消息监听器
- [ ] 已更新 `MATCHWISE_URL` 为生产环境 URL
- [ ] 已实现功能访问控制
- [ ] 已测试所有消息通信
- [ ] 已部署到生产环境

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. 浏览器控制台的错误信息
2. 网络请求是否成功
3. 消息格式是否正确
4. Origin 验证是否通过

---

**文档版本**: 1.0  
**最后更新**: 2025年1月  
**维护者**: MatchWise AI 开发团队