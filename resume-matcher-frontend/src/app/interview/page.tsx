// resume-matcher-frontend/src/app/interview/page.tsx
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
// GPU Enhancement imports
import { routedFetch } from "../utils/requestRouter";
import { useGPUBackend } from "../hooks/useGPUBackend";
import { GPUStatusBadge } from "../components/GPUStatusIndicator";

// ============ WEB SPEECH API TYPE DECLARATIONS ============
// These types are needed for TypeScript to recognize the Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: Event) => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor;
    webkitSpeechRecognition: SpeechRecognitionConstructor;
  }
}

// ============ TYPE DEFINITIONS ============
interface UserInfo {
  displayName?: string;
  email?: string;
  photoURL?: string;
}

interface MatchwiseLoginStatus {
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface STARScore {
  situation: number;
  task: number;
  action: number;
  result: number;
  average: number;
}

interface QuestionFeedback {
  question: string;
  response: string;
  activeListening: { score: number; insight: string };
  starScore: STARScore;
  strengths: string[];
  growthAreas: string[];
}

interface SessionFeedback {
  overallScore: number;
  questionsFeedback: QuestionFeedback[];
  aggregatedStrengths: string[];
  aggregatedGrowthAreas: string[];
}

// ============ MAIN COMPONENT ============
export default function InterviewPage() {
  // State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [inputText, setInputText] = useState("");
  const [feedback, setFeedback] = useState<SessionFeedback | null>(null);
  const [activeTab, setActiveTab] = useState<"coaching" | "analytics">("coaching");
  const [userId] = useState("demo-user"); // Replace with Firebase auth
  const [matchwiseLoginStatus, setMatchwiseLoginStatus] = useState<MatchwiseLoginStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 从 localStorage 加载登录状态
  useEffect(() => {
    const savedStatus = localStorage.getItem('matchwiseLoginStatus');
    if (savedStatus) {
      try {
        const parsed = JSON.parse(savedStatus);
        setMatchwiseLoginStatus(parsed);
      } catch (e) {
        console.error('Failed to parse saved login status:', e);
      }
    }

    // 监听 localStorage 变化（跨标签页同步）
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'matchwiseLoginStatus') {
        try {
          const parsed = e.newValue ? JSON.parse(e.newValue) : null;
          setMatchwiseLoginStatus(parsed);
        } catch (e) {
          console.error('Failed to parse login status from storage event:', e);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Refs
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionIdRef = useRef<string | null>(null); // Keep latest sessionId for speech recognition callback
  const pendingTranscriptRef = useRef<string>(""); // Store transcript to send

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://smartsuccess-ai.onrender.com";
  
  // GPU Backend hook (optional - for enhanced features)
  const { gpuAvailable } = useGPUBackend({
    autoCheck: true,
    checkInterval: 30000
  });

  // Keep sessionIdRef in sync with sessionId state
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  // ============ SPEECH RECOGNITION SETUP ============
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;

        recognitionRef.current.onresult = (event) => {
          let interimTranscript = "";
          let finalTranscript = "";

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const t = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += t;
            } else {
              interimTranscript += t;
            }
          }

          // Update display transcript
          setTranscript(finalTranscript || interimTranscript);

          // When we get a final transcript, store it for sending
          if (finalTranscript) {
            console.log("Final transcript captured:", finalTranscript);
            pendingTranscriptRef.current = finalTranscript;
          }
        };

        recognitionRef.current.onerror = (event) => {
          console.error("Speech recognition error:", event);
          setIsListening(false);
        };

        // When recognition ends (user stops speaking), send the message
        recognitionRef.current.onend = () => {
          console.log("Speech recognition ended");
          if (pendingTranscriptRef.current && sessionIdRef.current) {
            const textToSend = pendingTranscriptRef.current;
            pendingTranscriptRef.current = ""; // Clear pending
            setTranscript("");
            // Use setTimeout to ensure state is updated
            setTimeout(() => {
              sendMessageToBackend(textToSend);
            }, 100);
          }
          setIsListening(false);
        };
      }
      synthRef.current = window.speechSynthesis;
    }
  }, [sendMessageToBackend]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ============ INTERVIEW FUNCTIONS ============
  const startInterview = async () => {
    setIsLoading(true);
    setError(null); // Clear previous errors
    
    try {
      const formData = new FormData();
      formData.append("user_id", userId);

      console.log("🚀 Starting interview...", { BACKEND_URL, userId, gpuAvailable });

      // Use routedFetch for automatic GPU/Render routing
      const res = await routedFetch("/api/interview/start", {
        method: "POST",
        body: formData,
      }, {
        preferGPU: false, // Interview start can use either backend
        fallbackToRender: true
      });

      console.log("📡 Response status:", res.status, res.statusText);

      // Check if response is ok
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ error: `HTTP ${res.status}: ${res.statusText}` }));
        const errorMessage = errorData.error || `Failed to start interview: ${res.status} ${res.statusText}`;
        console.error("❌ API Error:", errorMessage);
        setError(errorMessage);
        setIsLoading(false);
        return;
      }

      const data = await res.json();
      console.log("✅ Interview started successfully:", data);

      // Check if response contains error (even with 200 status)
      if (data.error) {
        console.error("❌ Backend error:", data.error);
        setError(data.error);
        setIsLoading(false);
        return;
      }

      // Validate required fields
      if (!data.session_id || !data.message) {
        const errorMsg = "Invalid response from server: missing session_id or message";
        console.error("❌", errorMsg, data);
        setError(errorMsg);
        setIsLoading(false);
        return;
      }

      // Success - update state
      setSessionId(data.session_id);
      sessionIdRef.current = data.session_id; // Sync ref
      
      const welcomeMsg: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages([welcomeMsg]);
      speak(data.message);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to start interview. Please check your connection and try again.";
      console.error("❌ Failed to start:", error);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to send message to backend - uses refs for speech recognition callback
  const sendMessageToBackend = useCallback(async (text: string) => {
    const currentSessionId = sessionIdRef.current;
    if (!currentSessionId || !text.trim()) {
      console.log("Cannot send: sessionId=", currentSessionId, "text=", text);
      return;
    }

    console.log("Sending message to backend:", text);

    const userMsg: Message = {
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("session_id", currentSessionId);
      formData.append("message", text);

      // Use routedFetch for automatic GPU/Render routing
      const res = await routedFetch("/api/interview/message", {
        method: "POST",
        body: formData,
      }, {
        preferGPU: false, // Interview messages can use either backend
        fallbackToRender: true
      });

      // Check if response is ok
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ error: `HTTP ${res.status}: ${res.statusText}` }));
        const errorMessage = errorData.error || `Failed to send message: ${res.status} ${res.statusText}`;
        console.error("❌ API Error:", errorMessage);
        setError(errorMessage);
        
        // Show error message to user
        const errorMsg: Message = {
          role: "assistant",
          content: `I apologize, but I encountered an error: ${errorMessage}. Please try again or say "STOP" to return to the menu.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, errorMsg]);
        setIsLoading(false);
        return;
      }

      const data = await res.json();

      console.log("Backend response:", data);

      // Check if response contains error (even with 200 status)
      if (data.error) {
        console.error("❌ Backend error:", data.error);
        setError(data.error);
        const errorMsg: Message = {
          role: "assistant",
          content: `I apologize, but I encountered an error: ${data.error}. Please try again or say "STOP" to return to the menu.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, errorMsg]);
        setIsLoading(false);
        return;
      }

      // Validate required fields
      if (!data.response) {
        const errorMsg = "Invalid response from server: missing response field";
        console.error("❌", errorMsg, data);
        setError(errorMsg);
        setIsLoading(false);
        return;
      }

      // Clear any previous errors on successful response
      setError(null);

      const assistantMsg: Message = {
        role: "assistant",
        content: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      speak(data.response);

      // Update feedback if provided (individual question feedback)
      // Only process feedback if it exists and has required fields
      if (data.feedback && typeof data.feedback === 'object') {
        console.log("Question feedback received:", data.feedback);
        // Update with session feedback if available, otherwise create from individual feedback
        if (data.session_feedback && typeof data.session_feedback === 'object') {
          setFeedback(data.session_feedback);
        } else {
          // Create a session feedback structure from individual feedback
          // Safely access properties with default values
          setFeedback((prevFeedback) => {
            const strengths = Array.isArray(data.feedback.strengths) ? data.feedback.strengths : [];
            const growthAreas = Array.isArray(data.feedback.growthAreas) ? data.feedback.growthAreas : [];
            
            const newQuestionFeedback = {
              question: data.feedback.question || "Question",
              response: data.feedback.response || text,
              activeListening: data.feedback.activeListening || { score: 0, insight: "No feedback available" },
              starScore: data.feedback.starScore || { situation: 0, task: 0, action: 0, result: 0, average: 0 },
              strengths: strengths,
              growthAreas: growthAreas,
            };
            
            if (prevFeedback) {
              const prevStrengths = Array.isArray(prevFeedback.aggregatedStrengths) ? prevFeedback.aggregatedStrengths : [];
              const prevGrowthAreas = Array.isArray(prevFeedback.aggregatedGrowthAreas) ? prevFeedback.aggregatedGrowthAreas : [];
              
              return {
                ...prevFeedback,
                questionsFeedback: [...prevFeedback.questionsFeedback, newQuestionFeedback],
                aggregatedStrengths: [...new Set([...prevStrengths, ...strengths])].slice(0, 5),
                aggregatedGrowthAreas: [...new Set([...prevGrowthAreas, ...growthAreas])].slice(0, 5),
                overallScore: data.feedback.starScore?.average ? (data.feedback.starScore.average / 5) * 100 : prevFeedback.overallScore,
              };
            } else {
              return {
                overallScore: data.feedback.starScore?.average ? (data.feedback.starScore.average / 5) * 100 : 0,
                questionsFeedback: [newQuestionFeedback],
                aggregatedStrengths: strengths,
                aggregatedGrowthAreas: growthAreas,
              };
            }
          });
        }
      }
      
      // If session feedback is provided separately
      if (data.session_feedback && typeof data.session_feedback === 'object') {
        console.log("Session feedback received:", data.session_feedback);
        setFeedback(data.session_feedback);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send message. Please check your connection and try again.";
      console.error("❌ Message failed:", error);
      setError(errorMessage);
      
      // Show error message to user
      const errorMsg: Message = {
        role: "assistant",
        content: `I apologize, but I encountered an error: ${errorMessage}. Please try again or say "STOP" to return to the menu.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
    setIsLoading(false);
  }, []);

  // Wrapper for form submission (uses state)
  const handleSendMessage = async (text: string) => {
    if (!sessionId || !text.trim()) return;
    await sendMessageToBackend(text);
  };

  const speak = (text: string) => {
    if (!synthRef.current) return;
    synthRef.current.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    synthRef.current.speak(utterance);
  };

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const copyTranscript = () => {
    const text = messages
      .map((m) => `[${m.timestamp}] ${m.role === "user" ? "You" : "AI"}: ${m.content}`)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    alert("Transcript copied!");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      handleSendMessage(inputText);
      setInputText("");
    }
  };

  // ============ RENDER ============
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* ====== LEFT SIDEBAR ====== */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white/95 backdrop-blur-sm shadow-lg z-30 flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
            SmartSuccess.AI
          </h1>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <Link
                href="/"
                className="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <span className="mr-3">🏠</span>
                Home
              </Link>
            </li>
            <li>
              <Link
                href="/interview"
                className="flex items-center px-4 py-3 text-gray-700 bg-blue-50 rounded-lg font-medium"
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
            <Link
              href="/?login=true"
              className="block w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm text-center"
            >
              Guest User Sign In
            </Link>
          )}
          <div className="mt-4 text-xs text-gray-400 text-center">
            powered by <span className="font-semibold text-blue-600">SmartSuccess.AI</span>
          </div>
        </div>
      </aside>

      {/* ====== MAIN CONTENT ====== */}
      <main className="flex-1 ml-64 flex">
        {/* ====== CHAT PANEL ====== */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-white border-b px-6 py-4 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold">Mock Interview Session</h2>
              <p className="text-sm text-gray-500">
                {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
              </p>
            </div>
            <div className="flex gap-2 items-center">
              <GPUStatusBadge className="mr-2" />
              <span className="px-3 py-1 bg-gray-100 rounded-full text-sm">⭐ Not shared</span>
              <button className="px-4 py-1 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                Share
              </button>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
            {!sessionId ? (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="text-6xl mb-6">🎤</div>
                <h2 className="text-2xl font-bold mb-4">Ready for Mock Interview?</h2>
                <p className="text-gray-500 mb-6 text-center max-w-md">
                  Practice answering interview questions with AI feedback based on the STAR method.
                </p>
                {error && (
                  <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg max-w-md w-full">
                    <div className="flex items-start">
                      <span className="text-red-600 mr-2">⚠️</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-800">Error</p>
                        <p className="text-sm text-red-700 mt-1">{error}</p>
                        <button
                          onClick={() => {
                            setError(null);
                            startInterview();
                          }}
                          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                        >
                          Try Again
                        </button>
                      </div>
                    </div>
                  </div>
                )}
                <button
                  onClick={startInterview}
                  disabled={isLoading}
                  className="px-8 py-4 bg-blue-600 text-white rounded-xl text-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <span className="animate-spin mr-2">⏳</span>
                      Starting...
                    </span>
                  ) : (
                    "Start Interview"
                  )}
                </button>
                {process.env.NODE_ENV === 'development' && (
                  <div className="mt-4 text-xs text-gray-400 space-y-1">
                    <p>Backend: {BACKEND_URL}</p>
                    <p>GPU Status: {gpuAvailable ? '✅ Available' : '❌ Unavailable'}</p>
                  </div>
                )}
              </div>
            ) : (
              messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[70%] p-4 rounded-2xl ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-white shadow-sm rounded-bl-sm"
                    }`}
                  >
                    <p className="text-xs opacity-60 mb-1">{msg.timestamp}</p>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Transcript Section */}
          {sessionId && messages.length > 0 && (
            <div className="bg-white border-t p-4 max-h-48 overflow-y-auto">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-sm text-gray-600">TRANSCRIPT</h3>
                <button
                  onClick={copyTranscript}
                  className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                >
                  📋 Copy transcript
                </button>
              </div>
              <div className="space-y-2 text-sm">
                {messages.map((m, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-gray-400">{m.timestamp}</span>
                    <span className={m.role === "user" ? "text-blue-600" : "text-gray-800"}>
                      {m.role === "user" ? "You:" : "🤖"} {m.content.slice(0, 80)}...
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Voice Controls */}
          {sessionId && (
            <div className="bg-white border-t p-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={toggleListening}
                  className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                    isListening ? "bg-red-500 animate-pulse" : "bg-blue-600 hover:bg-blue-700"
                  }`}
                >
                  <span className="text-white text-xl">{isListening ? "🔴" : "🎤"}</span>
                </button>

                <form onSubmit={handleSubmit} className="flex-1 flex gap-2">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={transcript || "Type or speak your response..."}
                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoading ? "..." : "Send"}
                  </button>
                </form>
              </div>

              {(isListening || isSpeaking) && (
                <p className="text-center text-sm mt-2">
                  {isListening && <span className="text-red-500">🎙️ Listening...</span>}
                  {isSpeaking && <span className="text-blue-500">🔊 Speaking...</span>}
                </p>
              )}
            </div>
          )}
        </div>

        {/* ====== FEEDBACK PANEL ====== */}
        <aside className="w-80 bg-white border-l overflow-y-auto">
          {/* Session Status */}
          <div className="p-4 border-b">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🎭</span>
              <span className="font-semibold">Roleplay {feedback ? "complete" : "in progress"}</span>
            </div>
            {feedback && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Your score was</span>
                <span className="text-2xl font-bold text-blue-600">{feedback.overallScore}%</span>
              </div>
            )}
            <button className="mt-3 w-full py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50">
              Practice Again
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("coaching")}
              className={`flex-1 py-3 text-sm font-medium ${
                activeTab === "coaching" ? "border-b-2 border-blue-600 text-blue-600" : "text-gray-500"
              }`}
            >
              💬 Coaching {feedback && `(${feedback.questionsFeedback.length})`}
            </button>
            <button
              onClick={() => setActiveTab("analytics")}
              className={`flex-1 py-3 text-sm font-medium ${
                activeTab === "analytics" ? "border-b-2 border-blue-600 text-blue-600" : "text-gray-500"
              }`}
            >
              📊 Analytics
            </button>
          </div>

          {/* Rubric Section */}
          <div className="p-4 border-b">
            <h3 className="font-semibold mb-3">Rubric</h3>

            {/* Active Listening */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">👂 Active Listening</span>
                <span className="text-sm font-bold">{feedback?.questionsFeedback[0]?.activeListening.score || "-"}/5</span>
              </div>
              <p className="text-xs text-gray-500">
                {feedback?.questionsFeedback[0]?.activeListening.insight || "Waiting for responses..."}
              </p>
            </div>

            {/* STAR Scores */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">⭐ Use STAR</span>
                <span className="text-sm font-bold">
                  {feedback?.questionsFeedback[0]?.starScore.average.toFixed(1) || "-"}/5
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between">
                  <span>Situation:</span>
                  <span className="font-medium">{feedback?.questionsFeedback[0]?.starScore.situation || "-"}/5</span>
                </div>
                <div className="flex justify-between">
                  <span>Task:</span>
                  <span className="font-medium">{feedback?.questionsFeedback[0]?.starScore.task || "-"}/5</span>
                </div>
                <div className="flex justify-between">
                  <span>Action:</span>
                  <span className="font-medium">{feedback?.questionsFeedback[0]?.starScore.action || "-"}/5</span>
                </div>
                <div className="flex justify-between">
                  <span>Result:</span>
                  <span className="font-medium">{feedback?.questionsFeedback[0]?.starScore.result || "-"}/5</span>
                </div>
              </div>
            </div>
          </div>

          {/* Feedback Section */}
          <div className="p-4">
            <h3 className="font-semibold mb-3">Feedback</h3>

            {/* Strengths */}
            <div className="mb-4 p-3 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-600">✅</span>
                <span className="text-sm font-medium text-green-700">Strength</span>
              </div>
              {feedback?.aggregatedStrengths.length ? (
                feedback.aggregatedStrengths.map((s, i) => (
                  <p key={i} className="text-sm text-green-700 mb-1">• {s}</p>
                ))
              ) : (
                <p className="text-sm text-gray-500">Complete questions to see strengths</p>
              )}
            </div>

            {/* Growth Areas */}
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-orange-600">🌱</span>
                <span className="text-sm font-medium text-orange-700">Growth Area</span>
              </div>
              {feedback?.aggregatedGrowthAreas.length ? (
                feedback.aggregatedGrowthAreas.map((g, i) => (
                  <p key={i} className="text-sm text-orange-700 mb-1">• {g}</p>
                ))
              ) : (
                <p className="text-sm text-gray-500">Complete questions to see growth areas</p>
              )}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
