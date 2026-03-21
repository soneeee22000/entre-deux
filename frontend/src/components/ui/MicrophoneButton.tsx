import { Mic, Square } from "lucide-react";

interface MicrophoneButtonProps {
  isRecording: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export function MicrophoneButton({
  isRecording,
  onStart,
  onStop,
  disabled = false,
}: MicrophoneButtonProps) {
  return (
    <button
      type="button"
      onClick={isRecording ? onStop : onStart}
      disabled={disabled}
      aria-label={
        isRecording
          ? "Arreter l'enregistrement"
          : "Enregistrer un message vocal"
      }
      className={`
        relative flex items-center justify-center
        w-11 h-11 min-w-[44px] min-h-[44px]
        rounded-full border-2 transition-colors
        ${
          isRecording
            ? "border-destructive bg-destructive/10 text-destructive"
            : "border-primary bg-primary/10 text-primary hover:bg-primary/20"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      `}
    >
      {isRecording ? (
        <>
          <span className="absolute inset-0 rounded-full animate-ping bg-destructive/20" />
          <Square size={18} className="relative" />
        </>
      ) : (
        <Mic size={18} />
      )}
    </button>
  );
}
