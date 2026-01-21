/**
 * SmartSuccess.AI - useGPUBackend Hook
 * React hook for GPU backend integration with automatic fallback
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  checkGPUHealth,
  getGPUHealthDetails,
  refreshGPUHealth,
  getBackendStatus,
  routedFetch
} from '../utils/requestRouter';

interface GPUStatus {
  available: boolean;
  deviceName: string | null;
  memoryTotalGB: number | null;
  memoryFreeGB: number | null;
  utilizationPercent: number | null;
  modelsLoaded: Record<string, boolean>;
}

interface UseGPUBackendOptions {
  /** Enable auto health check polling */
  autoCheck?: boolean;
  /** Health check interval in ms (default: 30000) */
  checkInterval?: number;
  /** Callback when GPU becomes available */
  onGPUAvailable?: () => void;
  /** Callback when GPU becomes unavailable */
  onGPUUnavailable?: () => void;
}

interface UseGPUBackendReturn {
  /** Whether GPU server is available */
  gpuAvailable: boolean;
  /** Detailed GPU status */
  gpuStatus: GPUStatus | null;
  /** Loading state for health check */
  isChecking: boolean;
  /** Error from last health check */
  error: string | null;
  /** Last successful check timestamp */
  lastChecked: Date | null;
  /** Manually trigger health check */
  checkHealth: () => Promise<boolean>;
  /** Make a request with automatic routing */
  request: <T>(
    endpoint: string,
    options?: RequestInit,
    preferGPU?: boolean
  ) => Promise<T>;
  /** Get appropriate backend URL for an endpoint */
  getBackendUrl: (endpoint: string) => string;
}

/**
 * Hook for managing GPU backend connection
 */
export function useGPUBackend(options: UseGPUBackendOptions = {}): UseGPUBackendReturn {
  const {
    autoCheck = true,
    checkInterval = 30000,
    onGPUAvailable,
    onGPUUnavailable
  } = options;

  const [gpuAvailable, setGPUAvailable] = useState(false);
  const [gpuStatus, setGPUStatus] = useState<GPUStatus | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const previousAvailable = useRef<boolean | null>(null);

  // Health check function
  const checkHealth = useCallback(async (): Promise<boolean> => {
    setIsChecking(true);
    setError(null);

    try {
      const available = await refreshGPUHealth();
      setGPUAvailable(available);
      setLastChecked(new Date());

      // Get detailed status if available
      const details = getGPUHealthDetails();
      if (details) {
        setGPUStatus({
          available: details.gpu_available,
          deviceName: null, // Would need separate GPU status endpoint
          memoryTotalGB: details.gpu_memory_total,
          memoryFreeGB: details.gpu_memory_free,
          utilizationPercent: details.gpu_utilization,
          modelsLoaded: details.models_loaded
        });
      }

      // Trigger callbacks on status change
      if (previousAvailable.current !== null && previousAvailable.current !== available) {
        if (available) {
          onGPUAvailable?.();
        } else {
          onGPUUnavailable?.();
        }
      }
      previousAvailable.current = available;

      return available;

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Health check failed';
      setError(message);
      setGPUAvailable(false);

      if (previousAvailable.current === true) {
        onGPUUnavailable?.();
      }
      previousAvailable.current = false;

      return false;

    } finally {
      setIsChecking(false);
    }
  }, [onGPUAvailable, onGPUUnavailable]);

  // Auto health check on mount and interval
  useEffect(() => {
    if (!autoCheck) return;

    // Initial check
    checkHealth();

    // Set up interval
    const intervalId = setInterval(checkHealth, checkInterval);

    return () => clearInterval(intervalId);
  }, [autoCheck, checkInterval, checkHealth]);

  // Make a request with automatic routing
  const request = useCallback(async <T>(
    endpoint: string,
    options: RequestInit = {},
    preferGPU: boolean = true
  ): Promise<T> => {
    const response = await routedFetch(endpoint, options, {
      preferGPU,
      fallbackToRender: true
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    }

    return response.json();
  }, []);

  // Get backend URL for an endpoint
  const getBackendUrl = useCallback((endpoint: string): string => {
    const status = getBackendStatus();
    
    // Simple routing logic - GPU if available and endpoint supports it
    const gpuEndpoints = ['/interview', '/rag', '/voice', '/embedding'];
    const useGPU = status.gpuAvailable && 
      gpuEndpoints.some(prefix => endpoint.startsWith(prefix));

    return useGPU ? status.gpuUrl : status.renderUrl;
  }, []);

  return {
    gpuAvailable,
    gpuStatus,
    isChecking,
    error,
    lastChecked,
    checkHealth,
    request,
    getBackendUrl
  };
}

/**
 * Hook for GPU status display
 * Lighter weight version for status indicators
 */
export function useGPUStatus() {
  const [status, setStatus] = useState<{
    available: boolean;
    checking: boolean;
  }>({
    available: false,
    checking: true
  });

  useEffect(() => {
    const check = async () => {
      const available = await checkGPUHealth();
      setStatus({ available, checking: false });
    };

    check();

    // Recheck every minute
    const interval = setInterval(check, 60000);
    return () => clearInterval(interval);
  }, []);

  return status;
}

export default useGPUBackend;
