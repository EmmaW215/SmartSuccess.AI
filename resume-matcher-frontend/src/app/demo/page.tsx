// ============================================================
// FILE: resume-matcher-frontend/src/app/demo/page.tsx
// Demo page with HTML formatted outputs
// ============================================================

'use client';

import React from 'react';
import Link from 'next/link';

export default function DemoPage() {
  // Sample demo data showcasing the analysis output
  const demoData = {
    job_summary: {
      position: 'Senior Software Engineer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA (Hybrid)',
      keyRequirements: [
        '5+ years of experience in full-stack development',
        'Proficiency in React, Node.js, and Python',
        'Experience with cloud platforms (AWS/GCP)',
        'Strong problem-solving and communication skills',
        'Bachelor\'s degree in Computer Science or related field',
      ],
      preferredQualifications: [
        'Experience with microservices architecture',
        'Knowledge of CI/CD pipelines',
        'Leadership experience in Agile teams',
      ],
    },

    resume_comparison: [
      { category: 'Years of Experience', status: '✅ Strong', comments: '7+ years of full-stack development experience' },
      { category: 'React & Frontend', status: '✅ Strong', comments: 'Extensive React experience with multiple production apps' },
      { category: 'Node.js Backend', status: '✅ Strong', comments: 'Built RESTful APIs and microservices' },
      { category: 'Python', status: '✅ Moderate-Strong', comments: 'Used for data processing and automation scripts' },
      { category: 'Cloud Platforms (AWS)', status: '✅ Strong', comments: 'Deployed and managed applications on AWS' },
      { category: 'Problem-Solving', status: '✅ Strong', comments: 'Led technical troubleshooting for critical systems' },
      { category: 'Communication', status: '✅ Strong', comments: 'Cross-functional collaboration experience' },
      { category: 'Education', status: '✅ Strong', comments: 'B.S. in Computer Science' },
      { category: 'Microservices', status: '✅ Moderate-Strong', comments: 'Implemented service-oriented architecture' },
      { category: 'CI/CD Pipelines', status: '⚠️ Partial', comments: 'Basic experience with Jenkins and GitHub Actions' },
      { category: 'Leadership', status: '✅ Moderate-Strong', comments: 'Mentored junior developers' },
    ],

    match_score: 87,

    tailored_resume_summary: `Results-driven Senior Software Engineer with 7+ years of experience building scalable web applications using React, Node.js, and Python. Proven track record of delivering high-impact solutions in cloud environments (AWS), with expertise in microservices architecture and cross-functional team collaboration. Passionate about clean code, performance optimization, and mentoring emerging talent. Seeking to leverage technical leadership skills and full-stack expertise to drive innovation at TechCorp Inc.`,

    tailored_work_experience: [
      `<strong>Led development of customer-facing React application</strong> serving 500K+ monthly active users, implementing responsive design patterns and state management with Redux that improved user engagement by 35%`,
      `<strong>Architected and deployed microservices</strong> on AWS (ECS, Lambda, API Gateway), reducing system latency by 40% and enabling horizontal scaling during peak traffic periods`,
      `<strong>Built RESTful APIs using Node.js and Express</strong>, integrating with PostgreSQL and MongoDB databases, supporting 10M+ daily API calls with 99.9% uptime`,
      `<strong>Implemented CI/CD pipelines</strong> using GitHub Actions, automating testing and deployment processes that reduced release cycles from 2 weeks to 2 days`,
      `<strong>Mentored team of 4 junior developers</strong>, conducting code reviews and pair programming sessions that improved team velocity by 25% over 6 months`,
      `<strong>Collaborated with product and design teams</strong> in Agile sprints, translating business requirements into technical specifications and delivering features on schedule`,
    ],

    cover_letter: `Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position at TechCorp Inc. With over 7 years of experience in full-stack development and a passion for building scalable, user-centric applications, I am excited about the opportunity to contribute to your innovative team.

Throughout my career, I have developed expertise in React, Node.js, and Python—technologies central to this role. At my current position, I led the development of a customer-facing application serving over 500,000 monthly users, where I implemented performance optimizations that improved user engagement by 35%. My experience architecting microservices on AWS has given me deep insights into building resilient, scalable systems.

What particularly draws me to TechCorp Inc. is your commitment to innovation and your collaborative engineering culture. I thrive in Agile environments where cross-functional teamwork drives results, and I have a proven track record of mentoring junior developers while delivering high-quality code.

I am confident that my technical skills, leadership experience, and passion for continuous learning make me a strong fit for this position. I would welcome the opportunity to discuss how my background aligns with TechCorp's goals and how I can contribute to your team's success.

Thank you for considering my application. I look forward to the possibility of speaking with you.

Best regards,
[Your Name]`
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                SmartSuccess.AI
              </h1>
              <p className="text-gray-500">Demo Analysis Report</p>
            </div>
            <Link
              href="/"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              ← Try It Yourself
            </Link>
          </div>
          
          {/* Demo Banner */}
          <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-xl p-4 border border-purple-200">
            <div className="flex items-center">
              <span className="text-2xl mr-3">✨</span>
              <div>
                <h2 className="font-semibold text-purple-800">Sample Analysis Preview</h2>
                <p className="text-sm text-purple-600">
                  This is a demonstration of the AI-powered analysis you&apos;ll receive when you submit your resume and job posting.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Results */}
        <div className="bg-white rounded-xl shadow-lg p-8 border border-blue-100">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">📊 Analysis Results</h2>

          {/* 1. Job Requirement Summary - HTML Bullet List Format */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-blue-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">1. Job Requirement Summary</span>
            </div>
            <div className="bg-blue-50 rounded-lg p-5 ml-5">
              <div className="mb-4">
                <p className="text-gray-800"><strong>Position:</strong> {demoData.job_summary.position}</p>
                <p className="text-gray-800"><strong>Company:</strong> {demoData.job_summary.company}</p>
                <p className="text-gray-800"><strong>Location:</strong> {demoData.job_summary.location}</p>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-800 font-semibold mb-2">Key Requirements:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  {demoData.job_summary.keyRequirements.map((req, index) => (
                    <li key={index} className="text-gray-700">{req}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <p className="text-gray-800 font-semibold mb-2">Preferred Qualifications:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  {demoData.job_summary.preferredQualifications.map((qual, index) => (
                    <li key={index} className="text-gray-700">{qual}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 2. Resume vs. Job Requirements Comparison - HTML Table Format */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-purple-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">2. Resume vs. Job Requirements Comparison</span>
            </div>
            <div className="ml-5 overflow-x-auto">
              <table className="w-full border-collapse bg-white rounded-lg overflow-hidden shadow-sm">
                <thead>
                  <tr className="bg-purple-100">
                    <th className="px-4 py-3 text-left text-sm font-semibold text-purple-800 border-b border-purple-200">Category</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-purple-800 border-b border-purple-200">Match Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-purple-800 border-b border-purple-200">Comments</th>
                  </tr>
                </thead>
                <tbody>
                  {demoData.resume_comparison.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-3 text-sm text-gray-800 border-b border-gray-100 font-medium">{row.category}</td>
                      <td className="px-4 py-3 text-sm border-b border-gray-100">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          row.status.includes('Strong') ? 'bg-green-100 text-green-800' :
                          row.status.includes('Moderate') ? 'bg-yellow-100 text-yellow-800' :
                          row.status.includes('Partial') ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 border-b border-gray-100">{row.comments}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* 3. Match Score */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-green-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">3. Overall Match Score</span>
            </div>
            <div className="ml-5 bg-green-50 rounded-lg p-6">
              <div className="flex items-center mb-3">
                <span className="text-5xl font-bold text-green-600 mr-4">{demoData.match_score}%</span>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-4 bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all duration-1000"
                      style={{ width: `${demoData.match_score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              <p className="text-green-700 text-sm">
                🎯 Strong match! Your profile aligns well with the job requirements.
              </p>
            </div>
          </div>

          {/* 4. Tailored Resume Summary */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-purple-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">4. Tailored Professional Summary</span>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 ml-5 border-l-4 border-purple-400">
              <p className="text-gray-700 text-base italic">{demoData.tailored_resume_summary}</p>
            </div>
            <p className="text-xs text-gray-500 ml-5 mt-2">
              💡 Copy this optimized summary to your resume header
            </p>
          </div>

          {/* 5. Tailored Work Experience */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-orange-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">5. Tailored Work Experience Bullets</span>
            </div>
            <ul className="ml-5 space-y-3">
              {demoData.tailored_work_experience.map((item, index) => (
                <li
                  key={index}
                  className="flex items-start bg-orange-50 rounded-lg p-3 border-l-4 border-orange-400"
                >
                  <span className="text-orange-500 font-bold mr-2">•</span>
                  <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: item }}></span>
                </li>
              ))}
            </ul>
            <p className="text-xs text-gray-500 ml-5 mt-2">
              💡 These bullets are optimized to highlight skills matching the job requirements
            </p>
          </div>

          {/* 6. Cover Letter */}
          <div className="mb-8">
            <div className="flex items-center mb-3">
              <div className="w-1.5 h-7 bg-teal-500 rounded mr-3"></div>
              <span className="text-lg font-semibold text-gray-800">6. Generated Cover Letter</span>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 ml-5">
              <p className="text-gray-700 text-base whitespace-pre-wrap leading-relaxed">
                {demoData.cover_letter}
              </p>
            </div>
            <p className="text-xs text-gray-500 ml-5 mt-2">
              💡 Personalize this cover letter with specific details about the company
            </p>
          </div>

          {/* Coming Soon Section */}
          <div className="mt-10 pt-8 border-t-2 border-dashed border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">🚀 Coming Soon</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-200">
                <div className="text-3xl mb-3">🎤</div>
                <h4 className="font-semibold text-indigo-800 mb-2">AI Mock Interview</h4>
                <p className="text-sm text-indigo-600">
                  Practice answering interview questions with our voice-enabled AI interviewer. 
                  Get real-time feedback based on your resume and the job requirements.
                </p>
              </div>
              <div className="bg-gradient-to-br from-teal-50 to-green-50 rounded-xl p-6 border border-teal-200">
                <div className="text-3xl mb-3">💬</div>
                <h4 className="font-semibold text-teal-800 mb-2">Interview Chat History</h4>
                <p className="text-sm text-teal-600">
                  Review your mock interview transcripts, track your progress, 
                  and download conversation histories for later review.
                </p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-10 text-center">
            <Link
              href="/"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition shadow-lg transform hover:scale-105"
            >
              🚀 Create Your Analysis Now
            </Link>
            <p className="text-gray-500 text-sm mt-3">
              Free to use • No sign-up required
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-gray-400 text-xs">
          © {new Date().getFullYear()} SmartSuccess.AI. All rights reserved.
        </footer>
      </div>
    </div>
  );
}
