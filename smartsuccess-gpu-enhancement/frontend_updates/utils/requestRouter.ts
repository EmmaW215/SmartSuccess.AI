/**
 * SmartSuccess.AI - Request Router
 * Hybrid architecture: Routes requests to GPU server or Render based on availability
 * 
 * When GPU server is online: Uses GPU for voice, RAG, embeddings
 * When GPU server is offline: Falls back to Render for all services
 */

// Configuration
const GPU_BACKEND_URL = process.env.NEXT_PUBLIC_GPU_BACKEND_URL || 'https://gpu.smartsuccess.ai';
const RENDER_BACKEND_URL = process.env.NEXT_PUBLIC_RENDER_BACKEND_URL || 'https://smartsuccess-ai.onrender.com';

// Health check cache
let gpuHealthCache: {
  available: boolean;
  lastChecked: number;
  details: GPUHealthDetails | null;
} = {
  available: false,
  lastChecked: 0,
  details: null
};

const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds

interface GPUHealthDetails {
  status: string;
  gpu_available: boolean;
  gpu_memory_free: number | null;
  gpu_memory_total: number | null;
  gpu_utilization: number | null;
  models_loaded: Record<string, boolean>;
  uptime_seconds: number;
}

/**
 * Endpoint routing configuration
 */
const ROUTING_CONFIG = {
  // Endpoints that ALWAYS go to Render (user management, payments)
  renderOnly: [
    '/auth',
    '/payment',
    '/user',
    '/analytics',
    '/stripe',
    '/webhook'
  ],
  
  // Endpoints that prefer GPU when available
  gpuPreferred: [
    '/interview/voice',
    '/rag/general',
    '/rag/personalized',
    '/embedding',
    '/voice'
  ],
  
  // Endpoints that can work on both (interview text mode)
  hybrid: [
    '/interview/start',
    '/interview/message',
    '/interview/session'
  ]
};

/**
 * Check if GPU server is available
 */
export async function checkGPUHealth(): Promise<boolean> {
  const now = Date.now();
  
  // Return cached result if recent
  if (now - gpuHealthCache.lastChecked < HEALTH_CHECK_INTERVAL) {
    return gpuHealthCache.available;
  }
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${GPU_BACKEND_URL}/health`, {
      method: 'GET',
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data: GPUHealthDetails = await response.json();
      
      gpuHealthCache = {
        available: data.status === 'healthy' && data.gpu_available,
        lastChecked: now,
        details: data
      };
      
      console.log('🖥️ GPU server health:', gpuHealthCache.available ? 'Available' : 'Unavailable');
      return gpuHealthCache.available;
    }
    
    gpuHealthCache = { available: false, lastChecked: now, details: null };
    return false;
    
  } catch (error) {
    console.warn('⚠️ GPU server unreachable:', error);
    gpuHealthCache = { available: false, lastChecked: now, details: null };
    return false;
  }
}

/**
 * Get GPU health details
 */
export function getGPUHealthDetails(): GPUHealthDetails | null {
  return gpuHealthCache.details;
}

/**
 * Force refresh GPU health check
 */
export async function refreshGPUHealth(): Promise<boolean> {
  gpuHealthCache.lastChecked = 0;
  return checkGPUHealth();
}

/**
 * Determine which backend to use for an endpoint
 */
export async function getBackendUrl(endpoint: string, preferGPU: boolean = true): Promise<string> {
  // Check if endpoint is Render-only
  const isRenderOnly = ROUTING_CONFIG.renderOnly.some(prefix => 
    endpoint.startsWith(prefix)
  );
  
  if (isRenderOnly) {
    return RENDER_BACKEND_URL;
  }
  
  // Check if endpoint prefers GPU
  const isGPUPreferred = ROUTING_CONFIG.gpuPreferred.some(prefix =>
    endpoint.startsWith(prefix)
  );
  
  // For GPU-preferred endpoints, check availability
  if (isGPUPreferred && preferGPU) {
    const gpuAvailable = await checkGPUHealth();
    if (gpuAvailable) {
      return GPU_BACKEND_URL;
    }
  }
  
  // For hybrid endpoints, check GPU if voice is enabled
  const isHybrid = ROUTING_CONFIG.hybrid.some(prefix =>
    endpoint.startsWith(prefix)
  );
  
  if (isHybrid && preferGPU) {
    const gpuAvailable = await checkGPUHealth();
    if (gpuAvailable) {
      return GPU_BACKEND_URL;
    }
  }
  
  // Default to Render
  return RENDER_BACKEND_URL;
}

/**
 * Make a request with automatic backend routing
 */
export async function routedFetch(
  endpoint: string,
  options: RequestInit = {},
  config: {
    preferGPU?: boolean;
    fallbackToRender?: boolean;
    retries?: number;
  } = {}
): Promise<Response> {
  const {
    preferGPU = true,
    fallbackToRender = true,
    retries = 1
  } = config;
  
  // Get appropriate backend
  const backendUrl = await getBackendUrl(endpoint, preferGPU);
  const fullUrl = `${backendUrl}${endpoint}`;
  
  console.log(`📡 Request: ${endpoint} → ${backendUrl === GPU_BACKEND_URL ? 'GPU' : 'Render'}`);
  
  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    return response;
    
  } catch (error) {
    console.error(`❌ Request failed: ${endpoint}`, error);
    
    // If GPU failed and fallback is enabled, try Render
    if (backendUrl === GPU_BACKEND_URL && fallbackToRender) {
      console.log('🔄 Falling back to Render backend...');
      
      // Mark GPU as unavailable
      gpuHealthCache.available = false;
      gpuHealthCache.lastChecked = Date.now();
      
      const renderUrl = `${RENDER_BACKEND_URL}${endpoint}`;
      return fetch(renderUrl, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
    }
    
    throw error;
  }
}

/**
 * Interview-specific routing
 */
export async function routedInterviewFetch(
  endpoint: string,
  options: RequestInit = {},
  useVoice: boolean = false
): Promise<Response> {
  // Voice interviews always prefer GPU
  if (useVoice) {
    const gpuAvailable = await checkGPUHealth();
    if (!gpuAvailable) {
      console.warn('⚠️ Voice interview requested but GPU unavailable');
      // Could throw error or return indicator to frontend
    }
  }
  
  return routedFetch(endpoint, options, {
    preferGPU: useVoice,
    fallbackToRender: true
  });
}

/**
 * Get current backend status
 */
export function getBackendStatus(): {
  gpuAvailable: boolean;
  gpuUrl: string;
  renderUrl: string;
  lastChecked: Date | null;
} {
  return {
    gpuAvailable: gpuHealthCache.available,
    gpuUrl: GPU_BACKEND_URL,
    renderUrl: RENDER_BACKEND_URL,
    lastChecked: gpuHealthCache.lastChecked 
      ? new Date(gpuHealthCache.lastChecked) 
      : null
  };
}

// Export URLs for direct use
export { GPU_BACKEND_URL, RENDER_BACKEND_URL };
