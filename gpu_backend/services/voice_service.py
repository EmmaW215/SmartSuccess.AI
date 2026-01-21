"""
SmartSuccess.AI GPU Backend - Voice Service
Advanced ASR (Whisper) and TTS (XTTS-v2) for realistic interview experience
"""

import torch
import numpy as np
import whisper
from TTS.api import TTS
import io
import base64
import logging
import time
import tempfile
import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import soundfile as sf
import librosa
import noisereduce as nr

from config import get_settings, get_model_config, get_device, is_gpu_available, get_data_path
from models.schemas import (
    TranscriptionRequest,
    TranscriptionResponse,
    TTSRequest,
    TTSResponse,
    VoicePreset,
    EmotionStyle
)

logger = logging.getLogger(__name__)


# Voice preset configurations
VOICE_PRESETS = {
    VoicePreset.PROFESSIONAL_MALE: {
        "speaker_wav": "professional_male.wav",
        "speed": 1.0,
        "description": "Professional male interviewer voice"
    },
    VoicePreset.PROFESSIONAL_FEMALE: {
        "speaker_wav": "professional_female.wav",
        "speed": 1.0,
        "description": "Professional female interviewer voice"
    },
    VoicePreset.FRIENDLY_MALE: {
        "speaker_wav": "friendly_male.wav",
        "speed": 1.05,
        "description": "Friendly, approachable male voice"
    },
    VoicePreset.FRIENDLY_FEMALE: {
        "speaker_wav": "friendly_female.wav",
        "speed": 1.05,
        "description": "Friendly, approachable female voice"
    },
    VoicePreset.NEUTRAL: {
        "speaker_wav": "neutral.wav",
        "speed": 1.0,
        "description": "Neutral, professional voice"
    }
}


