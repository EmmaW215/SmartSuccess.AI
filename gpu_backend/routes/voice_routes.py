"""
SmartSuccess.AI GPU Backend - Voice Routes
ASR (Speech-to-Text) and TTS (Text-to-Speech) endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import logging
import io
import base64

from models.schemas import (
    TranscriptionRequest,
    TranscriptionResponse,
    TTSRequest,
    TTSResponse,
    VoicePreset,
    EmotionStyle
)
from services import get_voice_service, VoiceService
from config import is_gpu_available

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])


def get_service() -> VoiceService:
    """Dependency to get voice service"""
    return get_voice_service()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, etc.)"),
    language: str = Form(default="en"),
    task: str = Form(default="transcribe"),
    word_timestamps: bool = Form(default=False),
    initial_prompt: Optional[str] = Form(default=None),
    service: VoiceService = Depends(get_service)
):
    """
    Transcribe audio using Whisper large-v3
    
    Upload an audio file to get a text transcription.
    Supports multiple audio formats (WAV, MP3, M4A, etc.)
    
    Args:
        audio: Audio file to transcribe
        language: Language code (default: "en")
        task: "transcribe" or "translate" (to English)
        word_timestamps: Include word-level timestamps
        initial_prompt: Optional context for better transcription
        
    Returns:
        TranscriptionResponse with text and metadata
    """
    if not is_gpu_available():
        raise HTTPException(
            status_code=503,
            detail="GPU not available. Use Web Speech API for transcription."
        )
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Create request
        request = TranscriptionRequest(
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            initial_prompt=initial_prompt
        )
        
        # Transcribe
        response = await service.transcribe(audio_data, request)
        
        logger.info(f"Transcribed {audio.filename}: {len(response.text)} chars")
        return response
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe/base64", response_model=TranscriptionResponse)
async def transcribe_base64(
    audio_base64: str,
    language: str = "en",
    task: str = "transcribe",
    word_timestamps: bool = False,
    initial_prompt: Optional[str] = None,
    service: VoiceService = Depends(get_service)
):
    """
    Transcribe base64-encoded audio
    
    Alternative endpoint for sending audio as base64 string.
    
    Args:
        audio_base64: Base64-encoded audio data
        language: Language code
        task: "transcribe" or "translate"
        word_timestamps: Include word-level timestamps
        initial_prompt: Optional context
        
    Returns:
        TranscriptionResponse with text and metadata
    """
    if not is_gpu_available():
        raise HTTPException(
            status_code=503,
            detail="GPU not available. Use Web Speech API for transcription."
        )
    
    try:
        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        
        # Create request
        request = TranscriptionRequest(
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            initial_prompt=initial_prompt
        )
        
        # Transcribe
        response = await service.transcribe(audio_data, request)
        return response
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(
    request: TTSRequest,
    service: VoiceService = Depends(get_service)
):
    """
    Synthesize speech using XTTS-v2
    
    Generate natural-sounding speech from text with voice presets.
    
    Args:
        request: Text, voice preset, emotion, and speed settings
        
    Returns:
        TTSResponse with base64-encoded audio
    """
    if not is_gpu_available():
        raise HTTPException(
            status_code=503,
            detail="GPU not available. Use Web Speech API for TTS."
        )
    
    try:
        response = await service.synthesize(request)
        logger.info(f"Synthesized {len(request.text)} chars -> {response.duration_seconds:.2f}s audio")
        return response
        
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize/stream")
async def synthesize_stream(
    text: str = Form(...),
    voice_preset: VoicePreset = Form(default=VoicePreset.PROFESSIONAL_MALE),
    emotion: EmotionStyle = Form(default=EmotionStyle.NEUTRAL),
    speed: float = Form(default=1.0),
    service: VoiceService = Depends(get_service)
):
    """
    Synthesize speech and return as streaming audio
    
    Returns audio as a streaming response instead of base64.
    Useful for direct audio playback.
    
    Args:
        text: Text to synthesize
        voice_preset: Voice preset to use
        emotion: Emotion style
        speed: Speech speed (0.5 to 2.0)
        
    Returns:
        Streaming audio response (WAV format)
    """
    if not is_gpu_available():
        raise HTTPException(
            status_code=503,
            detail="GPU not available. Use Web Speech API for TTS."
        )
    
    try:
        request = TTSRequest(
            text=text,
            voice_preset=voice_preset,
            emotion=emotion,
            speed=speed
        )
        
        response = await service.synthesize(request)
        
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(response.audio_base64)
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS streaming failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def list_voice_presets():
    """
    List available voice presets
    
    Returns:
        List of available voice presets with descriptions
    """
    presets = [
        {
            "id": VoicePreset.PROFESSIONAL_MALE.value,
            "name": "Professional Male",
            "description": "Professional male interviewer voice"
        },
        {
            "id": VoicePreset.PROFESSIONAL_FEMALE.value,
            "name": "Professional Female",
            "description": "Professional female interviewer voice"
        },
        {
            "id": VoicePreset.FRIENDLY_MALE.value,
            "name": "Friendly Male",
            "description": "Friendly, approachable male voice"
        },
        {
            "id": VoicePreset.FRIENDLY_FEMALE.value,
            "name": "Friendly Female",
            "description": "Friendly, approachable female voice"
        },
        {
            "id": VoicePreset.NEUTRAL.value,
            "name": "Neutral",
            "description": "Neutral, professional voice"
        }
    ]
    
    return {"presets": presets}


@router.get("/status")
async def voice_status(
    service: VoiceService = Depends(get_service)
):
    """
    Get voice service status
    
    Returns:
        Status of Whisper and TTS models
    """
    return service.get_status()


@router.post("/unload")
async def unload_models(
    service: VoiceService = Depends(get_service)
):
    """
    Unload voice models to free GPU memory
    
    Admin endpoint to free GPU resources.
    
    Returns:
        Confirmation of unload
    """
    service.unload_models()
    return {"status": "success", "message": "Voice models unloaded"}
