import { useState, useEffect, useRef } from "react";
import { FlaskConical, Camera, Upload } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePatient } from "@/lib/use-patient";
import { api } from "@/lib/api";
import { fileToBase64, formatDate } from "@/lib/utils";
import { getObservationDisplay, type FhirObservation } from "@/lib/fhir";

export function LabResultsPage() {
  const { patientId } = usePatient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [analysisResult, setAnalysisResult] = useState<string>("");
  const [observations, setObservations] = useState<FhirObservation[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    api
      .listObservations(patientId)
      .then((data) => {
        if (!cancelled) setObservations(data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  async function handleFileSelect(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !patientId) return;

    setError("");
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

      const newObs = await api.listObservations(patientId);
      setObservations(newObs);
    } catch {
      setError("Quelque chose s'est mal passe. Veuillez reessayer.");
    } finally {
      setIsAnalyzing(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

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

        {error && (
          <p className="text-destructive text-sm" role="alert">
            {error}
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

          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : observations.length === 0 ? (
            <EmptyState
              icon={<FlaskConical size={40} />}
              title="Aucun resultat"
              description="Prenez en photo vos resultats d'analyse ou saisissez-les manuellement."
            />
          ) : (
            <div className="flex flex-col gap-2">
              {observations.map((obs) => (
                <ObservationCard key={obs.id} observation={obs} />
              ))}
            </div>
          )}
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