class VoiceService:
    """
    Advanced voice service for interview simulation
    
    Features:
    - Whisper large-v3 for high-accuracy transcription
    - XTTS-v2 for natural-sounding speech synthesis
    - Voice presets for different interviewer styles
    - Audio enhancement (noise reduction, normalization)
    - GPU-accelerated for real-time performance
    """
    
    _instance: Optional["VoiceService"] = None
    
    def __new__(cls):
        """Singleton pattern for model efficiency"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = get_settings()
        self.model_config = get_model_config()
        self.device = get_device()
        
        self.whisper_model: Optional[whisper.Whisper] = None
        self.tts_model: Optional[TTS] = None
        self.voice_presets_dir = get_data_path("voice_presets")
        
        self._initialized = True
        logger.info(f"VoiceService initialized on device: {self.device}")
    
    def load_whisper(self) -> bool:
        """Load Whisper ASR model"""
        if self.whisper_model is not None:
            return True
            
        try:
            logger.info(f"Loading Whisper model: {self.model_config.WHISPER_MODEL_SIZE}")
            start_time = time.time()
            
            self.whisper_model = whisper.load_model(
                self.model_config.WHISPER_MODEL_SIZE,
                device=self.device
            )
            
            # Optimize for inference
            if self.device == "cuda":
                self.whisper_model = self.whisper_model.half()
            
            load_time = time.time() - start_time
            logger.info(f"Whisper model loaded in {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    def load_tts(self) -> bool:
        """Load TTS model (XTTS-v2)"""
        if self.tts_model is not None:
            return True
            
        try:
            logger.info(f"Loading TTS model: {self.model_config.TTS_MODEL_NAME}")
            start_time = time.time()
            
            self.tts_model = TTS(self.model_config.TTS_MODEL_NAME)
            
            if self.device == "cuda":
                self.tts_model.to(self.device)
            
            load_time = time.time() - start_time
            logger.info(f"TTS model loaded in {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            return False
    
    async def transcribe(
        self,
        audio_data: bytes,
        request: TranscriptionRequest
    ) -> TranscriptionResponse:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_data: Audio bytes (WAV, MP3, etc.)
            request: Transcription settings
            
        Returns:
            TranscriptionResponse with text and metadata
        """
        start_time = time.time()
        
        if not self.load_whisper():
            raise RuntimeError("Whisper model not available")
        
        try:
            # Save audio to temp file (Whisper requires file path)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            # Load and preprocess audio
            audio = whisper.load_audio(tmp_path)
            audio = whisper.pad_or_trim(audio)
            
            # Get duration
            duration = len(audio) / 16000  # Whisper uses 16kHz
            
            # Transcribe
            result = self.whisper_model.transcribe(
                audio,
                language=request.language,
                task=request.task,
                fp16=(self.device == "cuda"),
                verbose=False,
                word_timestamps=request.word_timestamps,
                initial_prompt=request.initial_prompt
            )
            
            # Clean up
            os.unlink(tmp_path)
            
            # Calculate confidence from segments
            confidence = None
            if result.get("segments"):
                avg_prob = np.mean([
                    s.get("avg_logprob", 0) 
                    for s in result["segments"]
                ])
                confidence = min(1.0, np.exp(avg_prob))
            
            processing_time = (time.time() - start_time) * 1000
            
            return TranscriptionResponse(
                text=result["text"].strip(),
                language=result.get("language", request.language),
                duration_seconds=duration,
                segments=result.get("segments"),
                word_timestamps=self._extract_word_timestamps(result) if request.word_timestamps else None,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def _extract_word_timestamps(self, result: Dict) -> list:
        """Extract word-level timestamps from Whisper result"""
        words = []
        for segment in result.get("segments", []):
            for word in segment.get("words", []):
                words.append({
                    "word": word.get("word", ""),
                    "start": word.get("start", 0),
                    "end": word.get("end", 0),
                    "probability": word.get("probability", 0)
                })
        return words
    
    async def synthesize(
        self,
        request: TTSRequest
    ) -> TTSResponse:
        """
        Synthesize speech using XTTS-v2
        
        Args:
            request: TTS settings including text and voice preset
            
        Returns:
            TTSResponse with audio data
        """
        start_time = time.time()
        
        if not self.load_tts():
            raise RuntimeError("TTS model not available")
        
        try:
            # Get voice preset configuration
            preset_config = VOICE_PRESETS.get(
                request.voice_preset,
                VOICE_PRESETS[VoicePreset.PROFESSIONAL_MALE]
            )
            
            # Get speaker reference audio
            speaker_wav = self._get_speaker_wav(preset_config["speaker_wav"])
            
            # Apply emotion/style adjustments to text
            text = self._apply_emotion_markers(request.text, request.emotion)
            
            # Calculate effective speed
            speed = request.speed * preset_config.get("speed", 1.0)
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                self.tts_model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=request.language,
                    file_path=tmp.name,
                    speed=speed
                )
                
                # Read generated audio
                audio, sr = sf.read(tmp.name)
                os.unlink(tmp.name)
            
            # Apply post-processing
            audio = self._enhance_audio(audio, sr)
            
            # Convert to base64
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, audio, sr, format='WAV')
            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
            
            duration = len(audio) / sr
            processing_time = (time.time() - start_time) * 1000
            
            return TTSResponse(
                audio_base64=audio_base64,
                duration_seconds=duration,
                sample_rate=sr,
                format="wav",
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
    
    def _get_speaker_wav(self, filename: str) -> str:
        """Get path to speaker reference audio"""
        # Check in voice presets directory
        preset_path = os.path.join(self.voice_presets_dir, filename)
        if os.path.exists(preset_path):
            return preset_path
        
        # Use default if preset not found
        default_path = os.path.join(self.voice_presets_dir, "default.wav")
        if os.path.exists(default_path):
            return default_path
        
        # Create a minimal placeholder if nothing exists
        logger.warning(f"Voice preset not found: {filename}, using generated placeholder")
        return self._create_placeholder_speaker()
    
    def _create_placeholder_speaker(self) -> str:
        """Create a placeholder speaker wav for testing"""
        # Generate a simple sine wave as placeholder
        import numpy as np
        
        sr = 22050
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.3 * np.sin(2 * np.pi * 220 * t)  # 220 Hz sine wave
        
        placeholder_path = os.path.join(self.voice_presets_dir, "placeholder.wav")
        os.makedirs(self.voice_presets_dir, exist_ok=True)
        sf.write(placeholder_path, audio, sr)
        
        return placeholder_path
    
    def _apply_emotion_markers(self, text: str, emotion: EmotionStyle) -> str:
        """Apply emotion markers to text for more natural TTS"""
        # XTTS-v2 can use certain patterns to influence prosody
        emotion_prefixes = {
            EmotionStyle.NEUTRAL: "",
            EmotionStyle.ENCOURAGING: "Speaking warmly and encouragingly: ",
            EmotionStyle.SERIOUS: "Speaking professionally and seriously: ",
            EmotionStyle.WARM: "Speaking in a warm, friendly manner: "
        }
        
        # For now, just return the text
        # In production, could use more sophisticated prosody control
        return text
    
    def _enhance_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply audio post-processing for better quality"""
        try:
            # Reduce background noise
            audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                prop_decrease=0.6
            )
            
            # Normalize volume
            audio = librosa.util.normalize(audio)
            
            return audio
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed: {e}")
            return audio
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice service status"""
        return {
            "whisper_loaded": self.whisper_model is not None,
            "tts_loaded": self.tts_model is not None,
            "device": self.device,
            "whisper_model": self.model_config.WHISPER_MODEL_SIZE,
            "tts_model": self.model_config.TTS_MODEL_NAME,
            "available_presets": list(VOICE_PRESETS.keys())
        }
    
    def unload_models(self):
        """Unload models to free GPU memory"""
        if self.whisper_model is not None:
            del self.whisper_model
            self.whisper_model = None
            
        if self.tts_model is not None:
            del self.tts_model
            self.tts_model = None
            
        if self.device == "cuda":
            torch.cuda.empty_cache()
            
        logger.info("Voice models unloaded")


class VoiceServiceFallback:
    """
    Fallback voice service for when GPU is unavailable
    Uses Web Speech API (handled by frontend) with basic audio processing
    """
    
    async def transcribe(
        self,
        audio_data: bytes,
        request: TranscriptionRequest
    ) -> TranscriptionResponse:
        """Fallback transcription - returns error indicating frontend should use Web Speech API"""
        return TranscriptionResponse(
            text="",
            language=request.language,
            duration_seconds=0,
            segments=None,
            word_timestamps=None,
            confidence=None,
            processing_time_ms=0
        )
    
    async def synthesize(
        self,
        request: TTSRequest
    ) -> TTSResponse:
        """Fallback TTS - returns error indicating frontend should use Web Speech API"""
        return TTSResponse(
            audio_base64="",
            duration_seconds=0,
            sample_rate=22050,
            format="wav",
            processing_time_ms=0
        )


# Singleton accessor
_voice_service: Optional[VoiceService] = None

def get_voice_service() -> VoiceService:
    """Get the voice service singleton"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service


def get_voice_service_with_fallback() -> VoiceService:
    """Get voice service with fallback for non-GPU environments"""
    if is_gpu_available():
        return get_voice_service()
    else:
        logger.warning("GPU not available, using fallback voice service")
        return VoiceServiceFallback()
