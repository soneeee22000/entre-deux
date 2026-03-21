import { useState, useRef } from "react";
import { FlaskConical, Camera, Upload } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { usePatient } from "@/lib/use-patient";
import { useAsyncData, getErrorMessage } from "@/lib/use-async-data";
import { api, ApiRequestError } from "@/lib/api";
import { fileToBase64, formatDate } from "@/lib/utils";
import { getObservationDisplay, type FhirObservation } from "@/lib/fhir";

export function LabResultsPage() {
  const { patientId } = usePatient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [analysisResult, setAnalysisResult] = useState<string>("");

  const {
    data: observations,
    error: loadError,
    isLoading: isLoadingHistory,
    retry,
  } = useAsyncData(() => api.listObservations(patientId!), [patientId]);

  async function handleFileSelect(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !patientId) return;

    setSubmitError("");
    setIsAnalyzing(true);
    setAnalysisResult("");

    try {
      const base64 = await fileToBase64(file);
      const result = await api.analyzeLabImage({
        patient_id: patientId,
        image_base64: base64,
      });

      const explanation =
        typeof result.explanation === "string" ? result.explanation : "";
      setAnalysisResult(explanation);

      retry();
    } catch (err: unknown) {
      if (
        err instanceof ApiRequestError &&
        (err.status === 502 || err.status === 504)
      ) {
        setSubmitError(getErrorMessage(err));
      } else {
        setSubmitError(
          "L'analyse de l'image a echoue. Verifiez que la photo est lisible et reessayez.",
        );
      }
    } finally {
      setIsAnalyzing(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  const displayObservations = observations ?? [];

  return (
    <div>
      <PageHeader title="Mes analyses" />

      <div className="px-4 py-4 flex flex-col gap-6">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFileSelect}
        />

        <div className="flex gap-3">
          <Button
            className="flex-1"
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnalyzing}
          >
            <Camera size={18} className="mr-2" />
            Photo
          </Button>
          <Button
            variant="secondary"
            className="flex-1"
            onClick={() => {
              if (fileInputRef.current) {
                fileInputRef.current.removeAttribute("capture");
                fileInputRef.current.click();
                fileInputRef.current.setAttribute("capture", "environment");
              }
            }}
            disabled={isAnalyzing}
          >
            <Upload size={18} className="mr-2" />
            Fichier
          </Button>
        </div>

        {submitError && (
          <p className="text-destructive text-sm" role="alert">
            {submitError}
          </p>
        )}

        {isAnalyzing && (
          <LoadingSpinner message="Analyse en cours... Cela peut prendre quelques secondes." />
        )}

        {analysisResult && (
          <Card className="border-accent/40 bg-accent/5">
            <h3 className="font-semibold font-[var(--font-heading)] mb-2">
              Explication
            </h3>
            <p className="text-base text-foreground whitespace-pre-line">
              {analysisResult}
            </p>
          </Card>
        )}

        <div>
          <h2 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
            Historique des resultats
          </h2>

          {loadError && <ErrorBanner message={loadError} onRetry={retry} />}

          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : !loadError && displayObservations.length === 0 ? (
            <EmptyState
              icon={<FlaskConical size={40} />}
              title="Aucun resultat"
              description="Prenez en photo vos resultats d'analyse ou saisissez-les manuellement."
            />
          ) : !loadError ? (
            <div className="flex flex-col gap-2">
              {displayObservations.map((obs) => (
                <ObservationCard key={obs.id} observation={obs} />
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function ObservationCard({ observation }: { observation: FhirObservation }) {
  const display = getObservationDisplay(observation);
  const date = observation.effectiveDateTime
    ? formatDate(observation.effectiveDateTime)
    : "";

  return (
    <Card>
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="font-medium text-base text-foreground">
            {display.name}
          </p>
          <p className="text-sm text-muted-foreground">{date}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-lg font-semibold">
            {display.value} {display.unit}
          </span>
          {display.isOutOfRange && (
            <Badge variant="destructive">Hors norme</Badge>
          )}
        </div>
      </div>
    </Card>
  );
}
