
import React from 'react';
import { motion } from 'framer-motion';

interface FloatingIconProps {
  label: string;
  icon: React.ReactNode;
  url: string;
  color: string;
  delay?: number;
  isSpeaking: boolean;
  initialX: string | number;
  initialY: string | number;
  rangeX: [number, number, number, number, number];
  rangeY: [number, number, number, number, number];
}

const FloatingIcon: React.FC<FloatingIconProps> = ({ 
  label, 
  icon, 
  url, 
  color, 
  delay = 0, 
  isSpeaking,
  initialX,
  initialY,
  rangeX,
  rangeY
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ 
        opacity: 1, 
        scale: 1,
        x: rangeX,
        y: rangeY,
      }}
      transition={{
        x: {
          duration: 22 + delay,
          repeat: Infinity,
          ease: "easeInOut",
        },
        y: {
          duration: 28 + delay,
          repeat: Infinity,
          ease: "easeInOut",
        },
        opacity: { duration: 1 },
        scale: { duration: 0.5 }
      }}
      className="absolute cursor-pointer group z-30 pointer-events-auto"
      style={{ left: initialX, top: initialY }}
    >
      <a 
        href={url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="flex flex-col items-center gap-4"
      >
        <motion.div
          animate={isSpeaking ? {
            scale: [1, 1.1, 1],
            boxShadow: [
              `0 0 20px ${color}66`,
              `0 0 50px ${color}aa`,
              `0 0 20px ${color}66`,
            ]
          } : {
            boxShadow: [
              `0 0 10px ${color}33`,
              `0 0 20px ${color}44`,
              `0 0 10px ${color}33`,
            ]
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className={`w-24 h-24 md:w-32 md:h-32 rounded-full flex items-center justify-center bg-slate-900/80 backdrop-blur-sm border-2 transition-all duration-500`}
          style={{ borderColor: color }}
        >
          <div className="text-white transform group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        </motion.div>
        
        <div className="bg-slate-900/90 backdrop-blur-md px-4 py-2 rounded-full border border-slate-700 shadow-2xl group-hover:border-white/30 transition-colors">
          <span className="text-xs md:text-sm font-orbitron font-medium tracking-wider text-slate-300 group-hover:text-white whitespace-nowrap">
            {label}
          </span>
        </div>
      </a>
    </motion.div>
  );
};

export default FloatingIcon;
