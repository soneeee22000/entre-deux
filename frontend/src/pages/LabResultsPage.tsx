import { useState, useRef } from "react";
import {
  FlaskConical,
  Camera,
  Upload,
  TrendingDown,
  TrendingUp,
  Minus,
} from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { usePatient } from "@/lib/use-patient";
import { useAsyncData, getErrorMessage } from "@/lib/use-async-data";
import { api, ApiRequestError } from "@/lib/api";
import { fileToBase64, formatDate } from "@/lib/utils";
import { getObservationDisplay, type FhirObservation } from "@/lib/fhir";

interface ObservationGroup {
  code: string;
  name: string;
  unit: string;
  refLow: number | undefined;
  refHigh: number | undefined;
  readings: Array<{
    value: number;
    date: string;
    isOutOfRange: boolean;
  }>;
}

const EXPLANATIONS: Record<
  string,
  (latest: number, first: number, improving: boolean) => string
> = {
  "59261-8": (latest, first, improving) =>
    improving
      ? `Votre HbA1c est passe de ${first}% a ${latest}%. C'est une tres bonne amelioration qui montre que votre traitement fonctionne.`
      : `Votre HbA1c est a ${latest}%. Discutez avec votre medecin des ajustements possibles.`,
  "2339-0": (latest, first, improving) =>
    improving
      ? `Votre glycemie a jeun s'ameliore : de ${first} a ${latest} mmol/L. Continuez vos efforts.`
      : `Votre glycemie a jeun est a ${latest} mmol/L. Parlez-en a votre medecin.`,
  "2093-3": (latest, first, improving) =>
    improving
      ? `Votre cholesterol baisse : de ${first} a ${latest} mmol/L. Vos habitudes alimentaires portent leurs fruits.`
      : `Votre cholesterol est a ${latest} mmol/L. Un suivi dietetique pourrait aider.`,
  "2160-0": (latest) =>
    `Votre creatinine est a ${latest} umol/L. C'est dans la zone normale, votre fonction renale est preservee.`,
};

function groupObservations(
  observations: FhirObservation[],
): ObservationGroup[] {
  const groups = new Map<string, ObservationGroup>();

  for (const obs of observations) {
    const display = getObservationDisplay(obs);
    const code = obs.code?.coding?.[0]?.code ?? "unknown";
    const value = obs.valueQuantity?.value;
    if (value === undefined) continue;

    const range = obs.referenceRange?.[0];

    if (!groups.has(code)) {
      groups.set(code, {
        code,
        name: display.name,
        unit: display.unit,
        refLow: range?.low?.value,
        refHigh: range?.high?.value,
        readings: [],
      });
    }

    groups.get(code)!.readings.push({
      value,
      date: obs.effectiveDateTime ?? "",
      isOutOfRange: display.isOutOfRange,
    });
  }

  for (const group of groups.values()) {
    group.readings.sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );
  }

  return Array.from(groups.values());
}

function getTrend(
  readings: ObservationGroup["readings"],
  refHigh: number | undefined,
): "improving" | "stable" | "worsening" {
  if (readings.length < 2) return "stable";
  const first = readings[0].value;
  const latest = readings[readings.length - 1].value;
  const diff = latest - first;
  const threshold = Math.abs(first) * 0.03;

  if (Math.abs(diff) < threshold) return "stable";

  if (refHigh !== undefined && first > refHigh) {
    return diff < 0 ? "improving" : "worsening";
  }
  return diff > 0 ? "worsening" : "improving";
}

function getSeverity(
  value: number,
  refLow: number | undefined,
  refHigh: number | undefined,
): "normal" | "borderline" | "high" {
  if (refHigh !== undefined && value > refHigh) {
    const overshoot = ((value - refHigh) / refHigh) * 100;
    return overshoot > 20 ? "high" : "borderline";
  }
  if (refLow !== undefined && value < refLow) {
    const undershoot = ((refLow - value) / refLow) * 100;
    return undershoot > 20 ? "high" : "borderline";
  }
  return "normal";
}

const SEVERITY_STYLES = {
  normal: "text-accent",
  borderline: "text-primary",
  high: "text-destructive",
} as const;

const SEVERITY_BG = {
  normal: "bg-accent",
  borderline: "bg-primary",
  high: "bg-destructive",
} as const;

