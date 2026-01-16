# SmartSuccess.AI - MatchWise AI 集成实现计划

## 📋 项目概述

本文档描述如何在 SmartSuccess.AI 中集成 MatchWise AI 的功能，通过 iframe 嵌入和 postMessage 通信实现无缝集成。

**目标**：
- 在 SmartSuccess.AI 的 Home 页面中间区域嵌入 MatchWise AI 完整功能
- 保留 SmartSuccess.AI 的左侧菜单栏和右侧工具栏
- 实现登录状态同步和功能访问控制
- 移除 MatchWise AI 的访客计数器

---

## 一、阶段 1：嵌入 MatchWise AI 主页面

### 1.1 修改 Home 页面布局

**文件位置**: `resume-matcher-frontend/src/app/page.tsx`

**实现步骤**：

#### Step 1: 添加 iframe 容器

在中间主内容区域（`<main>` 标签内）替换现有的表单内容为 iframe：

```typescript
// 在 page.tsx 中
'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // 监听来自 iframe 的消息
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 安全检查：只接受来自 matchwise-ai.vercel.app 的消息
      if (event.origin !== 'https://matchwise-ai.vercel.app') return;

      if (event.data.type === 'loginStatus') {
        setIsLoggedIn(event.data.isLoggedIn);
        setUserInfo(event.data.userInfo || null);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // 查询登录状态（iframe 加载完成后）
  useEffect(() => {
    const checkLoginStatus = () => {
      if (iframeRef.current?.contentWindow) {
        iframeRef.current.contentWindow.postMessage(
          { action: 'getLoginStatus' },
          'https://matchwise-ai.vercel.app'
        );
      }
    };

    // iframe 加载完成后查询状态
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.addEventListener('load', checkLoginStatus);
      return () => iframe.removeEventListener('load', checkLoginStatus);
    }
  }, []);

  // 登录按钮处理
  const handleLoginClick = () => {
    const iframe = iframeRef.current;
    if (iframe?.contentWindow) {
      // 发送消息给 iframe，要求显示登录弹窗
      iframe.contentWindow.postMessage(
        {
          action: 'showLoginModal',
          message: 'Please sign in to access SmartSuccess.AI features'
        },
        'https://matchwise-ai.vercel.app'
      );
    }
  };

  // Mock Interview 按钮处理
  const handleMockInterviewClick = () => {
    if (isLoggedIn) {
      // 已登录，跳转到面试页面
      window.location.href = '/interview';
    } else {
      // 未登录，显示登录弹窗
      handleLoginClick();
    }
  };

  // My Records 按钮处理
  const handleMyRecordsClick = () => {
    if (isLoggedIn) {
      // 已登录，跳转到记录页面
      window.location.href = '/dashboard';
    } else {
      // 未登录，显示登录弹窗
      handleMyRecordsClick();
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* 背景样式保持不变 */}
      <div className="fixed inset-0 bg-white/70" aria-hidden="true"></div>

      {/* ====== LEFT SIDEBAR ====== */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white/95 backdrop-blur-sm shadow-lg z-30 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
            SmartSuccess.AI
          </h1>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <Link
                href="/"
                className="flex items-center px-4 py-3 text-gray-700 bg-blue-50 rounded-lg font-medium"
              >
                <span className="mr-3">🏠</span>
                Home
              </Link>
            </li>
            <li>
              <button
                onClick={handleMockInterviewClick}
                className="flex items-center w-full px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">🎤</span>
                Mock Interview
              </button>
            </li>
            <li>
              <button
                onClick={handleMyRecordsClick}
                className="flex items-center w-full px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">📁</span>
                My Records
              </button>
            </li>
            <li>
              <Link
                href="/admin/visitor-stats"
                className="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">⚙️</span>
                Admin
              </Link>
            </li>
          </ul>
        </nav>

        {/* User Info / Login Button */}
        <div className="p-4 border-t border-gray-200">
          {isLoggedIn ? (
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-gray-500">👤</span>
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">{userInfo?.displayName || 'User'}</p>
                <p className="text-xs text-gray-400">{userInfo?.email || ''}</p>
              </div>
            </div>
          ) : (
            <button
              onClick={handleLoginClick}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Sign in with Google
            </button>
          )}
          <div className="mt-4 text-xs text-gray-400 text-center">
            powered by <span className="font-semibold text-blue-600">SmartSuccess.AI</span>
          </div>
        </div>
      </aside>

      {/* ====== MAIN CONTENT (CENTER) - IFRAME EMBED ====== */}
      <main className="flex-1 ml-64 mr-80 min-h-screen relative z-10">
        <iframe
          ref={iframeRef}
          src="https://matchwise-ai.vercel.app/"
          className="w-full h-full border-0"
          id="matchwise-iframe"
          title="MatchWise AI Resume Analysis"
          allow="camera; microphone; geolocation"
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
          style={{ minHeight: '100vh' }}
        />
      </main>

      {/* ====== RIGHT SIDEBAR ====== */}
      <aside className="fixed right-0 top-0 h-full w-80 bg-white/95 backdrop-blur-sm shadow-lg z-30 flex flex-col p-6 overflow-y-auto">
        {/* Brand Info */}
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-3">
            SmartSuccess.AI
          </h2>
          <h3 className="text-lg font-semibold text-blue-600 mb-3">
            Tailor Your Resume & Cover Letter with AI
          </h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            An AI-Powered Career Success Platform providing intelligent job application assistance,
            resume optimization, and mock interview preparation for your dream job.
          </p>
        </div>

        {/* View Demo Button */}
        <div className="mb-6">
          <Link
            href="/demo"
            className="flex items-center justify-center w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-semibold rounded-full shadow-lg hover:from-purple-600 hover:to-indigo-600 transition-all transform hover:scale-105"
          >
            <span className="mr-2">✨</span>
            View Demo Report
            <span className="ml-2">→</span>
          </Link>
          <p className="text-xs text-gray-500 mt-2 text-center">
            See what kind of analysis you'll get
          </p>
        </div>

        {/* Additional Info Cards */}
        <div className="space-y-4 flex-1">
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
            <h4 className="font-semibold text-blue-800 mb-2">🎯 Resume Matching</h4>
            <p className="text-sm text-blue-700">AI-powered analysis to match your resume with job requirements</p>
          </div>

          <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
            <h4 className="font-semibold text-purple-800 mb-2">📝 Cover Letter</h4>
            <p className="text-sm text-purple-700">Generate tailored cover letters for each application</p>
          </div>

          <Link href="/interview" className="block bg-orange-50 rounded-xl p-4 border border-orange-100 hover:bg-orange-100 transition">
            <h4 className="font-semibold text-orange-800 mb-2">🎤 Mock Interview</h4>
            <p className="text-sm text-orange-700">Voice-powered interview practice with STAR feedback</p>
          </Link>
        </div>
      </aside>
    </div>
  );
}
```

