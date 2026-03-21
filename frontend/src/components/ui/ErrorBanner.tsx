import { AlertTriangle } from "lucide-react";
import { Button } from "./Button";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4"
    >
      <AlertTriangle size={20} className="text-destructive shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-destructive">{message}</p>
        {onRetry && (
          <Button
            variant="ghost"
            className="text-sm mt-2 min-h-[36px] px-3 text-destructive"
            onClick={onRetry}
          >
            Reessayer
          </Button>
        )}
      </div>
    </div>
  );
}
