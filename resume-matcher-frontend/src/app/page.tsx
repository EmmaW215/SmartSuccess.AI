// ============================================================
// FILE: resume-matcher-frontend/src/app/page.tsx
// FULL REPLACEMENT - Copy this entire file
// ============================================================

'use client';

import React, { useState, useRef } from 'react';
import Link from 'next/link';
import SimpleVisitorCounter from './components/SimpleVisitorCounter';
import ReactMarkdown from 'react-markdown';

interface ComparisonResponse {
  job_summary: string;
  resume_summary: string;
  match_score: number;
  tailored_resume_summary: string;
  tailored_work_experience: string[];
  cover_letter: string;
}

export default function Home() {
  const [jobUrl, setJobUrl] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<ComparisonResponse | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
      setError('');
    }
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResumeFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleButtonClick = () => {
    inputRef.current?.click();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!jobUrl || !resumeFile) {
      alert('Please provide both job description and resume.');
      return;
    }

    const formData = new FormData();
    formData.append('job_url', jobUrl);
    formData.append('resume', resumeFile);

    setLoading(true);
    setError('');
    setResponse(null);

    try {
      const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://resume-matcher-backend-rrrw.onrender.com';
      const response = await fetch(`${BACKEND_URL}/api/compare`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch comparison');
      }
      const data = await response.json();
      setResponse(data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      if (errorMessage.includes('xAI API error: 403')) {
        setError('Unable to process due to insufficient xAI API credits. Please contact support.');
      } else if (errorMessage.includes('Failed to fetch job posting')) {
        setError('The job posting URL is not accessible. Try a LinkedIn or company career page URL.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

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
                <span className="mr-3">📁</span>
                My Records
              </Link>
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

        {/* User Info / Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-gray-500">👤</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Guest User</p>
              <p className="text-xs text-gray-400">Login coming soon</p>
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-400 text-center">
            powered by <span className="font-semibold text-blue-600">SmartSuccess.AI</span>
          </div>
        </div>
      </aside>

      {/* ====== MAIN CONTENT (CENTER) ====== */}
      <main className="flex-1 ml-64 mr-80 min-h-screen relative z-10 p-6 overflow-y-auto">
        <div className="max-w-2xl mx-auto">
          {/* Input Form */}
          <form
            className="bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-8 flex flex-col gap-6 border border-gray-100"
            onSubmit={handleSubmit}
          >
            <div>
              <label htmlFor="jobUrl" className="block text-sm font-semibold text-gray-700 mb-2">
                Job Description
              </label>
              <textarea
                id="jobUrl"
                required
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="Please paste the full job description here"
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y text-gray-700"
              />
            </div>
            
            <div
              className={`w-full border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
                dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50'
              }`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={handleButtonClick}
            >
              <input
                id="resume"
                type="file"
                accept=".pdf,.doc,.docx"
                required
                ref={inputRef}
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex flex-col items-center justify-center gap-2">
                <span className="text-gray-700 font-medium">Upload Resume (PDF or DOCX)</span>
                <span className="text-xs text-gray-400">Drag & drop or click to select file</span>
                {resumeFile && <span className="text-green-600 text-sm mt-2">{resumeFile.name}</span>}
              </div>
            </div>
            
            {error && <div className="text-red-500 text-sm">{error}</div>}
            {loading && <div className="text-blue-600 text-sm text-center">Processing your request...</div>}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow transition disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating...' : 'Generate Comparison'}
            </button>
          </form>

          {/* ====== ANALYSIS RESULTS OUTPUT ====== */}
          {response && (
            <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-8 mt-6 border border-blue-100 flex flex-col gap-8 animate-fade-in">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Analysis Results</h2>

              {/* Job Requirement Summary */}
              <div className="mb-6">
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-blue-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Job Requirement Summary</span>
                </div>
                <p className="text-gray-700 text-base ml-5">{response.job_summary || 'No job summary available.'}</p>
              </div>

              {/* Resume - Job Posting Comparison */}
              <div className="mb-6">
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-purple-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Resume - Job Posting Comparison</span>
                </div>
                <div className="ml-5">
                  <ReactMarkdown>{response.resume_summary}</ReactMarkdown>
                </div>
              </div>

              {/* Match Score */}
              <div className="mb-6">
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-green-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Match Score</span>
                </div>
                <div className="flex items-center ml-5 mb-2">
                  <span className="text-3xl font-bold text-green-600 mr-4">{response.match_score || 0}%</span>
                  <div className="flex-1 h-3 bg-gray-200 rounded">
                    <div
                      className="h-3 bg-green-500 rounded"
                      style={{ width: `${response.match_score || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Tailored Resume Summary */}
              <div className="mb-6">
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-purple-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Tailored Resume Summary</span>
                </div>
                <p className="text-gray-700 text-base ml-5">{response.tailored_resume_summary || 'No tailored resume summary available.'}</p>
              </div>

              {/* Tailored Resume Work Experience */}
              <div className="mb-6">
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-orange-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Tailored Resume Work Experience</span>
                </div>
                <ul className="list-disc list-inside text-gray-700 text-base ml-5 space-y-1">
                  {response.tailored_work_experience && response.tailored_work_experience.length > 0 ? (
                    response.tailored_work_experience.map((item: string, index: number) => (
                      <li key={index} dangerouslySetInnerHTML={{ __html: item }}></li>
                    ))
                  ) : (
                    <li>No tailored work experience provided.</li>
                  )}
                </ul>
              </div>

              {/* Cover Letter */}
              <div>
                <div className="flex items-center mb-2">
                  <div className="w-1.5 h-7 bg-teal-500 rounded mr-3"></div>
                  <span className="text-lg font-semibold text-gray-800">Cover Letter</span>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 ml-5">
                  <p className="text-gray-700 text-base whitespace-pre-wrap">{response.cover_letter || 'No cover letter available.'}</p>
                </div>
              </div>

              {/* Mock Interview Button */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <Link
                    href="/interview"
                    className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
                  >
                    🎤 Start Mock Interview
                  </Link>
                  <p className="text-gray-500 text-sm mt-2">
                    Voice-powered interview practice based on your resume and job posting
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <footer className="mt-10 text-gray-400 text-xs text-center pb-6">
            © {new Date().getFullYear()} SmartSuccess.AI. All rights reserved.
          </footer>
        </div>
      </main>

      {/* ====== RIGHT SIDEBAR ====== */}
      <aside className="fixed right-0 top-0 h-full w-80 bg-white/95 backdrop-blur-sm shadow-lg z-30 flex flex-col p-6 overflow-y-auto">
        {/* Visitor Counter - At the very top */}
        <div className="bg-gray-50 rounded-xl p-3 mb-6">
          <SimpleVisitorCounter className="justify-center" />
        </div>

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

        {/* User Login Placeholder */}
        <div className="mt-auto pt-6 border-t border-gray-200">
          <button
            disabled
            className="w-full py-3 px-4 bg-gray-100 text-gray-500 font-medium rounded-lg cursor-not-allowed"
          >
            🔐 User Login (Coming Soon)
          </button>
        </div>
      </aside>
    </div>
  );
}