#### Step 2: 实现登录按钮点击处理

```typescript
// 在 Home 组件中添加
const handleLoginClick = () => {
  const iframe = iframeRef.current;
  if (iframe?.contentWindow) {
    // 发送消息给 iframe，要求显示登录弹窗
    iframe.contentWindow.postMessage(
      {
        action: 'showLoginModal',
        message: 'Please sign in to access SmartSuccess.AI features'
      },
      'https://matchwise-ai.vercel.app'
    );
  }
};
```

#### Step 3: 实现功能按钮登录检查

```typescript
// Mock Interview 按钮处理
const handleMockInterviewClick = () => {
  if (isLoggedIn) {
    // 已登录，跳转到面试页面
    window.location.href = '/interview';
  } else {
    // 未登录，显示登录弹窗
    handleLoginClick();
  }
};

// My Records 按钮处理
const handleMyRecordsClick = () => {
  if (isLoggedIn) {
    // 已登录，跳转到记录页面
    window.location.href = '/dashboard';
  } else {
    // 未登录，显示登录弹窗
    handleMyRecordsClick();
  }
};
```

#### Step 4: 请求隐藏访客计数器

```typescript
// 在 iframe 加载完成后发送消息
useEffect(() => {
  const iframe = iframeRef.current;
  if (iframe) {
    const handleLoad = () => {
      // 请求隐藏访客计数器
      iframe.contentWindow?.postMessage(
        { action: 'hideVisitorCounter' },
        'https://matchwise-ai.vercel.app'
      );
    };

    iframe.addEventListener('load', handleLoad);
    return () => iframe.removeEventListener('load', handleLoad);
  }
}, []);
```

