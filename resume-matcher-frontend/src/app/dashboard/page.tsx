// resume-matcher-frontend/src/app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

// ============ TYPE DEFINITIONS ============
interface SessionHistory {
  sessionId: string;
  date: string;
  score: number;
  questionsAnswered: number;
}

interface Analytics {
  totalSessions: number;
  averageScore: number;
  improvementTrend: number[];
  topStrengths: string[];
  focusAreas: string[];
}

// ============ MAIN COMPONENT ============
export default function DashboardPage() {
  const [userId] = useState("user_" + Math.random().toString(36).substr(2, 9));
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [sessions, setSessions] = useState<SessionHistory[]>([]);
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/interview/analytics/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.log("Could not fetch analytics:", error);
      // Set mock data for demo
      setAnalytics({
        totalSessions: 0,
        averageScore: 0,
        improvementTrend: [],
        topStrengths: [],
        focusAreas: []
      });
    } finally {
      setLoading(false);
    }
  };

  // Generate score color based on value
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              SmartSuccess.AI
            </Link>
            <span className="text-gray-400">|</span>
            <h1 className="text-xl font-semibold text-gray-800">My Dashboard</h1>
          </div>
          <Link
            href="/interview"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Start New Interview
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-sm p-6 border">
                <div className="text-sm text-gray-500 mb-1">Total Sessions</div>
                <div className="text-3xl font-bold text-gray-800">
                  {analytics?.totalSessions || 0}
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border">
                <div className="text-sm text-gray-500 mb-1">Average Score</div>
                <div className={`text-3xl font-bold ${getScoreColor(analytics?.averageScore || 0)}`}>
                  {analytics?.averageScore || 0}%
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border">
                <div className="text-sm text-gray-500 mb-1">Top Strength</div>
                <div className="text-lg font-semibold text-green-600">
                  {analytics?.topStrengths?.[0] || "Complete an interview to see"}
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border">
                <div className="text-sm text-gray-500 mb-1">Focus Area</div>
                <div className="text-lg font-semibold text-orange-600">
                  {analytics?.focusAreas?.[0] || "Complete an interview to see"}
                </div>
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Progress Chart */}
              <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6 border">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Score Progress</h2>
                {analytics?.improvementTrend && analytics.improvementTrend.length > 0 ? (
                  <div className="h-64 flex items-end gap-2">
                    {analytics.improvementTrend.map((score, index) => (
                      <div
                        key={index}
                        className={`flex-1 ${getScoreBg(score)} rounded-t-lg transition-all hover:opacity-80`}
                        style={{ height: `${score}%` }}
                        title={`Session ${index + 1}: ${score}%`}
                      >
                        <div className="text-center text-xs pt-1 font-medium text-gray-600">
                          {score}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <p className="text-lg mb-2">No interview data yet</p>
                      <Link
                        href="/interview"
                        className="text-blue-600 hover:underline"
                      >
                        Start your first interview →
                      </Link>
                    </div>
                  </div>
                )}
              </div>

              {/* Strengths & Growth Areas */}
              <div className="space-y-6">
                {/* Strengths */}
                <div className="bg-white rounded-xl shadow-sm p-6 border">
                  <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span className="text-green-500">✓</span> Top Strengths
                  </h2>
                  {analytics?.topStrengths && analytics.topStrengths.length > 0 ? (
                    <ul className="space-y-2">
                      {analytics.topStrengths.map((strength, index) => (
                        <li
                          key={index}
                          className="flex items-center gap-2 text-gray-700"
                        >
                          <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400 text-sm">
                      Complete interviews to discover your strengths
                    </p>
                  )}
                </div>

                {/* Growth Areas */}
                <div className="bg-white rounded-xl shadow-sm p-6 border">
                  <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span className="text-orange-500">↗</span> Focus Areas
                  </h2>
                  {analytics?.focusAreas && analytics.focusAreas.length > 0 ? (
                    <ul className="space-y-2">
                      {analytics.focusAreas.map((area, index) => (
                        <li
                          key={index}
                          className="flex items-center gap-2 text-gray-700"
                        >
                          <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                          {area}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400 text-sm">
                      Complete interviews to identify growth areas
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Session History */}
            <div className="mt-8 bg-white rounded-xl shadow-sm p-6 border">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Sessions</h2>
              {sessions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b text-left text-gray-500 text-sm">
                        <th className="pb-3">Date</th>
                        <th className="pb-3">Questions</th>
                        <th className="pb-3">Score</th>
                        <th className="pb-3">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sessions.map((session) => (
                        <tr key={session.sessionId} className="border-b last:border-0">
                          <td className="py-3">{session.date}</td>
                          <td className="py-3">{session.questionsAnswered}</td>
                          <td className="py-3">
                            <span
                              className={`px-2 py-1 rounded-full text-sm font-medium ${getScoreBg(
                                session.score
                              )} ${getScoreColor(session.score)}`}
                            >
                              {session.score}%
                            </span>
                          </td>
                          <td className="py-3">
                            <button className="text-blue-600 hover:underline text-sm">
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <p className="mb-2">No interview sessions yet</p>
                  <Link
                    href="/interview"
                    className="text-blue-600 hover:underline"
                  >
                    Start your first mock interview →
                  </Link>
                </div>
              )}
            </div>

            {/* Tips Section */}
            <div className="mt-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-sm p-6 text-white">
              <h2 className="text-lg font-semibold mb-4">💡 Interview Tips</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/10 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Use STAR Method</h3>
                  <p className="text-sm text-white/80">
                    Structure your answers with Situation, Task, Action, and Result for maximum impact.
                  </p>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Be Specific</h3>
                  <p className="text-sm text-white/80">
                    Include numbers, metrics, and concrete examples to make your answers memorable.
                  </p>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Practice Regularly</h3>
                  <p className="text-sm text-white/80">
                    Consistent practice builds confidence. Aim for 2-3 mock interviews per week.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          © 2025 SmartSuccess.AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

