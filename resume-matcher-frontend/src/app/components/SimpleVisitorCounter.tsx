'use client';

import React, { useState, useEffect } from 'react';

interface SimpleVisitorCounterProps {
  className?: string;
}

export default function SimpleVisitorCounter({ className = '' }: SimpleVisitorCounterProps) {
  const [visitorCount, setVisitorCount] = useState<number | null>(null);
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
    
    const fetchAndIncrementCount = async () => {
      try {
        // Check if this session has already been counted
        const sessionCounted = sessionStorage.getItem('visitor_counted');
        
        const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://smartsuccess-ai.onrender.com';
        
        if (!sessionCounted) {
          // First visit in this session - increment count
          const response = await fetch(`${BACKEND_URL}/api/visitor/increment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
          });
          
          if (response.ok) {
            const data = await response.json();
            setVisitorCount(data.count);
            sessionStorage.setItem('visitor_counted', 'true');
          } else {
            // Fallback to GET if POST fails
            const getResponse = await fetch(`${BACKEND_URL}/api/visitor/count`);
            if (getResponse.ok) {
              const data = await getResponse.json();
              setVisitorCount(data.count);
            }
          }
        } else {
          // Already counted this session - just get current count
          const response = await fetch(`${BACKEND_URL}/api/visitor/count`);
          if (response.ok) {
            const data = await response.json();
            setVisitorCount(data.count);
          }
        }
      } catch (err) {
        console.error('Visitor counter error:', err);
        // Fallback to localStorage for offline/error cases
        try {
          const localCount = parseInt(localStorage.getItem('fallback_visitor_count') || '100');
          setVisitorCount(localCount);
        } catch {
          setVisitorCount(100); // Default fallback
        }
      }
    };

    fetchAndIncrementCount();
  }, []);

  // Format large numbers
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  // Loading state
  if (!mounted || visitorCount === null) {
    return (
      <div className={`flex items-center justify-center space-x-2 ${className}`}>
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600 font-medium">Visitors:</span>
        </div>
        <div className="text-lg font-bold text-blue-600 animate-pulse">
          ...
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-center space-x-2 ${className}`}>
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-sm text-gray-600 font-medium">Visitors:</span>
      </div>
      <div className="text-lg font-bold text-blue-600 transition-all duration-300 ease-in-out">
        {formatNumber(visitorCount)}
      </div>
    </div>
  );
}