---

## 二、阶段 2：登录状态同步

### 2.1 监听登录状态变化

```typescript
// 在 useEffect 中添加完整的消息监听
useEffect(() => {
  const handleMessage = (event: MessageEvent) => {
    // 安全检查
    if (event.origin !== 'https://matchwise-ai.vercel.app') return;

    switch (event.data.type) {
      case 'loginStatus':
        // 更新登录状态
        setIsLoggedIn(event.data.isLoggedIn);
        setUserInfo(event.data.userInfo || null);
        break;

      case 'loginSuccess':
        // 登录成功通知
        setIsLoggedIn(true);
        setUserInfo(event.data.userInfo);
        // 可以显示成功提示
        console.log('Login successful');
        break;

      case 'logout':
        // 登出通知
        setIsLoggedIn(false);
        setUserInfo(null);
        break;

      default:
        break;
    }
  };

  window.addEventListener('message', handleMessage);
  return () => window.removeEventListener('message', handleMessage);
}, []);
```

### 2.2 定期查询登录状态（可选）

```typescript
// 定期查询登录状态（每 30 秒）
useEffect(() => {
  const interval = setInterval(() => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { action: 'getLoginStatus' },
        'https://matchwise-ai.vercel.app'
      );
    }
  }, 30000); // 30 秒

  return () => clearInterval(interval);
}, []);
```

---

## 三、阶段 3：错误处理和边界情况

### 3.1 iframe 加载失败处理

```typescript
const [iframeError, setIframeError] = useState(false);

// 在 iframe 上添加错误处理
<iframe
  ref={iframeRef}
  src="https://matchwise-ai.vercel.app/"
  className="w-full h-full border-0"
  id="matchwise-iframe"
  onError={() => setIframeError(true)}
  title="MatchWise AI Resume Analysis"
  allow="camera; microphone; geolocation"
/>

// 显示错误信息
{iframeError && (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <p className="text-red-500 mb-4">Failed to load MatchWise AI</p>
      <a
        href="https://matchwise-ai.vercel.app/"
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:underline"
      >
        Open in new tab
      </a>
    </div>
  </div>
)}
```

### 3.2 超时处理

```typescript
const [iframeLoading, setIframeLoading] = useState(true);

useEffect(() => {
  const timer = setTimeout(() => {
    if (iframeLoading) {
      console.warn('Iframe loading timeout');
      setIframeLoading(false);
    }
  }, 10000); // 10 秒超时

  return () => clearTimeout(timer);
}, [iframeLoading]);
```

---

## 四、完整代码结构

### 4.1 完整的 Home 组件代码结构

