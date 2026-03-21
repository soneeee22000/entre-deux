import { useState } from "react";
import { BookHeart, Send } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { MicrophoneButton } from "@/components/ui/MicrophoneButton";
import { usePatient } from "@/lib/use-patient";
import { useAudioRecorder } from "@/lib/use-audio-recorder";
import { useAsyncData, getErrorMessage } from "@/lib/use-async-data";
import { api, ApiRequestError } from "@/lib/api";
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
  const [submitError, setSubmitError] = useState("");
  const [lastResponse, setLastResponse] =
    useState<FhirQuestionnaireResponse | null>(null);

  const {
    isRecording,
    startRecording,
    stopRecording,
    audioBlob,
    error: audioError,
    reset: resetAudio,
  } = useAudioRecorder();

  const {
    data: entries,
    error: loadError,
    isLoading: isLoadingHistory,
    retry,
  } = useAsyncData(() => api.listJournalEntries(patientId!), [patientId]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!patientId || !transcript.trim()) return;

    setSubmitError("");
    setIsSubmitting(true);
    setLastResponse(null);

    try {
      const response = await api.createJournalEntry({
        patient_id: patientId,
        transcript: transcript.trim(),
      });
      setLastResponse(response);
      setTranscript("");
    } catch (err: unknown) {
      if (
        err instanceof ApiRequestError &&
        (err.status === 502 || err.status === 504)
      ) {
        setSubmitError(getErrorMessage(err));
      } else {
        setSubmitError(
          "Impossible d'enregistrer votre entree. Verifiez votre connexion et reessayez.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSendAudio() {
    if (!patientId || !audioBlob) return;

    setSubmitError("");
    setIsSubmitting(true);
    setLastResponse(null);

    try {
      const response = await api.createJournalEntryAudio(patientId, audioBlob);
      setLastResponse(response);
      resetAudio();
    } catch (err: unknown) {
      if (
        err instanceof ApiRequestError &&
        (err.status === 502 || err.status === 504)
      ) {
        setSubmitError(getErrorMessage(err));
      } else {
        setSubmitError(
          "Impossible de transcrire l'audio. Verifiez votre connexion et reessayez.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const displayEntries = entries ?? [];

  return (
    <div>
      <PageHeader title="Mon journal" />

      <div className="px-4 py-4 flex flex-col gap-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Textarea
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            placeholder="Comment vous sentez-vous aujourd'hui ? Decrivez vos symptomes, votre humeur, ce que vous avez mange..."
            disabled={isSubmitting || isRecording}
          />
          {(submitError || audioError) && (
            <p className="text-destructive text-sm" role="alert">
              {submitError || audioError}
            </p>
          )}
          {audioBlob && !isSubmitting && (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10 border border-accent/30">
              <span className="text-sm text-foreground flex-1">
                Enregistrement pret a envoyer
              </span>
              <Button
                type="button"
                onClick={handleSendAudio}
                className="text-sm"
              >
                <Send size={16} className="mr-1" />
                Envoyer l&apos;audio
              </Button>
              <button
                type="button"
                onClick={resetAudio}
                className="text-sm text-muted-foreground underline"
              >
                Annuler
              </button>
            </div>
          )}
          {isSubmitting ? (
            <LoadingSpinner message="Analyse en cours..." />
          ) : (
            <div className="flex gap-2">
              <Button
                type="submit"
                disabled={!transcript.trim() || isRecording}
                className="flex-1"
              >
                <Send size={18} className="mr-2" />
                Envoyer
              </Button>
              <MicrophoneButton
                isRecording={isRecording}
                onStart={startRecording}
                onStop={stopRecording}
                disabled={isSubmitting}
              />
            </div>
          )}
        </form>

        {lastResponse && <AiResponseCard response={lastResponse} />}

        <div>
          <h2 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
            Historique
          </h2>

          {loadError && <ErrorBanner message={loadError} onRetry={retry} />}

          {isLoadingHistory ? (
            <LoadingSpinner />
          ) : !loadError && displayEntries.length === 0 ? (
            <EmptyState
              icon={<BookHeart size={40} />}
              title="Aucune entree"
              description="Ecrivez votre premiere entree de journal ci-dessus."
            />
          ) : !loadError ? (
            <div className="flex flex-col gap-3">
              {displayEntries.map((entry) => (
                <JournalEntryCard key={entry.id} entry={entry} />
              ))}
            </div>
          ) : null}
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
