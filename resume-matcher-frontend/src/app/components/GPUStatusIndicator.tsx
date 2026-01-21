/**
 * SmartSuccess.AI - GPU Status Indicator Component
 * Shows GPU server availability and status
 */

'use client';

import React from 'react';
import { useGPUStatus } from '../hooks/useGPUBackend';

interface GPUStatusIndicatorProps {
  /** Show detailed status or just indicator */
  showDetails?: boolean;
  /** Custom class name */
  className?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

/**
 * GPU Status Indicator
 * Displays the availability status of the GPU server
 */
export function GPUStatusIndicator({
  showDetails = false,
  className = '',
  size = 'md'
}: GPUStatusIndicatorProps) {
  const { available, checking } = useGPUStatus();

  const sizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4'
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  if (checking) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className={`${sizeClasses[size]} rounded-full bg-yellow-400 animate-pulse`} />
        {showDetails && (
          <span className={`${textSizeClasses[size]} text-gray-500`}>
            Checking GPU...
          </span>
        )}
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div
        className={`${sizeClasses[size]} rounded-full ${
          available 
            ? 'bg-green-500 shadow-green-500/50 shadow-sm' 
            : 'bg-gray-400'
        }`}
        title={available ? 'GPU Server Online' : 'GPU Server Offline'}
      />
      {showDetails && (
        <span className={`${textSizeClasses[size]} ${
          available ? 'text-green-600' : 'text-gray-500'
        }`}>
          {available ? 'GPU Enhanced' : 'Standard Mode'}
        </span>
      )}
    </div>
  );
}

/**
 * GPU Status Badge
 * More prominent badge-style indicator
 */
export function GPUStatusBadge({
  className = ''
}: {
  className?: string;
}) {
  const { available, checking } = useGPUStatus();

  if (checking) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-100 text-yellow-800 text-xs font-medium ${className}`}>
        <div className="h-1.5 w-1.5 rounded-full bg-yellow-500 animate-pulse" />
        Checking...
      </div>
    );
  }

  if (available) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100 text-green-800 text-xs font-medium ${className}`}>
        <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
        GPU Enhanced
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium ${className}`}>
      <div className="h-1.5 w-1.5 rounded-full bg-gray-400" />
      Standard Mode
    </div>
  );
}

/**
 * GPU Status Card
 * Detailed status card with all information
 */
export function GPUStatusCard({
  className = ''
}: {
  className?: string;
}) {
  const { available, checking } = useGPUStatus();

  return (
    <div className={`bg-white rounded-lg border p-4 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-medium text-gray-900">Server Status</h3>
          <p className="text-sm text-gray-500 mt-1">
            {checking 
              ? 'Checking connection...'
              : available 
                ? 'GPU server online - enhanced features available'
                : 'Running in standard mode'
            }
          </p>
        </div>
        <GPUStatusIndicator size="lg" />
      </div>

      {!checking && (
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Voice Processing</span>
            <p className={`font-medium ${available ? 'text-green-600' : 'text-gray-900'}`}>
              {available ? 'Whisper AI' : 'Web Speech'}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Speech Output</span>
            <p className={`font-medium ${available ? 'text-green-600' : 'text-gray-900'}`}>
              {available ? 'XTTS Neural' : 'Browser TTS'}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Question Bank</span>
            <p className={`font-medium ${available ? 'text-green-600' : 'text-gray-900'}`}>
              {available ? 'GPU RAG' : 'Standard'}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Response Speed</span>
            <p className={`font-medium ${available ? 'text-green-600' : 'text-gray-900'}`}>
              {available ? 'Ultra Fast' : 'Normal'}
            </p>
          </div>
        </div>
      )}

      {available && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="text-green-600">Premium voice features enabled</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default GPUStatusIndicator;
