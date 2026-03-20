import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  message?: string;
  className?: string;
}

export function LoadingSpinner({ message, className }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center gap-3 py-8", className)}>
      <div className="h-8 w-8 animate-spin rounded-full border-3 border-muted border-t-primary" />
      {message && <p className="text-muted-foreground text-base">{message}</p>}
    </div>
  );
}
