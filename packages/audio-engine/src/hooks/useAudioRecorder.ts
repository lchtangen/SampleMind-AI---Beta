import { useState, useRef, useCallback, useEffect } from 'react';

// Type for the hook's return value
interface UseAudioRecorderReturn {
  isRecording: boolean;
  audioBlob: Blob | null;
  audioUrl: string | null;
  error: string | null;
  audioData: Uint8Array;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob>;
}

// Extend the Window interface to include webkit prefixed APIs
declare global {
  interface Window {
    webkitAudioContext: new (contextOptions?: AudioContextOptions) => AudioContext;
    webkitMediaRecorder: typeof MediaRecorder;
  }
}

// Declare types for the Web Audio API
declare const AudioContext: {
  new (contextOptions?: AudioContextOptions): AudioContext;
  prototype: AudioContext;
};

declare const MediaRecorder: {
  new (stream: MediaStream, options?: MediaRecorderOptions): MediaRecorder;
  isTypeSupported(type: string): boolean;
};

interface AudioContext extends BaseAudioContext {
  createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
  createAnalyser(): AnalyserNode;
  close(): Promise<void>;
  state: AudioContextState;
  resume(): Promise<void>;
  suspend(): Promise<void>;
  sampleRate: number;
}

export const useAudioRecorder = (): UseAudioRecorderReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [audioData, setAudioData] = useState<Uint8Array>(new Uint8Array(0));
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const audioContext = useRef<AudioContext | null>(null);
  const analyser = useRef<AnalyserNode | null>(null);
  const dataArray = useRef<Uint8Array>(new Uint8Array(0));
  const bufferLengthRef = useRef(0);
  const animationFrameId = useRef<number>(0);
  const streamRef = useRef<MediaStream | null>(null);

  const startVisualization = useCallback(() => {
    if (!analyser.current) return;

    const tick = () => {
      if (!analyser.current) return;
      
      const newBufferLength = analyser.current.frequencyBinCount;
      if (dataArray.current.length !== newBufferLength) {
        dataArray.current = new Uint8Array(newBufferLength);
        bufferLengthRef.current = newBufferLength;
      }
      
      const tempArray = new Uint8Array(newBufferLength);
      analyser.current.getByteFrequencyData(tempArray);
      dataArray.current = tempArray;
      setAudioData(new Uint8Array(tempArray));
      
      if (isRecording) {
        animationFrameId.current = window.requestAnimationFrame(tick);
      }
    };

    animationFrameId.current = window.requestAnimationFrame(tick);
  }, [isRecording]);

  const stopVisualization = () => {
    window.cancelAnimationFrame(animationFrameId.current);
  };

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // Set up audio context and analyser
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      audioContext.current = new AudioCtx();
      analyser.current = audioContext.current.createAnalyser();
      analyser.current.fftSize = 2048;
      
      const source = audioContext.current.createMediaStreamSource(stream);
      source.connect(analyser.current);
      
      // Set up media recorder
      const MediaRecorderClass = window.MediaRecorder || window.webkitMediaRecorder;
      mediaRecorder.current = new MediaRecorderClass(stream);
      audioChunks.current = [];
      
      mediaRecorder.current.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };
      
      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        stopVisualization();
      };
      
      mediaRecorder.current.start();
      setIsRecording(true);
      startVisualization();
      
    } catch (err) {
      setError('Could not access microphone. Please check your permissions.');
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = useCallback(async (): Promise<Blob> => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      if (mediaRecorder.current.stream) {
        mediaRecorder.current.stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
      }
      setIsRecording(false);
      return new Blob(audioChunks.current, { type: 'audio/wav' });
    }
    return new Blob();
  }, [isRecording]);

  useEffect(() => {
    return () => {
      if (mediaRecorder.current && isRecording) {
        mediaRecorder.current.stop();
      }
      stopVisualization();
    };
  }, [isRecording]);

  return {
    isRecording,
    audioBlob,
    audioUrl,
    startRecording,
    stopRecording,
    error,
    audioData,
  };
};
