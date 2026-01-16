# MatchWise AI - SmartSuccess.AI 集成配合要求

## 📋 项目背景

SmartSuccess.AI 计划将 MatchWise AI 的核心功能（简历分析、匹配评分、求职信生成）嵌入到其平台中，以提供统一的用户体验。为了实现无缝集成，MatchWise AI 需要进行一些配合修改。

---

## 一、为什么需要配合修改？

### 1.1 集成目标

SmartSuccess.AI 希望：
- 在其 Home 页面中间区域嵌入 MatchWise AI 的完整功能
- 保留 SmartSuccess.AI 的左侧菜单栏和右侧工具栏
- 实现登录状态同步，让用户在 SmartSuccess.AI 中也能使用 MatchWise AI 的登录功能
- 控制功能访问，未登录用户访问某些功能时提示登录

### 1.2 技术需求

为了实现上述目标，需要：
1. **允许 iframe 嵌入**：MatchWise AI 需要允许被其他域名通过 iframe 嵌入
2. **跨域通信支持**：通过 postMessage API 实现父子页面之间的通信
3. **登录状态共享**：将登录状态变化通知给父页面（SmartSuccess.AI）
4. **UI 控制**：支持隐藏访客计数器等 UI 元素

---

## 二、需要实现的功能

### 2.1 允许 iframe 嵌入

**问题**：默认情况下，Next.js 应用可能不允许被其他域名通过 iframe 嵌入（X-Frame-Options 限制）。

**解决方案**：修改 `next.config.ts` 或 `next.config.js` 文件。

**实现代码**：

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  
  // 允许被 SmartSuccess.AI 嵌入
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN', // 或 'ALLOW-FROM https://smartsuccess-ai.vercel.app'
          },
          // 或者使用 Content-Security-Policy
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' https://smartsuccess-ai.vercel.app https://*.vercel.app;",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

**注意**：如果使用 `ALLOW-FROM`，某些浏览器可能不支持。推荐使用 `Content-Security-Policy` 的 `frame-ancestors` 指令。

---

### 2.2 实现 postMessage 监听器

**功能**：监听来自父页面（SmartSuccess.AI）的消息，并执行相应操作。

**实现位置**：在根布局文件或主页面组件中添加。

**实现代码**：

```typescript
// 在 layout.tsx 或 page.tsx 中添加
'use client';

import { useEffect } from 'react';

export default function Layout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // 监听来自父页面的消息
    const handleMessage = (event: MessageEvent) => {
      // 安全检查：只接受来自 SmartSuccess.AI 的消息
      const allowedOrigins = [
        'https://smartsuccess-ai.vercel.app',
        'http://localhost:3000', // 开发环境
      ];

      if (!allowedOrigins.includes(event.origin)) {
        console.warn('Rejected message from unauthorized origin:', event.origin);
        return;
      }

      // 处理不同的操作
      switch (event.data.action) {
        case 'showLoginModal':
          // 显示登录弹窗
          handleShowLoginModal(event.data.message);
          break;

        case 'getLoginStatus':
          // 返回当前登录状态
          handleGetLoginStatus(event);
          break;

        case 'hideVisitorCounter':
          // 隐藏访客计数器
          handleHideVisitorCounter();
          break;

        default:
          console.warn('Unknown action:', event.data.action);
      }
    };

    window.addEventListener('message', handleMessage);

    // 清理
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  return <>{children}</>;
}
```

---

### 2.3 实现登录弹窗显示功能

**功能**：当收到 `showLoginModal` 消息时，显示登录弹窗。

**实现代码**：

```typescript
// 假设你有一个登录组件或函数
const handleShowLoginModal = (message?: string) => {
  // 方法 1: 如果使用现有的登录组件
  // 触发登录弹窗显示
  setShowLoginModal(true);
  if (message) {
    setLoginMessage(message);
  }

  // 方法 2: 如果使用 Firebase Auth 的 signInWithPopup
  // import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
  // const provider = new GoogleAuthProvider();
  // signInWithPopup(auth, provider);
};
```

**在组件中使用**：

```typescript
// 在页面组件中
const [showLoginModal, setShowLoginModal] = useState(false);
const [loginMessage, setLoginMessage] = useState('');

// 暴露给全局的函数
useEffect(() => {
  (window as any).handleShowLoginModal = (message?: string) => {
    setShowLoginModal(true);
    if (message) {
      setLoginMessage(message);
    }
  };
}, []);
```

---

### 2.4 实现登录状态查询功能

**功能**：当收到 `getLoginStatus` 消息时，返回当前登录状态。

**实现代码**：

```typescript
// 假设使用 Firebase Auth
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '@/lib/firebase'; // 你的 Firebase 配置

const handleGetLoginStatus = (event: MessageEvent) => {
  // 获取当前用户
  const user = auth.currentUser;

  // 发送登录状态回父页面
  if (event.source && event.source !== window) {
    (event.source as Window).postMessage(
      {
        type: 'loginStatus',
        isLoggedIn: !!user,
        userInfo: user
          ? {
              uid: user.uid,
              displayName: user.displayName,
              email: user.email,
              photoURL: user.photoURL,
            }
          : null,
      },
      event.origin
    );
  }
};
```

