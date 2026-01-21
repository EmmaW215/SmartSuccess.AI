"""
SmartSuccess.AI GPU Backend - Health Routes
Health check and status endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import torch
import time
import psutil
import platform

from config import get_settings, is_gpu_available
from models.schemas import HealthStatus, GPUStatus

router = APIRouter(tags=["Health"])

# Track server start time
SERVER_START_TIME = time.time()


@router.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "SmartSuccess.AI GPU Backend",
        "version": get_settings().APP_VERSION,
        "status": "running"
    }


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Comprehensive health check endpoint
    
    Returns:
        HealthStatus with GPU, memory, and service information
    """
    settings = get_settings()
    
    # GPU status
    gpu_available = is_gpu_available()
    gpu_memory_free = None
    gpu_memory_total = None
    gpu_utilization = None
    
    if gpu_available:
        try:
            gpu_memory_free = torch.cuda.mem_get_info()[0] / (1024**3)  # GB
            gpu_memory_total = torch.cuda.mem_get_info()[1] / (1024**3)  # GB
            
            # Try to get utilization via nvidia-smi
            try:
                import subprocess
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    gpu_utilization = float(result.stdout.strip())
            except:
                pass
        except:
            pass
    
    # Check which models are loaded
    models_loaded = {}
    try:
        from services import get_embedding_service, get_voice_service, get_prerag_service
        
        embedding_service = get_embedding_service()
        models_loaded["embedding"] = embedding_service.model is not None
        
        voice_service = get_voice_service()
        models_loaded["whisper"] = voice_service.whisper_model is not None
        models_loaded["tts"] = voice_service.tts_model is not None
        
        prerag_service = get_prerag_service()
        models_loaded["prerag"] = len(prerag_service.collections) > 0
    except:
        pass
    
    # Get active sessions count
    active_requests = 0
    try:
        from services import get_gpu_interview_service
        interview_service = get_gpu_interview_service()
        active_requests = interview_service.get_active_sessions_count()
    except:
        pass
    
    uptime = time.time() - SERVER_START_TIME
    
    return HealthStatus(
        status="healthy" if gpu_available else "degraded",
        gpu_available=gpu_available,
        gpu_memory_free=gpu_memory_free,
        gpu_memory_total=gpu_memory_total,
        gpu_utilization=gpu_utilization,
        active_requests=active_requests,
        models_loaded=models_loaded,
        uptime_seconds=uptime,
        version=settings.APP_VERSION
    )


@router.get("/gpu/status", response_model=GPUStatus)
async def gpu_status():
    """
    Detailed GPU status endpoint
    
    Returns:
        GPUStatus with comprehensive GPU information
    """
    if not is_gpu_available():
        return GPUStatus(available=False)
    
    try:
        device_name = torch.cuda.get_device_name(0)
        memory_total = torch.cuda.mem_get_info()[1] / (1024**3)
        memory_free = torch.cuda.mem_get_info()[0] / (1024**3)
        memory_used = memory_total - memory_free
        
        # Get additional info via nvidia-smi
        utilization = None
        temperature = None
        try:
            import subprocess
            
            # Get utilization
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                utilization = float(result.stdout.strip())
            
            # Get temperature
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                temperature = float(result.stdout.strip())
        except:
            pass
        
        return GPUStatus(
            available=True,
            device_name=device_name,
            memory_total_gb=round(memory_total, 2),
            memory_used_gb=round(memory_used, 2),
            memory_free_gb=round(memory_free, 2),
            utilization_percent=utilization,
            temperature_celsius=temperature,
            cuda_version=torch.version.cuda
        )
        
    except Exception as e:
        return GPUStatus(available=False)


@router.get("/system/info")
async def system_info():
    """
    System information endpoint
    
    Returns:
        System resource information
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "system": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        },
        "cpu": {
            "count": psutil.cpu_count(),
            "physical_count": psutil.cpu_count(logical=False),
            "percent": cpu_percent
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
    }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe
    
    Returns 200 if service is ready to accept requests
    """
    # Check if essential services are available
    try:
        from services import get_prerag_service
        prerag_service = get_prerag_service()
        
        if not prerag_service.collections:
            raise HTTPException(status_code=503, detail="Pre-RAG not initialized")
        
        return {"ready": True}
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe
    
    Returns 200 if service is alive
    """
    return {"alive": True}
