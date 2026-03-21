import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface ErrorFallbackProps {
  error: Error;
  onReset: () => void;
}

export function ErrorFallback({ error, onReset }: ErrorFallbackProps) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <Card className="w-full max-w-sm p-6 text-center">
        <AlertTriangle size={48} className="mx-auto mb-4 text-destructive" />
        <h1 className="text-xl font-bold font-[var(--font-heading)] text-foreground mb-2">
          Quelque chose s'est mal passe
        </h1>
        <p className="text-sm text-muted-foreground mb-6">
          Une erreur inattendue est survenue. Veuillez reessayer ou revenir a
          l'accueil.
        </p>
        {import.meta.env.DEV && (
          <pre className="mb-4 max-h-24 overflow-auto rounded bg-muted p-2 text-left text-xs text-muted-foreground">
            {error.message}
          </pre>
        )}
        <div className="flex flex-col gap-3">
          <Button onClick={onReset} className="w-full">
            Reessayer
          </Button>
          <a
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Retour a l'accueil
          </a>
        </div>
      </Card>
    </div>
  );
}
