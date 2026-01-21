/**
 * SmartSuccess.AI - useVoiceInterview Hook
 * Advanced voice interview with GPU-powered ASR and TTS
 * Falls back to Web Speech API when GPU is unavailable
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useGPUBackend } from './useGPUBackend';

interface VoiceConfig {
  /** Voice preset for TTS */
  voicePreset: 'professional_male' | 'professional_female' | 'friendly_male' | 'friendly_female' | 'neutral';
  /** Emotion style for TTS */
  emotion: 'neutral' | 'encouraging' | 'serious' | 'warm';
  /** Speech speed (0.5 to 2.0) */
  speed: number;
  /** Language code */
  language: string;
}

interface UseVoiceInterviewOptions {
  /** Whether to use GPU for voice when available */
  useGPU?: boolean;
  /** Voice configuration */
  voiceConfig?: Partial<VoiceConfig>;
  /** Callback when transcription completes */
  onTranscription?: (text: string) => void;
  /** Callback when audio is ready */
  onAudioReady?: (audioBlob: Blob) => void;
  /** Callback for errors */
  onError?: (error: string) => void;
}

interface UseVoiceInterviewReturn {
  /** Whether voice features are available */
  voiceAvailable: boolean;
  /** Whether using GPU (true) or Web Speech API (false) */
  usingGPU: boolean;
  /** Recording state */
  isRecording: boolean;
  /** Processing state (transcribing/synthesizing) */
  isProcessing: boolean;
  /** Current transcription text */
  transcription: string;
  /** Error message */
  error: string | null;
  /** Start recording audio */
  startRecording: () => Promise<void>;
  /** Stop recording and get transcription */
  stopRecording: () => Promise<string>;
  /** Synthesize text to speech */
  speak: (text: string) => Promise<void>;
  /** Stop any playing audio */
  stopSpeaking: () => void;
  /** Check if audio is currently playing */
  isSpeaking: boolean;
}

const DEFAULT_VOICE_CONFIG: VoiceConfig = {
  voicePreset: 'professional_male',
  emotion: 'neutral',
  speed: 1.0,
  language: 'en'
};

/**
 * Hook for voice-enabled interviews
 */
