import { useState, useEffect } from "react";
import { FileText } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePatient } from "@/lib/use-patient";
import { api } from "@/lib/api";
import { formatDate, formatDateInput } from "@/lib/utils";
import type { FhirComposition } from "@/lib/fhir";

function defaultPeriodStart(): string {
  const date = new Date();
  date.setDate(date.getDate() - 30);
  return formatDateInput(date);
}

export function VisitBriefPage() {
  const { patientId } = usePatient();
  const [periodStart, setPeriodStart] = useState(defaultPeriodStart);
  const [periodEnd, setPeriodEnd] = useState(() => formatDateInput(new Date()));
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [lastBrief, setLastBrief] = useState<FhirComposition | null>(null);
  const [compositions, setCompositions] = useState<FhirComposition[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    api
      .listCompositions(patientId)
      .then((data) => {
        if (!cancelled) setCompositions(data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  async function handleGenerate(event: React.FormEvent) {
    event.preventDefault();
    if (!patientId) return;

    setError("");
    setIsGenerating(true);
    setLastBrief(null);

    try {
      const brief = await api.generateVisitBrief({
        patient_id: patientId,
        period_start: new Date(periodStart).toISOString(),
        period_end: new Date(periodEnd).toISOString(),
      });
      setLastBrief(brief);
      setCompositions((prev) => [brief, ...prev]);
    } catch {
      setError("Quelque chose s'est mal passe. Veuillez reessayer.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div>
      <PageHeader title="Bilan de visite" />

      <div className="px-4 py-4 flex flex-col gap-6">
        <form onSubmit={handleGenerate} className="flex flex-col gap-3">
          <div className="flex gap-3">
            <div className="flex-1">
              <label
                htmlFor="periodStart"
                className="block text-sm font-medium text-foreground mb-1"
              >
                Du
              </label>
              <Input
                id="periodStart"
                type="date"
                value={periodStart}
                onChange={(event) => setPeriodStart(event.target.value)}
              />
            </div>
            <div className="flex-1">
              <label
                htmlFor="periodEnd"
                className="block text-sm font-medium text-foreground mb-1"
              >
                Au
              </label>
              <Input
                id="periodEnd"
                type="date"
                value={periodEnd}
                onChange={(event) => setPeriodEnd(event.target.value)}
              />
            </div>
          </div>

          {error && (
            <p className="text-destructive text-sm" role="alert">
              {error}
            </p>
          )}

          {isGenerating ? (
            <LoadingSpinner message="Generation du bilan... Cela peut prendre quelques secondes." />
          ) : (
            <Button type="submit">Generer le bilan</Button>
          )}
        </form>

        {lastBrief && <CompositionDetail composition={lastBrief} />}

        <div>
          <h2 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
            Bilans precedents
          </h2>

          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : compositions.length === 0 ? (
            <EmptyState
              icon={<FileText size={40} />}
              title="Aucun bilan"
              description="Generez votre premier bilan de visite ci-dessus."
            />
          ) : (
            <div className="flex flex-col gap-3">
              {compositions.map((comp) => (
                <CompositionCard key={comp.id} composition={comp} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CompositionDetail({ composition }: { composition: FhirComposition }) {
  return (
    <Card className="border-primary/30">
      <h3 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
        {composition.title ?? "Bilan de visite"}
      </h3>
      {composition.section?.map((section, index) => (
        <div key={index} className="mb-4 last:mb-0">
          {section.title && (
            <h4 className="font-medium text-base text-foreground mb-1">
              {section.title}
            </h4>
          )}
          {section.text?.div && (
            <div
              className="text-base text-foreground prose-sm"
              dangerouslySetInnerHTML={{ __html: section.text.div }}
            />
          )}
        </div>
      ))}
    </Card>
  );
}

function CompositionCard({ composition }: { composition: FhirComposition }) {
  const [expanded, setExpanded] = useState(false);
  const date = composition.date ? formatDate(composition.date) : "";

  return (
    <Card className="cursor-pointer" onClick={() => setExpanded(!expanded)}>
      <div className="flex items-center justify-between">
        <p className="font-medium text-base">
          {composition.title ?? "Bilan de visite"}
        </p>
        <span className="text-sm text-muted-foreground">{date}</span>
      </div>
      {expanded && (
        <div className="mt-3 pt-3 border-t border-border">
          {composition.section?.map((section, index) => (
            <div key={index} className="mb-3 last:mb-0">
              {section.title && (
                <h4 className="font-medium text-sm text-foreground mb-1">
                  {section.title}
                </h4>
              )}
              {section.text?.div && (
                <div
                  className="text-sm text-foreground"
                  dangerouslySetInnerHTML={{ __html: section.text.div }}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
