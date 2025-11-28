// resume-matcher-frontend/src/app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";

// ============ TYPE DEFINITIONS ============
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
  timestamp: string;
  activeListening: { score: number; insight: string };
  starScore: STARScore;
  strengths: string[];
  growthAreas: string[];
  delivery: {
    fillerWords: number;
    wordCount: number;
    speakingTime: number;
    pacing: string;
  };
}

interface SessionSummary {
  sessionId: string;
  date: string;
  overallScore: number;
  questionsCount: number;
  section: string;
}

interface UserAnalytics {
  totalSessions: number;
  averageScore: number;
  improvementTrend: number[];
  topStrengths: string[];
  focusAreas: string[];
  recentSessions: SessionSummary[];
}

// ============ MOCK DATA (Replace with API calls) ============
const mockAnalytics: UserAnalytics = {
  totalSessions: 8,
  averageScore: 72.5,
  improvementTrend: [58, 62, 65, 68, 71, 75, 78, 72],
  topStrengths: [
    "Clear communication style",
    "Relevant technical examples",
    "Professional demeanor",
    "Good use of STAR method",
  ],
  focusAreas: [
    "Quantify results with metrics",
    "Reduce filler words (um, like)",
    "Provide more specific examples",
    "Elaborate on leadership impact",
  ],
  recentSessions: [
    { sessionId: "s1", date: "2025-11-27", overallScore: 72, questionsCount: 5, section: "Technical" },
    { sessionId: "s2", date: "2025-11-25", overallScore: 78, questionsCount: 5, section: "Soft Skills" },
    { sessionId: "s3", date: "2025-11-23", overallScore: 75, questionsCount: 5, section: "Self-Intro" },
    { sessionId: "s4", date: "2025-11-20", overallScore: 71, questionsCount: 5, section: "Technical" },
    { sessionId: "s5", date: "2025-11-18", overallScore: 68, questionsCount: 5, section: "Soft Skills" },
  ],
};

// ============ SIMPLE CHART COMPONENT ============
function SimpleLineChart({ data, height = 120 }: { data: number[]; height?: number }) {
  if (!data.length) return null;
  
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 80 - 10;
    return `${x},${y}`;
  }).join(" ");

  return (
    <div style={{ height }} className="w-full relative">
      <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="none">
        {/* Grid lines */}
        <line x1="0" y1="25" x2="100" y2="25" stroke="#374151" strokeWidth="0.5" />
        <line x1="0" y1="50" x2="100" y2="50" stroke="#374151" strokeWidth="0.5" />
        <line x1="0" y1="75" x2="100" y2="75" stroke="#374151" strokeWidth="0.5" />
        
        {/* Line */}
        <polyline
          points={points}
          fill="none"
          stroke="#3B82F6"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Points */}
        {data.map((value, index) => {
          const x = (index / (data.length - 1)) * 100;
          const y = 100 - ((value - min) / range) * 80 - 10;
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="2"
              fill="#3B82F6"
            />
          );
        })}
      </svg>
      
      {/* Labels */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-1">
        <span>Session 1</span>
        <span>Session {data.length}</span>
      </div>
    </div>
  );
}

// ============ STAR RADAR CHART ============
function STARRadar({ scores }: { scores: { s: number; t: number; a: number; r: number } }) {
  const { s, t, a, r } = scores;
  const scale = (v: number) => (v / 5) * 40;
  
  // Calculate points for diamond shape
  const points = `
    50,${50 - scale(s)}
    ${50 + scale(t)},50
    50,${50 + scale(a)}
    ${50 - scale(r)},50
  `;

  return (
    <div className="w-32 h-32 relative">
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {/* Background grid */}
        {[1, 2, 3, 4, 5].map((level) => (
          <polygon
            key={level}
            points={`50,${50 - level * 8} ${50 + level * 8},50 50,${50 + level * 8} ${50 - level * 8},50`}
            fill="none"
            stroke="#374151"
            strokeWidth="0.5"
          />
        ))}
        
        {/* Axes */}
        <line x1="50" y1="10" x2="50" y2="90" stroke="#4B5563" strokeWidth="0.5" />
        <line x1="10" y1="50" x2="90" y2="50" stroke="#4B5563" strokeWidth="0.5" />
        
        {/* Data polygon */}
        <polygon
          points={points}
          fill="rgba(59, 130, 246, 0.3)"
          stroke="#3B82F6"
          strokeWidth="2"
        />
        
        {/* Labels */}
        <text x="50" y="8" textAnchor="middle" className="text-xs fill-gray-400">S</text>
        <text x="92" y="53" textAnchor="start" className="text-xs fill-gray-400">T</text>
        <text x="50" y="98" textAnchor="middle" className="text-xs fill-gray-400">A</text>
        <text x="8" y="53" textAnchor="end" className="text-xs fill-gray-400">R</text>
      </svg>
    </div>
  );
}

