import { useCallback, useEffect, useRef, useState } from "react";

type RecorderState = "idle" | "recording" | "processing";

interface UseAudioRecorderReturn {
  state: RecorderState;
  isRecording: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  audioBlob: Blob | null;
  error: string;
  reset: () => void;
}

function getSupportedMimeType(): string {
  const types = ["audio/webm", "audio/mp4", "audio/ogg"];
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return "audio/webm";
}

export function useAudioRecorder(): UseAudioRecorderReturn {
  const [state, setState] = useState<RecorderState>("idle");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    return () => {
      if (recorderRef.current?.state === "recording") {
        recorderRef.current.stop();
      }
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const startRecording = useCallback(async () => {
    setError("");
    setAudioBlob(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = getSupportedMimeType();
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        setAudioBlob(blob);
        setState("idle");
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorder.onerror = () => {
        setError("Erreur d'enregistrement. Verifiez les permissions du micro.");
        setState("idle");
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorderRef.current = recorder;
      recorder.start();
      setState("recording");
    } catch {
      setError("Impossible d'acceder au microphone. Verifiez les permissions.");
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (recorderRef.current?.state === "recording") {
      setState("processing");
      recorderRef.current.stop();
    }
  }, []);

  const reset = useCallback(() => {
    setAudioBlob(null);
    setError("");
    setState("idle");
  }, []);

  return {
    state,
    isRecording: state === "recording",
    startRecording,
    stopRecording,
    audioBlob,
    error,
    reset,
  };
}