export function useVoiceInterview(options: UseVoiceInterviewOptions = {}): UseVoiceInterviewReturn {
  const {
    useGPU = true,
    voiceConfig: userVoiceConfig,
    onTranscription,
    onAudioReady,
    onError
  } = options;

  const voiceConfig = { ...DEFAULT_VOICE_CONFIG, ...userVoiceConfig };

  // GPU backend hook
  const { gpuAvailable, request: gpuRequest } = useGPUBackend({
    autoCheck: useGPU
  });

  // State
  const [voiceAvailable, setVoiceAvailable] = useState(false);
  const [usingGPU, setUsingGPU] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const webSpeechRecognitionRef = useRef<any>(null);

  // Check voice availability
  useEffect(() => {
    const checkAvailability = async () => {
      // Check Web Speech API availability
      const webSpeechAvailable = 
        typeof window !== 'undefined' &&
        ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);

      // Determine which to use
      if (useGPU && gpuAvailable) {
        setUsingGPU(true);
        setVoiceAvailable(true);
      } else if (webSpeechAvailable) {
        setUsingGPU(false);
        setVoiceAvailable(true);
      } else {
        setVoiceAvailable(false);
      }
    };

    checkAvailability();
  }, [useGPU, gpuAvailable]);

  // Initialize Web Speech Recognition
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;

    if (SpeechRecognition && !usingGPU) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = voiceConfig.language;

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscription(finalTranscript);
          onTranscription?.(finalTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        const errorMessage = `Speech recognition error: ${event.error}`;
        setError(errorMessage);
        onError?.(errorMessage);
      };

      webSpeechRecognitionRef.current = recognition;
    }

    return () => {
      if (webSpeechRecognitionRef.current) {
        try {
          webSpeechRecognitionRef.current.stop();
        } catch {}
      }
    };
  }, [usingGPU, voiceConfig.language, onTranscription, onError]);

  // Start recording
  const startRecording = useCallback(async () => {
    setError(null);
    setTranscription('');

    if (usingGPU) {
      // GPU mode: Record audio for later transcription
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm'
        });

        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start(100); // Collect chunks every 100ms
        setIsRecording(true);

      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to start recording';
        setError(message);
        onError?.(message);
      }

    } else {
      // Web Speech API mode
      if (webSpeechRecognitionRef.current) {
        try {
          webSpeechRecognitionRef.current.start();
          setIsRecording(true);
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Failed to start recognition';
          setError(message);
          onError?.(message);
        }
      }
    }
  }, [usingGPU, onError]);

  // Stop recording and get transcription
  const stopRecording = useCallback(async (): Promise<string> => {
    setIsRecording(false);

    if (usingGPU) {
      // GPU mode: Stop recording and send to Whisper
      return new Promise((resolve, reject) => {
        const mediaRecorder = mediaRecorderRef.current;
        if (!mediaRecorder) {
          reject('No recording in progress');
          return;
        }

        mediaRecorder.onstop = async () => {
          setIsProcessing(true);

          try {
            // Create audio blob
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            onAudioReady?.(audioBlob);

            // Convert to base64
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            
            reader.onloadend = async () => {
              const base64Audio = (reader.result as string).split(',')[1];

              try {
                // Send to GPU backend
                const result = await gpuRequest<{
                  text: string;
                  confidence: number;
                  processing_time_ms: number;
                }>('/api/voice/transcribe/base64', {
                  method: 'POST',
                  body: JSON.stringify({
                    audio_base64: base64Audio,
                    language: voiceConfig.language
                  })
                }, true);

                setTranscription(result.text);
                onTranscription?.(result.text);
                resolve(result.text);

              } catch (err) {
                // Fallback to Web Speech API hint
                const message = 'GPU transcription failed - please try again';
                setError(message);
                onError?.(message);
                reject(err);
              } finally {
                setIsProcessing(false);
              }
            };

          } catch (err) {
            setIsProcessing(false);
            reject(err);
          }

          // Stop media stream
          mediaRecorder.stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.stop();
      });

    } else {
      // Web Speech API mode
      if (webSpeechRecognitionRef.current) {
        webSpeechRecognitionRef.current.stop();
      }
      return transcription;
    }
  }, [usingGPU, transcription, voiceConfig.language, gpuRequest, onTranscription, onAudioReady, onError]);

  // Synthesize text to speech
  const speak = useCallback(async (text: string) => {
    if (!text) return;

    setError(null);
    setIsSpeaking(true);

    if (usingGPU) {
      // GPU mode: Use XTTS
      setIsProcessing(true);

      try {
        const result = await gpuRequest<{
          audio_base64: string;
          duration_seconds: number;
          sample_rate: number;
        }>('/api/voice/synthesize', {
          method: 'POST',
          body: JSON.stringify({
            text,
            voice_preset: voiceConfig.voicePreset,
            emotion: voiceConfig.emotion,
            speed: voiceConfig.speed,
            language: voiceConfig.language
          })
        }, true);

        // Play audio
        const audioData = atob(result.audio_base64);
        const audioArray = new Uint8Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          audioArray[i] = audioData.charCodeAt(i);
        }

        const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        const audio = new Audio(audioUrl);
        currentAudioRef.current = audio;

        audio.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = () => {
          setIsSpeaking(false);
          setError('Audio playback failed');
          URL.revokeObjectURL(audioUrl);
        };

        await audio.play();

      } catch (err) {
        const message = err instanceof Error ? err.message : 'TTS failed';
        setError(message);
        onError?.(message);
        setIsSpeaking(false);

        // Fallback to Web Speech API
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = voiceConfig.speed;
          utterance.onend = () => setIsSpeaking(false);
          utterance.onerror = () => setIsSpeaking(false);
          speechSynthesis.speak(utterance);
        }
      } finally {
        setIsProcessing(false);
      }

    } else {
      // Web Speech API mode
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = voiceConfig.speed;
        utterance.lang = voiceConfig.language;
        
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => {
          setIsSpeaking(false);
          setError('Speech synthesis failed');
        };

        speechSynthesis.speak(utterance);
      } else {
        setIsSpeaking(false);
        setError('Speech synthesis not supported');
      }
    }
  }, [usingGPU, voiceConfig, gpuRequest, onError]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }

    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }

    setIsSpeaking(false);
  }, []);

  return {
    voiceAvailable,
    usingGPU,
    isRecording,
    isProcessing,
    transcription,
    error,
    startRecording,
    stopRecording,
    speak,
    stopSpeaking,
    isSpeaking
  };
}

export default useVoiceInterview;
