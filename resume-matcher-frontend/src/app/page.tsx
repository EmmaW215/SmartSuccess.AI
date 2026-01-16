// ============================================================
// FILE: resume-matcher-frontend/src/app/page.tsx
// FULL REPLACEMENT - SmartSuccess.AI + MatchWise AI Integration
// ============================================================

'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

interface UserInfo {
  displayName?: string;
  email?: string;
  photoURL?: string;
}

interface MatchwiseLoginStatus {
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
}

export default function Home() {
  // MatchWise AI 登录状态
  const [matchwiseLoginStatus, setMatchwiseLoginStatus] = useState<MatchwiseLoginStatus | null>(null);

  // iframe 状态管理
  const [iframeError, setIframeError] = useState(false);
  const [iframeLoaded, setIframeLoaded] = useState(false);

  // Refs
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // MatchWise AI 的 URL
  const MATCHWISE_URL = 'https://matchwise-ai.vercel.app';

  // 监听来自 MatchWise AI iframe 的消息
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 安全检查：只接受来自 MatchWise AI 的消息
      if (event.origin !== MATCHWISE_URL) {
        // 可选：在开发环境中记录被过滤的消息
        if (process.env.NODE_ENV === 'development') {
          console.debug('🚫 Message from unauthorized origin:', event.origin);
        }
        return;
      }

      // 开发环境日志
      if (process.env.NODE_ENV === 'development') {
        console.log('📨 Message received from MatchWise AI:', event.data.type, event.data);
      }

      // 处理登录状态更新
      if (event.data.type === 'loginStatus') {
        setMatchwiseLoginStatus({
          isLoggedIn: event.data.isLoggedIn,
          userInfo: event.data.userInfo,
        });
        if (process.env.NODE_ENV === 'development') {
          console.log('✅ Login status updated:', event.data.isLoggedIn ? 'Logged in' : 'Guest');
        }
      }

      // 处理登录成功通知
      if (event.data.type === 'loginSuccess') {
        setMatchwiseLoginStatus({
          isLoggedIn: true,
          userInfo: event.data.userInfo,
        });
        console.log('✅ User logged in to MatchWise:', event.data.userInfo);
      }

      // 处理登出通知
      if (event.data.type === 'logout') {
        setMatchwiseLoginStatus({
          isLoggedIn: false,
          userInfo: null,
        });
        if (process.env.NODE_ENV === 'development') {
          console.log('👋 User logged out from MatchWise');
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // 查询 MatchWise AI 的登录状态
  const checkMatchwiseLoginStatus = () => {
    if (iframeRef.current?.contentWindow) {
      const message = { action: 'getLoginStatus' };
      iframeRef.current.contentWindow.postMessage(message, MATCHWISE_URL);
      if (process.env.NODE_ENV === 'development') {
        console.log('📤 Sent message to MatchWise AI:', message);
      }
    } else {
      console.warn('⚠️ Cannot send message: iframe contentWindow not available');
    }
  };

  // 显示 MatchWise AI 登录弹窗
  const showMatchwiseLogin = (message?: string) => {
    if (iframeRef.current?.contentWindow) {
      const msg = { action: 'showLoginModal', message };
      iframeRef.current.contentWindow.postMessage(msg, MATCHWISE_URL);
      if (process.env.NODE_ENV === 'development') {
        console.log('📤 Sent message to MatchWise AI:', msg);
      }
    } else {
      console.warn('⚠️ Cannot show login modal: iframe contentWindow not available');
      // Fallback: 在新标签页中打开 MatchWise AI
      window.open(MATCHWISE_URL, '_blank');
    }
  };

  // 隐藏 MatchWise AI 的访客计数器
  const hideMatchwiseVisitorCounter = () => {
    if (iframeRef.current?.contentWindow) {
      const message = { action: 'hideVisitorCounter' };
      iframeRef.current.contentWindow.postMessage(message, MATCHWISE_URL);
      if (process.env.NODE_ENV === 'development') {
        console.log('📤 Sent message to MatchWise AI:', message);
      }
    }
  };

  // iframe 加载完成后初始化
  useEffect(() => {
    if (iframeLoaded && iframeRef.current?.contentWindow) {
      // iframe 加载完成后，延迟一点再发送消息以确保 iframe 内部已准备好
      const initTimer = setTimeout(() => {
        checkMatchwiseLoginStatus();
        hideMatchwiseVisitorCounter();
        console.log('✅ MatchWise AI iframe loaded, initialization messages sent');
      }, 500);

      return () => clearTimeout(initTimer);
    }
  }, [iframeLoaded]);

  // 设置加载超时 - 如果 15 秒后还没加载成功，显示错误
  useEffect(() => {
    const timeoutTimer = setTimeout(() => {
      if (!iframeLoaded) {
        setIframeError(true);
        console.warn('⚠️ MatchWise AI iframe failed to load within timeout (15s)');
      }
    }, 15000); // 15 秒超时

    return () => clearTimeout(timeoutTimer);
  }, [iframeLoaded]);



  return (
    <div
      className="min-h-screen flex"
      style={{
        backgroundImage: "url('/Job_Search_Pic.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
      }}
    >
      {/* Background Overlay */}
      <div className="fixed inset-0 bg-white/70" aria-hidden="true"></div>

      {/* ====== LEFT SIDEBAR ====== */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white/95 backdrop-blur-sm shadow-lg z-30 flex flex-col">
        {/* Logo / Website Name */}
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
              <Link
                href="/interview"
                className="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">🎤</span>
                Mock Interview
              </Link>
            </li>
            <li>
              <Link
                href="/dashboard"
                className="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">📊</span>
                My Dashboard
              </Link>
            </li>
            <li>
              <Link
                href="/admin/visitor-stats"
                className="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">📹</span>
                My Recordings
              </Link>
            </li>
          </ul>
        </nav>

        {/* User Info / Login Button */}
        <div className="p-4 border-t border-gray-200">
          {matchwiseLoginStatus?.isLoggedIn ? (
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-gray-500">👤</span>
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">{matchwiseLoginStatus.userInfo?.displayName || 'User'}</p>
                <p className="text-xs text-gray-400">{matchwiseLoginStatus.userInfo?.email || ''}</p>
              </div>
            </div>
          ) : (
            <button
              onClick={() => showMatchwiseLogin('Please sign in to access SmartSuccess.AI features')}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
            >
              Sign in to MatchWise
            </button>
          )}
          <div className="mt-4 text-xs text-gray-400 text-center">
            powered by <span className="font-semibold text-blue-600">SmartSuccess.AI</span>
          </div>
        </div>
      </aside>

      {/* ====== MAIN CONTENT (CENTER) - MATCHWISE AI IFRAME ====== */}
      <main className="flex-1 ml-64 mr-80 min-h-screen relative z-10">
        {iframeError ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center p-8 max-w-md">
              <div className="text-orange-500 mb-6">
                <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <p className="text-xl font-semibold mb-2">MatchWise AI Integration Pending</p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-gray-700 mb-3">
                  MatchWise AI needs to be configured to allow iframe embedding from SmartSuccess.AI.
                </p>
                <p className="text-sm text-gray-600">
                  This is a security feature that prevents websites from being embedded in other sites without permission.
                </p>
              </div>

              <div className="space-y-3">
                <a
                  href={MATCHWISE_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clipRule="evenodd" />
                    <path fillRule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clipRule="evenodd" />
                  </svg>
                  Open MatchWise AI (New Tab)
                </a>

                <p className="text-xs text-gray-500 text-center">
                  Use this temporary solution while integration is being configured
                </p>
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 font-medium mb-2">🔧 Technical Details:</p>
                <p className="text-xs text-blue-700">
                  MatchWise AI needs to configure CORS and Content-Security-Policy headers to allow iframe embedding from SmartSuccess.AI domain.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <>
            <iframe
              ref={iframeRef}
              src={MATCHWISE_URL}
              className="w-full h-full border-0"
              id="matchwise-iframe"
              title="MatchWise AI Resume Analysis"
              allow="camera; microphone; geolocation"
              sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
              style={{ minHeight: '100vh' }}
              onError={() => {
                console.error('❌ MatchWise AI iframe failed to load');
                setIframeError(true);
                setIframeLoaded(false);
              }}
              onLoad={() => {
                console.log('✅ MatchWise AI iframe loaded successfully');
                setIframeError(false);
                setIframeLoaded(true);
              }}
            />
          </>
        )}
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
            className="flex items-center justify-center w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-semibold rounded-full shadow-lg hover:from-purple-600 hover:to-indigo-600 transition-all transform hover:scale-105 text-sm"
          >
            <span className="mr-2">✨</span>
            View Comparison Demo
            <span className="ml-2">→</span>
          </Link>
          <p className="text-xs text-gray-500 mt-2 text-center">
            See what kind of analysis you&apos;ll get
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

        {/* MatchWise AI Status Display */}
        <div className="mt-auto pt-6 border-t border-gray-200">
          {matchwiseLoginStatus ? (
            <div className="matchwise-status p-3 bg-gray-50 rounded-lg">
              {matchwiseLoginStatus.isLoggedIn ? (
                <div>
                  <div className="flex items-center mb-2">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-2">
                      <span className="text-white text-xs">✓</span>
                    </div>
                    <p className="text-sm font-medium text-green-700">MatchWise Connected</p>
                  </div>
                  <p className="text-xs text-gray-600 truncate">
                    {matchwiseLoginStatus.userInfo?.displayName || matchwiseLoginStatus.userInfo?.email || 'User'}
                  </p>
                </div>
              ) : (
                <div>
                  <div className="flex items-center mb-2">
                    <div className="w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center mr-2">
                      <span className="text-white text-xs">○</span>
                    </div>
                    <p className="text-sm font-medium text-gray-600">MatchWise Guest</p>
                  </div>
                  <button
                    onClick={() => showMatchwiseLogin('Please sign in to MatchWise for full features')}
                    className="w-full py-2 px-3 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition"
                  >
                    Sign in to MatchWise
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 text-center">Connecting to MatchWise...</p>
            </div>
          )}
        </div>

      </aside>
    </div>
  );
}