const TREND_CONFIG = {
  improving: {
    icon: TrendingDown,
    label: "En amelioration",
    className: "text-accent",
  },
  stable: { icon: Minus, label: "Stable", className: "text-muted-foreground" },
  worsening: {
    icon: TrendingUp,
    label: "En hausse",
    className: "text-destructive",
  },
} as const;

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
  const groups = groupObservations(displayObservations);

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
            Mes resultats
          </h2>

          {loadError && <ErrorBanner message={loadError} onRetry={retry} />}

          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : !loadError && groups.length === 0 ? (
            <EmptyState
              icon={<FlaskConical size={40} />}
              title="Aucun resultat"
              description="Prenez en photo vos resultats d'analyse ou saisissez-les manuellement."
            />
          ) : !loadError ? (
            <div className="flex flex-col gap-4">
              {groups.map((group) => (
                <ObservationGroupCard key={group.code} group={group} />
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function ObservationGroupCard({ group }: { group: ObservationGroup }) {
  const [expanded, setExpanded] = useState(false);
  const latest = group.readings[group.readings.length - 1];
  const trend = getTrend(group.readings, group.refHigh);
  const severity = getSeverity(latest.value, group.refLow, group.refHigh);
  const TrendIcon = TREND_CONFIG[trend].icon;

  const first = group.readings[0];
  const explainFn = EXPLANATIONS[group.code];
  const explanation = explainFn
    ? explainFn(latest.value, first.value, trend === "improving")
    : null;

  return (
    <Card
      className="cursor-pointer"
      onClick={() => setExpanded(!expanded)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          setExpanded(!expanded);
        }
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-base text-foreground">
            {group.name}
          </p>
          <div className="flex items-center gap-1 mt-1">
            <TrendIcon size={14} className={TREND_CONFIG[trend].className} />
            <span
              className={`text-xs font-medium ${TREND_CONFIG[trend].className}`}
            >
              {TREND_CONFIG[trend].label}
            </span>
          </div>
        </div>
        <div className="text-right shrink-0">
          <span className={`text-2xl font-bold ${SEVERITY_STYLES[severity]}`}>
            {latest.value}
          </span>
          <span className="text-sm text-muted-foreground ml-1">
            {group.unit}
          </span>
        </div>
      </div>

      <RangeBar
        value={latest.value}
        refLow={group.refLow}
        refHigh={group.refHigh}
        severity={severity}
      />

      {group.readings.length > 1 && (
        <div className="flex items-center gap-1 mt-2">
          {group.readings.map((reading, idx) => (
            <span
              key={idx}
              className={`text-xs ${idx === group.readings.length - 1 ? "font-bold" : "text-muted-foreground"}`}
            >
              {reading.value}
              {idx < group.readings.length - 1 && (
                <span className="text-muted-foreground mx-1">&rarr;</span>
              )}
            </span>
          ))}
          <span className="text-xs text-muted-foreground ml-1">
            {group.unit}
          </span>
        </div>
      )}

      {expanded && (
        <div className="mt-3 pt-3 border-t border-border flex flex-col gap-3">
          {explanation && (
            <p className="text-sm text-foreground leading-relaxed">
              {explanation}
            </p>
          )}

          {(group.refLow !== undefined || group.refHigh !== undefined) && (
            <p className="text-xs text-muted-foreground">
              Valeurs de reference :{" "}
              {group.refLow !== undefined && group.refHigh !== undefined
                ? `${group.refLow} – ${group.refHigh} ${group.unit}`
                : group.refHigh !== undefined
                  ? `< ${group.refHigh} ${group.unit}`
                  : `> ${group.refLow} ${group.unit}`}
            </p>
          )}

          <div className="flex flex-col gap-2">
            {group.readings.map((reading, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-sm"
              >
                <span className="text-muted-foreground">
                  {reading.date ? formatDate(reading.date) : ""}
                </span>
                <span
                  className={`font-medium ${
                    reading.isOutOfRange ? "text-destructive" : "text-accent"
                  }`}
                >
                  {reading.value} {group.unit}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function RangeBar({
  value,
  refLow,
  refHigh,
  severity,
}: {
  value: number;
  refLow: number | undefined;
  refHigh: number | undefined;
  severity: "normal" | "borderline" | "high";
}) {
  if (refHigh === undefined && refLow === undefined) return null;

  const low = refLow ?? 0;
  const high = refHigh ?? value * 1.5;
  const rangeSpan = high - low;
  const barMin = low - rangeSpan * 0.3;
  const barMax = high + rangeSpan * 0.3;
  const totalSpan = barMax - barMin;

  const normalStart = ((low - barMin) / totalSpan) * 100;
  const normalWidth = ((high - low) / totalSpan) * 100;
  const markerPos = Math.max(
    0,
    Math.min(100, ((value - barMin) / totalSpan) * 100),
  );

  return (
    <div className="relative h-3 rounded-full bg-muted overflow-hidden mt-1">
      <div
        className="absolute h-full bg-accent/30 rounded-full"
        style={{
          left: `${normalStart}%`,
          width: `${normalWidth}%`,
        }}
      />
      <div
        className={`absolute top-0 w-3 h-3 rounded-full border-2 border-background ${SEVERITY_BG[severity]}`}
        style={{
          left: `${markerPos}%`,
          transform: "translateX(-50%)",
        }}
      />
    </div>
  );
}
