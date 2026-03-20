import { useState, useEffect } from "react";
import { BookHeart, Send } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePatient } from "@/lib/use-patient";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import {
  getJournalTranscript,
  getJournalAiResponse,
  getJournalSymptoms,
  getJournalEmotionalState,
  type FhirQuestionnaireResponse,
} from "@/lib/fhir";

export function JournalPage() {
  const { patientId } = usePatient();
  const [transcript, setTranscript] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [lastResponse, setLastResponse] =
    useState<FhirQuestionnaireResponse | null>(null);
  const [entries, setEntries] = useState<FhirQuestionnaireResponse[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    api
      .listJournalEntries(patientId)
      .then((data) => {
        if (!cancelled) setEntries(data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!patientId || !transcript.trim()) return;

    setError("");
    setIsSubmitting(true);
    setLastResponse(null);

    try {
      const response = await api.createJournalEntry({
        patient_id: patientId,
        transcript: transcript.trim(),
      });
      setLastResponse(response);
      setEntries((prev) => [response, ...prev]);
      setTranscript("");
    } catch {
      setError("Quelque chose s'est mal passe. Veuillez reessayer.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader title="Mon journal" />

      <div className="px-4 py-4 flex flex-col gap-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Textarea
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            placeholder="Comment vous sentez-vous aujourd'hui ? Decrivez vos symptomes, votre humeur, ce que vous avez mange..."
            disabled={isSubmitting}
          />
          {error && (
            <p className="text-destructive text-sm" role="alert">
              {error}
            </p>
          )}
          {isSubmitting ? (
            <LoadingSpinner message="Analyse en cours..." />
          ) : (
            <Button type="submit" disabled={!transcript.trim()}>
              <Send size={18} className="mr-2" />
              Envoyer
            </Button>
          )}
        </form>

        {lastResponse && <AiResponseCard response={lastResponse} />}

        <div>
          <h2 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
            Historique
          </h2>
          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : entries.length === 0 ? (
            <EmptyState
              icon={<BookHeart size={40} />}
              title="Aucune entree"
              description="Ecrivez votre premiere entree de journal ci-dessus."
            />
          ) : (
            <div className="flex flex-col gap-3">
              {entries.map((entry) => (
                <JournalEntryCard key={entry.id} entry={entry} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AiResponseCard({ response }: { response: FhirQuestionnaireResponse }) {
  const aiResponse = getJournalAiResponse(response);
  const symptoms = getJournalSymptoms(response);
  const emotionalState = getJournalEmotionalState(response);

  if (!aiResponse) return null;

  return (
    <Card className="border-accent/40 bg-accent/5">
      <p className="text-base text-foreground whitespace-pre-line mb-3">
        {aiResponse}
      </p>
      {symptoms.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {symptoms.map((symptom) => (
            <Badge key={symptom} variant="accent">
              {symptom}
            </Badge>
          ))}
        </div>
      )}
      {emotionalState && (
        <p className="text-sm text-muted-foreground">
          Etat emotionnel : {emotionalState}
        </p>
      )}
    </Card>
  );
}

function JournalEntryCard({ entry }: { entry: FhirQuestionnaireResponse }) {
  const transcript = getJournalTranscript(entry);
  const emotionalState = getJournalEmotionalState(entry);
  const date = entry.authored ? formatDate(entry.authored) : "";

  return (
    <Card>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{date}</span>
        {emotionalState && <Badge>{emotionalState}</Badge>}
      </div>
      <p className="text-base text-foreground">
        {transcript.length > 120
          ? `${transcript.slice(0, 120)}...`
          : transcript}
      </p>
    </Card>
  );
}