// ============ MAIN DASHBOARD COMPONENT ============
export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [userId] = useState("demo-user"); // Replace with Firebase auth

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://smartsuccess-backend.onrender.com";

  useEffect(() => {
    // Fetch analytics from backend
    const fetchAnalytics = async () => {
      try {
        // Uncomment when backend is ready:
        // const res = await fetch(`${BACKEND_URL}/api/interview/analytics/${userId}`);
        // const data = await res.json();
        // setAnalytics(data);
        
        // Using mock data for now
        setTimeout(() => {
          setAnalytics(mockAnalytics);
          setLoading(false);
        }, 500);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
        setAnalytics(mockAnalytics);
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Loading your analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-4">No interview data yet</p>
          <a href="/interview" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Start Your First Interview
          </a>
        </div>
      </div>
    );
  }

  // Calculate average STAR scores from recent sessions (mock)
  const avgSTAR = { s: 3.8, t: 3.5, a: 4.0, r: 3.2 };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Interview Analytics</h1>
            <p className="text-gray-500">Track your mock interview progress</p>
          </div>
          <div className="flex gap-3">
            <a href="/" className="px-4 py-2 border rounded-lg hover:bg-gray-50">
              ← Home
            </a>
            <a href="/interview" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              🎤 New Interview
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Total Sessions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Sessions</p>
                <p className="text-3xl font-bold text-gray-800">{analytics.totalSessions}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">🎯</span>
              </div>
            </div>
          </div>

          {/* Average Score */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Average Score</p>
                <p className="text-3xl font-bold text-blue-600">{analytics.averageScore}%</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>

          {/* Improvement */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Improvement</p>
                <p className="text-3xl font-bold text-green-600">
                  +{analytics.improvementTrend[analytics.improvementTrend.length - 1] - analytics.improvementTrend[0]}%
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">📈</span>
              </div>
            </div>
          </div>

          {/* Questions Practiced */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Questions Practiced</p>
                <p className="text-3xl font-bold text-gray-800">{analytics.totalSessions * 5}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">💬</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Progress Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Score Progress Over Time</h2>
            <SimpleLineChart data={analytics.improvementTrend} height={200} />
            <div className="mt-4 flex justify-center gap-8 text-sm text-gray-500">
              <span>Started: {analytics.improvementTrend[0]}%</span>
              <span>Current: {analytics.improvementTrend[analytics.improvementTrend.length - 1]}%</span>
            </div>
          </div>

          {/* STAR Breakdown */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">STAR Method Scores</h2>
            <div className="flex justify-center mb-4">
              <STARRadar scores={avgSTAR} />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Situation</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(avgSTAR.s / 5) * 100}%` }}></div>
                  </div>
                  <span className="text-sm font-medium w-8">{avgSTAR.s}/5</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Task</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(avgSTAR.t / 5) * 100}%` }}></div>
                  </div>
                  <span className="text-sm font-medium w-8">{avgSTAR.t}/5</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Action</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(avgSTAR.a / 5) * 100}%` }}></div>
                  </div>
                  <span className="text-sm font-medium w-8">{avgSTAR.a}/5</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Result</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(avgSTAR.r / 5) * 100}%` }}></div>
                  </div>
                  <span className="text-sm font-medium w-8">{avgSTAR.r}/5</span>
                </div>
              </div>
            </div>
          </div>

          {/* Strengths */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="text-green-500">✅</span> Your Strengths
            </h2>
            <ul className="space-y-3">
              {analytics.topStrengths.map((strength, i) => (
                <li key={i} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <span className="text-green-500 mt-0.5">•</span>
                  <span className="text-sm text-green-800">{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Focus Areas */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="text-orange-500">🌱</span> Areas to Improve
            </h2>
            <ul className="space-y-3">
              {analytics.focusAreas.map((area, i) => (
                <li key={i} className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
                  <span className="text-orange-500 mt-0.5">•</span>
                  <span className="text-sm text-orange-800">{area}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recent Sessions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Sessions</h2>
            <div className="space-y-3">
              {analytics.recentSessions.map((session) => (
                <div
                  key={session.sessionId}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                >
                  <div>
                    <p className="font-medium text-gray-800">{session.section}</p>
                    <p className="text-sm text-gray-500">{session.date}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      session.overallScore >= 75 ? "text-green-600" :
                      session.overallScore >= 60 ? "text-blue-600" : "text-orange-600"
                    }`}>
                      {session.overallScore}%
                    </p>
                    <p className="text-xs text-gray-500">{session.questionsCount} questions</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg text-sm font-medium">
              View All Sessions →
            </button>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <h2 className="text-xl font-bold mb-4">💡 Personalized Tips</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Improve Your Results</h3>
              <p className="text-sm text-blue-100">
                Your "Result" score is lowest. Try ending each answer with specific metrics or outcomes.
              </p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Practice More Technical</h3>
              <p className="text-sm text-blue-100">
                You've done well in soft skills. Challenge yourself with more technical questions.
              </p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Keep the Momentum</h3>
              <p className="text-sm text-blue-100">
                You've improved {analytics.improvementTrend[analytics.improvementTrend.length - 1] - analytics.improvementTrend[0]}% since starting. Aim for 80% by your next session!
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>SmartSuccess.AI - Your AI-Powered Interview Coach</p>
        </div>
      </footer>
    </div>
  );
}