```typescript
'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

interface UserInfo {
  displayName?: string;
  email?: string;
  photoURL?: string;
}

export default function Home() {
  // State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [iframeLoading, setIframeLoading] = useState(true);
  const [iframeError, setIframeError] = useState(false);

  // Refs
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // 消息监听
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== 'https://matchwise-ai.vercel.app') return;

      switch (event.data.type) {
        case 'loginStatus':
          setIsLoggedIn(event.data.isLoggedIn);
          setUserInfo(event.data.userInfo || null);
          break;
        case 'loginSuccess':
          setIsLoggedIn(true);
          setUserInfo(event.data.userInfo);
          break;
        case 'logout':
          setIsLoggedIn(false);
          setUserInfo(null);
          break;
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // iframe 加载处理
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleLoad = () => {
      setIframeLoading(false);
      // 隐藏访客计数器
      iframe.contentWindow?.postMessage(
        { action: 'hideVisitorCounter' },
        'https://matchwise-ai.vercel.app'
      );
      // 查询登录状态
      iframe.contentWindow?.postMessage(
        { action: 'getLoginStatus' },
        'https://matchwise-ai.vercel.app'
      );
    };

    iframe.addEventListener('load', handleLoad);
    return () => iframe.removeEventListener('load', handleLoad);
  }, []);

  // 登录按钮处理
  const handleLoginClick = () => {
    const iframe = iframeRef.current;
    if (iframe?.contentWindow) {
      iframe.contentWindow.postMessage(
        {
          action: 'showLoginModal',
          message: 'Please sign in to access SmartSuccess.AI features'
        },
        'https://matchwise-ai.vercel.app'
      );
    }
  };

  // Mock Interview 按钮处理
  const handleMockInterviewClick = () => {
    if (isLoggedIn) {
      // 已登录，跳转到面试页面
      window.location.href = '/interview';
    } else {
      // 未登录，显示登录弹窗
      handleLoginClick();
    }
  };

  // My Records 按钮处理
  const handleMyRecordsClick = () => {
    if (isLoggedIn) {
      // 已登录，跳转到记录页面
      window.location.href = '/dashboard';
    } else {
      // 未登录，显示登录弹窗
      handleLoginClick();
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ... 左侧菜单栏和右侧工具栏代码 ... */}

      {/* 中间 iframe 区域 */}
      <main className="flex-1 ml-64 mr-80 min-h-screen relative z-10">
        {iframeError ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-red-500 mb-4">Failed to load MatchWise AI</p>
              <a
                href="https://matchwise-ai.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                Open in new tab
              </a>
            </div>
          </div>
        ) : (
          <>
            {iframeLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-white/50">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading MatchWise AI...</p>
                </div>
              </div>
            )}
            <iframe
              ref={iframeRef}
              src="https://matchwise-ai.vercel.app/"
              className="w-full h-full border-0"
              id="matchwise-iframe"
              title="MatchWise AI Resume Analysis"
              allow="camera; microphone; geolocation"
              sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
              style={{ minHeight: '100vh' }}
              onError={() => setIframeError(true)}
            />
          </>
        )}
      </main>
    </div>
  );
}
```

---

## 五、测试清单

### 5.1 功能测试

- [ ] iframe 正常加载 MatchWise AI 页面
- [ ] 访客计数器已隐藏
- [ ] 点击 "Sign in with Google" 按钮能触发登录弹窗
- [ ] 登录成功后，左侧菜单栏显示用户信息
- [ ] 点击 "Mock Interview" 未登录时显示登录弹窗
- [ ] 点击 "Mock Interview" 已登录时跳转到面试页面
- [ ] 点击 "My Records" 未登录时显示登录弹窗
- [ ] 点击 "My Records" 已登录时跳转到记录页面
- [ ] 登出后，左侧菜单栏恢复为登录按钮

### 5.2 跨域通信测试

- [ ] postMessage 消息能正确发送到 iframe
- [ ] iframe 返回的消息能正确接收
- [ ] 登录状态变化能实时同步
- [ ] 消息 origin 验证正常工作

### 5.3 错误处理测试

- [ ] iframe 加载失败时显示错误信息
- [ ] 网络超时时有适当提示
- [ ] 跨域消息被正确过滤

---

## 六、部署注意事项

### 6.1 环境变量

确保 `.env.local` 或 Vercel 环境变量中配置了正确的后端 URL：

```env
NEXT_PUBLIC_BACKEND_URL=https://smartsuccess-ai.onrender.com
```

### 6.2 CORS 配置

确保后端允许来自 `https://smartsuccess-ai.vercel.app` 的请求。

### 6.3 安全检查

- 所有 postMessage 必须验证 `event.origin`
- iframe 使用 `sandbox` 属性限制权限
- 不信任来自未验证源的消息

---

## 七、后续优化建议

1. **性能优化**：添加 iframe 懒加载
2. **用户体验**：添加加载动画和错误提示
3. **功能扩展**：支持更多跨域通信功能
4. **监控**：添加错误监控和日志记录

---

**文档版本**: 1.0  
**最后更新**: 2025年1月  
**维护者**: SmartSuccess.AI Team