**实时监听登录状态变化**：

```typescript
useEffect(() => {
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    // 通知父页面登录状态变化
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(
        {
          type: 'loginStatus',
          isLoggedIn: !!user,
          userInfo: user
            ? {
                uid: user.uid,
                displayName: user.displayName,
                email: user.email,
                photoURL: user.photoURL,
              }
            : null,
        },
        '*' // 或指定 'https://smartsuccess-ai.vercel.app'
      );
    }

    // 如果登录成功，发送成功通知
    if (user) {
      window.parent.postMessage(
        {
          type: 'loginSuccess',
          userInfo: {
            uid: user.uid,
            displayName: user.displayName,
            email: user.email,
            photoURL: user.photoURL,
          },
        },
        '*'
      );
    }
  });

  return () => unsubscribe();
}, []);
```

---

### 2.5 实现访客计数器隐藏功能

**功能**：当收到 `hideVisitorCounter` 消息时，隐藏访客计数器。

**实现代码**：

```typescript
// 在访客计数器组件中
const [isVisible, setIsVisible] = useState(true);

useEffect(() => {
  const handleMessage = (event: MessageEvent) => {
    if (
      event.origin === 'https://smartsuccess-ai.vercel.app' &&
      event.data.action === 'hideVisitorCounter'
    ) {
      setIsVisible(false);
    }
  };

  window.addEventListener('message', handleMessage);
  return () => window.removeEventListener('message', handleMessage);
}, []);

// 在组件渲染中
if (!isVisible) return null;

// 或者使用 CSS 隐藏
return (
  <div style={{ display: isVisible ? 'block' : 'none' }}>
    {/* 访客计数器内容 */}
  </div>
);
```

---

## 三、完整实现示例

### 3.1 创建消息处理 Hook

**文件**: `hooks/useParentMessage.ts`

```typescript
import { useEffect } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '@/lib/firebase';

interface MessageHandler {
  showLoginModal?: (message?: string) => void;
  hideVisitorCounter?: () => void;
}

export function useParentMessage(handlers: MessageHandler) {
  useEffect(() => {
    const allowedOrigins = [
      'https://smartsuccess-ai.vercel.app',
      'http://localhost:3000',
    ];

    const handleMessage = (event: MessageEvent) => {
      if (!allowedOrigins.includes(event.origin)) {
        return;
      }

      switch (event.data.action) {
        case 'showLoginModal':
          handlers.showLoginModal?.(event.data.message);
          break;

        case 'getLoginStatus':
          const user = auth.currentUser;
          if (event.source && event.source !== window) {
            (event.source as Window).postMessage(
              {
                type: 'loginStatus',
                isLoggedIn: !!user,
                userInfo: user
                  ? {
                      uid: user.uid,
                      displayName: user.displayName,
                      email: user.email,
                      photoURL: user.photoURL,
                    }
                  : null,
              },
              event.origin
            );
          }
          break;

        case 'hideVisitorCounter':
          handlers.hideVisitorCounter?.();
          break;
      }
    };

    window.addEventListener('message', handleMessage);

    // 监听登录状态变化并通知父页面
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage(
          {
            type: 'loginStatus',
            isLoggedIn: !!user,
            userInfo: user
              ? {
                  uid: user.uid,
                  displayName: user.displayName,
                  email: user.email,
                  photoURL: user.photoURL,
                }
              : null,
          },
          '*'
        );

        if (user) {
          window.parent.postMessage(
            {
              type: 'loginSuccess',
              userInfo: {
                uid: user.uid,
                displayName: user.displayName,
                email: user.email,
                photoURL: user.photoURL,
              },
            },
            '*'
          );
        }
      }
    });

    return () => {
      window.removeEventListener('message', handleMessage);
      unsubscribe();
    };
  }, [handlers]);
}
```

### 3.2 在主页面中使用

**文件**: `app/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useParentMessage } from '@/hooks/useParentMessage';
import SimpleVisitorCounter from './components/SimpleVisitorCounter';

export default function Home() {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showVisitorCounter, setShowVisitorCounter] = useState(true);

  // 使用消息处理 Hook
  useParentMessage({
    showLoginModal: (message) => {
      setShowLoginModal(true);
      // 可以显示 message 提示
      if (message) {
        console.log('Login requested:', message);
      }
    },
    hideVisitorCounter: () => {
      setShowVisitorCounter(false);
    },
  });

  return (
    <div>
      {/* 访客计数器 - 条件渲染 */}
      {showVisitorCounter && <SimpleVisitorCounter />}

      {/* 登录弹窗 */}
      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
        />
      )}

      {/* 其他页面内容 */}
      {/* ... */}
    </div>
  );
}
```

