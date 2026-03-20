import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description?: string;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-3 py-12 text-center",
        className,
      )}
    >
      <div className="text-muted-foreground">{icon}</div>
      <p className="text-lg font-medium text-foreground">{title}</p>
      {description && (
        <p className="text-muted-foreground text-base max-w-xs">
          {description}
        </p>
      )}
    </div>
  );
}
