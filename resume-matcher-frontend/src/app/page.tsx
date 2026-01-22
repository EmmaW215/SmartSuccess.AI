'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Users, Play, Terminal, Database, Cpu, Volume2, VolumeX } from 'lucide-react';
import Link from 'next/link';
import { generateSpeech, decodeAudioBuffer } from '@/services/geminiService';
import FloatingIcon from '@/components/FloatingIcon';

const GREETING_TEXT = "Welcome to the AI Evaluation Platform. I am your guide to career excellence. Explore MatchWise to tailor your professional identity, or master your skills with SmartSuccess Mock Interviews. Your journey to AI leadership starts now.";

export default function Home() {
  const [hasEntered, setHasEntered] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [audioError, setAudioError] = useState<string | null>(null);
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const greetingBufferRef = useRef<AudioBuffer | null>(null);
  const currentSourceRef = useRef<AudioBufferSourceNode | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (currentSourceRef.current) {
        currentSourceRef.current.stop();
      }
    };
  }, []);

  const playGreeting = async () => {
    if (!audioContextRef.current || !isVoiceEnabled) return;

    // Ensure audio context is resumed if suspended
    if (audioContextRef.current.state === 'suspended') {
      await audioContextRef.current.resume();
    }

    try {
      setIsSpeaking(true);
      setAudioError(null); // Clear any previous errors
      
      // Cache the buffer so we don't call the API every time
      if (!greetingBufferRef.current) {
        const audioData = await generateSpeech(GREETING_TEXT);
        greetingBufferRef.current = await decodeAudioBuffer(audioData, audioContextRef.current);
      }
      
      const source = audioContextRef.current.createBufferSource();
      source.buffer = greetingBufferRef.current;
      source.connect(audioContextRef.current.destination);
      currentSourceRef.current = source;
      
      source.onended = () => {
        setIsSpeaking(false);
        currentSourceRef.current = null;
      };
      
      source.start(0);
    } catch (error) {
      console.error("Speech generation or playback failed:", error);
      setIsSpeaking(false);
      // Clear the buffer so it will retry next time
      greetingBufferRef.current = null;
      
      // Silently fail for all errors (API key missing, network errors, quota exceeded, etc.)
      // Don't show any error message to the user
      setAudioError(null);
    }
  };

  const toggleVoice = () => {
    if (isVoiceEnabled) {
      // Turn OFF
      setIsVoiceEnabled(false);
      if (currentSourceRef.current) {
        try {
          currentSourceRef.current.stop();
        } catch {
          // Ignore if already stopped
        }
        currentSourceRef.current = null;
      }
      setIsSpeaking(false);
    } else {
      // Turn ON
      setIsVoiceEnabled(true);
      // We'll use a timeout to trigger playGreeting to avoid state race condition
      setTimeout(() => {
        if (!isSpeaking) playGreeting();
      }, 50);
    }
  };

  const handleEntry = async () => {
    setHasEntered(true);
    
    // Initialize Audio Context on user gesture
    if (!audioContextRef.current) {
      const AudioContextClass = window.AudioContext || (window as typeof window & { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      audioContextRef.current = new AudioContextClass({ sampleRate: 24000 });
    }

    // Start the voice loop
    playGreeting();
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950 selection:bg-cyan-500/30">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-900/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-900/10 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      <AnimatePresence>
        {!hasEntered ? (
          <motion.div 
            key="splash"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950 px-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8 }}
              className="text-center relative"
            >
              {/* Decorative Halo behind text */}
              <div className="absolute inset-0 bg-cyan-500/5 blur-[100px] rounded-full scale-150 animate-pulse-slow" />
              
              <h1 className="relative text-4xl md:text-6xl font-orbitron font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 drop-shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                AI CAREER MASTERY
              </h1>
              <p className="relative text-slate-400 max-w-md mx-auto mb-12 text-lg leading-relaxed">
                Evaluating the next generation of AI Engineering, Architecture, and Leadership.
              </p>
              
              <div className="relative inline-block">
                {/* Layered Spreading Halo Effect */}
                <motion.div 
                  animate={{ scale: [1, 2], opacity: [0.6, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeOut" }}
                  className="absolute inset-0 bg-cyan-500/20 rounded-full blur-2xl"
                />
                <motion.div 
                  animate={{ scale: [1, 1.5], opacity: [0.4, 0] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeOut", delay: 1 }}
                  className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl"
                />

                <button
                  onClick={handleEntry}
                  className="group relative z-10 inline-flex items-center gap-3 px-10 py-5 bg-slate-900 text-white font-orbitron tracking-widest text-lg border border-cyan-500/50 hover:border-cyan-400 transition-all duration-300 overflow-hidden rounded-sm"
                >
                  <div className="absolute inset-0 w-0 bg-gradient-to-r from-cyan-500/20 to-transparent group-hover:w-full transition-all duration-700 ease-out" />
                  
                  {/* Radiant Light Stream Effect - Constant Animation */}
                  <div className="absolute top-0 -left-full w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-[45deg] animate-[shimmer_2.5s_infinite]" />
                  
                  <Play className="w-5 h-5 fill-cyan-400 text-cyan-400 group-hover:scale-110 transition-transform" />
                  <span>INITIATE PLATFORM</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div 
            key="main"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="relative z-10 w-full min-h-screen flex flex-col"
          >
            {/* Header */}
            <header className="w-full px-6 py-8 flex justify-between items-center max-w-7xl mx-auto">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
                  <Cpu className="text-white w-6 h-6" />
                </div>
                <span className="font-orbitron font-bold text-xl tracking-tighter">AI MASTERY</span>
              </div>
              <nav className="hidden md:flex gap-8 text-sm font-medium text-slate-400">
                <a href="#" className="hover:text-cyan-400 transition-colors">ENGINEERING</a>
                <a href="#" className="hover:text-cyan-400 transition-colors">ARCHITECTURE</a>
                <a href="#" className="hover:text-cyan-400 transition-colors">AIOPS</a>
                <a href="#" className="hover:text-cyan-400 transition-colors">PRODUCT</a>
              </nav>
              <Link 
                href="/dashboard" 
                className="px-5 py-2 rounded-full border border-slate-700 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all text-sm font-medium text-white"
              >
                DASHBOARD
              </Link>
            </header>

            {/* Main Hero Content */}
            <main className="flex-1 flex flex-col items-center justify-center px-4 relative">
              <div className="text-center max-w-4xl mx-auto mb-24 z-20 pointer-events-none relative">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h2 className="text-xs md:text-sm font-orbitron tracking-[0.4em] text-cyan-500/80 mb-6 uppercase">
                    Evaluation & Career Assessment
                  </h2>
                  <h1 className="text-5xl md:text-8xl font-orbitron font-bold leading-tight mb-8">
                    <span className="text-white">Elevate Your AI</span> <br /> 
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-500 drop-shadow-[0_0_20px_rgba(6,182,212,0.2)]">
                      Professional Identity
                    </span>
                  </h1>
                </motion.div>
                
                {audioError && (
                  <motion.p 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-red-400 mb-4 bg-red-950/20 border border-red-900/50 px-4 py-2 rounded text-sm font-mono"
                  >
                    {audioError}
                  </motion.p>
                )}
                
                {/* Voice Visualizer - Persistent & Clickable */}
                <div 
                  onClick={toggleVoice}
                  title={isVoiceEnabled ? "Mute guidance" : "Unmute guidance"}
                  className="flex flex-col items-center gap-3 cursor-pointer pointer-events-auto group mb-8"
                >
                  <div className="flex justify-center gap-1.5 h-10 items-end">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                      <motion.div
                        key={i}
                        animate={isSpeaking ? { 
                          height: [8, Math.random() * 30 + 10, 8],
                          opacity: 1
                        } : { 
                          height: isVoiceEnabled ? [4, 8, 4] : 2,
                          opacity: isVoiceEnabled ? 0.5 : 0.2 
                        }}
                        transition={{ 
                          duration: isSpeaking ? (0.4 + i * 0.05) : 2, 
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                        className={`w-1.5 rounded-full transition-colors duration-500 ${
                          isVoiceEnabled 
                            ? "bg-gradient-to-t from-cyan-600 to-blue-400 shadow-[0_0_10px_rgba(6,182,212,0.5)]" 
                            : "bg-slate-700"
                        }`}
                      />
                    ))}
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-orbitron tracking-widest text-slate-500 group-hover:text-cyan-400 transition-colors">
                    {isVoiceEnabled ? (
                      <>
                        <Volume2 className="w-3 h-3" />
                        <span>VOICE GUIDANCE ACTIVE</span>
                      </>
                    ) : (
                      <>
                        <VolumeX className="w-3 h-3" />
                        <span>VOICE GUIDANCE MUTED</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Floating Icons Area */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none z-30">
                <div className="w-full h-full relative max-w-[1400px] mx-auto pointer-events-none">
                  {/* Left Peripheral Icon: MatchWise */}
                  <FloatingIcon 
                    label="MATCHWISE: RESUME TAILORING"
                    icon={<FileText className="w-10 h-10 md:w-14 md:h-14" />}
                    url="https://matchwise-ai.vercel.app/"
                    color="#06b6d4"
                    isSpeaking={isSpeaking}
                    initialX="8%"
                    initialY="40%"
                    rangeX={[0, 40, -20, 30, 0]}
                    rangeY={[0, -80, 50, -60, 0]}
                  />
                  
                  {/* Right Peripheral Icon: SmartSuccess */}
                  <div className="absolute left-[78%] top-[30%] pointer-events-none">
                    <FloatingIcon 
                      label="SMARTSUCCESS: MOCK INTERVIEW"
                      icon={<Users className="w-10 h-10 md:w-14 md:h-14" />}
                      url="/interview"
                      color="#a855f7"
                      isSpeaking={isSpeaking}
                      initialX="0%"
                      initialY="0%"
                      rangeX={[0, -50, 30, -40, 0]}
                      rangeY={[0, 60, -70, 50, 0]}
                      delay={4}
                    />
                  </div>
                </div>
              </div>
            </main>

            {/* Platform Stats / Footer Area */}
            <footer className="w-full px-6 py-12 bg-slate-900/30 backdrop-blur-2xl border-t border-slate-800/50">
              <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
                {[
                  { label: "Global Reach", val: "12k+", sub: "Active AI Engineers" },
                  { label: "Success Rate", val: "84%", sub: "Interview Advancements" },
                  { label: "Integrations", val: "500+", sub: "Tech Partners" },
                  { label: "AI Readiness", val: "Tier-1", sub: "Industry Standard" },
                ].map((stat, idx) => (
                  <div key={idx} className="space-y-2 group">
                    <h4 className="text-slate-500 text-[10px] font-orbitron uppercase tracking-[0.2em] group-hover:text-cyan-500/70 transition-colors">{stat.label}</h4>
                    <p className="text-2xl font-bold font-orbitron text-slate-200">{stat.val}</p>
                    <p className="text-slate-500 text-xs">{stat.sub}</p>
                  </div>
                ))}
              </div>
            </footer>

            {/* Tech Decoration */}
            <div className="fixed bottom-0 left-0 p-4 pointer-events-auto opacity-40 hidden lg:block">
              <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-500/60 uppercase tracking-widest">
                <Terminal className="w-3 h-3" />
                <span>Status: Autonomous Guidance Active</span>
              </div>
            </div>
            <div className="fixed bottom-0 right-0 p-4 pointer-events-auto opacity-40 hidden lg:block">
              <div className="flex items-center gap-2 text-[10px] font-mono text-purple-500/60 uppercase tracking-widest">
                <Database className="w-3 h-3" />
                <span>Node: US-WEST-01 // EVAL-SYS</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        @keyframes shimmer {
          0% { left: -100%; }
          100% { left: 200%; }
        }
      `}</style>
    </div>
  );
}