---

## 四、消息协议规范

### 4.1 从 SmartSuccess.AI 发送的消息

| action | 说明 | 参数 |
|--------|------|------|
| `showLoginModal` | 显示登录弹窗 | `message?: string` (可选提示信息) |
| `getLoginStatus` | 查询登录状态 | 无 |
| `hideVisitorCounter` | 隐藏访客计数器 | 无 |

**消息格式**：
```typescript
{
  action: 'showLoginModal' | 'getLoginStatus' | 'hideVisitorCounter',
  message?: string // 仅用于 showLoginModal
}
```

### 4.2 发送给 SmartSuccess.AI 的消息

| type | 说明 | 数据 |
|------|------|------|
| `loginStatus` | 登录状态响应 | `{ isLoggedIn: boolean, userInfo: UserInfo \| null }` |
| `loginSuccess` | 登录成功通知 | `{ userInfo: UserInfo }` |
| `logout` | 登出通知 | 无数据 |

**消息格式**：
```typescript
// loginStatus
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

// loginSuccess
{
  type: 'loginSuccess',
  userInfo: {
    uid: string,
    displayName: string | null,
    email: string | null,
    photoURL: string | null,
  }
}

// logout
{
  type: 'logout'
}
```

---

## 五、安全检查

### 5.1 Origin 验证

**必须验证消息来源**，防止恶意网站发送消息：

```typescript
const ALLOWED_ORIGINS = [
  'https://smartsuccess-ai.vercel.app',
  'http://localhost:3000', // 仅开发环境
];

if (!ALLOWED_ORIGINS.includes(event.origin)) {
  console.warn('Rejected message from unauthorized origin');
  return;
}
```

### 5.2 消息验证

验证消息格式和内容：

```typescript
const isValidMessage = (data: any): boolean => {
  if (!data || typeof data !== 'object') return false;
  if (!data.action && !data.type) return false;
  return true;
};

if (!isValidMessage(event.data)) {
  console.warn('Invalid message format');
  return;
}
```

---

## 六、测试清单

### 6.1 功能测试

- [ ] iframe 可以被 SmartSuccess.AI 正常嵌入
- [ ] 收到 `showLoginModal` 消息时能显示登录弹窗
- [ ] 收到 `getLoginStatus` 消息时能正确返回登录状态
- [ ] 收到 `hideVisitorCounter` 消息时能隐藏访客计数器
- [ ] 登录状态变化时能通知父页面
- [ ] 登录成功后能发送 `loginSuccess` 消息
- [ ] 登出后能发送 `logout` 消息

### 6.2 安全测试

- [ ] 来自未授权域名的消息被正确拒绝
- [ ] 消息格式验证正常工作
- [ ] 不会泄露敏感信息

### 6.3 兼容性测试

- [ ] Chrome/Edge 浏览器正常工作
- [ ] Firefox 浏览器正常工作
- [ ] Safari 浏览器正常工作
- [ ] 移动端浏览器正常工作

---

## 七、部署注意事项

### 7.1 环境变量

确保生产环境配置正确：

```env
# 如果需要，添加允许嵌入的域名列表
ALLOWED_IFRAME_ORIGINS=https://smartsuccess-ai.vercel.app
```

### 7.2 CORS 配置

确保后端 API 允许来自 SmartSuccess.AI 的请求（如果 MatchWise AI 有独立后端）。

---

## 八、故障排查

### 8.1 iframe 无法加载

**问题**：iframe 显示空白或错误。

**解决方案**：
1. 检查 `X-Frame-Options` 或 `Content-Security-Policy` 配置
2. 检查浏览器控制台错误信息
3. 确认域名白名单配置正确

### 8.2 postMessage 不工作

**问题**：消息无法发送或接收。

**解决方案**：
1. 检查 origin 验证逻辑
2. 使用浏览器开发者工具查看消息
3. 确认消息格式正确

### 8.3 登录状态不同步

**问题**：登录状态无法同步到父页面。

**解决方案**：
1. 检查 `onAuthStateChanged` 监听器是否正确设置
2. 确认 `window.parent.postMessage` 调用正确
3. 检查父页面是否正确监听消息

---

## 九、实现时间估算

| 任务 | 预计时间 |
|------|---------|
| 配置 iframe 嵌入 | 30 分钟 |
| 实现 postMessage 监听器 | 1-2 小时 |
| 实现登录状态查询 | 1 小时 |
| 实现访客计数器隐藏 | 30 分钟 |
| 测试和调试 | 1-2 小时 |
| **总计** | **4-6 小时** |

---

## 十、联系信息

如有问题或需要技术支持，请联系 SmartSuccess.AI 开发团队。

---

**文档版本**: 1.0  
**最后更新**: 2025年1月  
**目标项目**: MatchWise AI  
**集成项目**: SmartSuccess.AI
