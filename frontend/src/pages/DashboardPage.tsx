import { useNavigate } from "react-router-dom";
import { FlaskConical, BookHeart, FileText, Settings } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { usePatient } from "@/lib/use-patient";
import { useAsyncData } from "@/lib/use-async-data";
import { api } from "@/lib/api";
import { formatDateShort } from "@/lib/utils";
import {
  getPatientFirstName,
  getObservationDisplay,
  getJournalTranscript,
  type PatientTimeline,
} from "@/lib/fhir";

interface TimelineItem {
  type: "observation" | "journal" | "composition";
  date: string;
  label: string;
}

function buildTimelineItems(timeline: PatientTimeline): TimelineItem[] {
  const items: TimelineItem[] = [];

  for (const obs of timeline.observations) {
    const display = getObservationDisplay(obs);
    items.push({
      type: "observation",
      date: obs.effectiveDateTime ?? "",
      label: `${display.name}: ${display.value} ${display.unit}`,
    });
  }

  for (const qr of timeline.questionnaire_responses) {
    const transcript = getJournalTranscript(qr);
    items.push({
      type: "journal",
      date: qr.authored ?? "",
      label:
        transcript.length > 60 ? `${transcript.slice(0, 60)}...` : transcript,
    });
  }

  for (const comp of timeline.compositions) {
    items.push({
      type: "composition",
      date: comp.date ?? "",
      label: comp.title ?? "Bilan de visite",
    });
  }

  items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  return items.slice(0, 5);
}

const ICON_MAP = {
  observation: FlaskConical,
  journal: BookHeart,
  composition: FileText,
} as const;

function handleCardKeyDown(
  event: React.KeyboardEvent,
  action: () => void,
): void {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    action();
  }
}

export function DashboardPage() {
  const { patientId, patient } = usePatient();
  const navigate = useNavigate();

  const {
    data: timelineData,
    error,
    isLoading,
    retry,
  } = useAsyncData(() => api.getPatientTimeline(patientId!), [patientId]);

  const timeline = timelineData ? buildTimelineItems(timelineData) : [];
  const firstName = patient ? getPatientFirstName(patient) : "";
  const today = new Date().toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <div className="px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-[var(--font-heading)]">
            Bonjour, {firstName}
          </h1>
          <p className="text-muted-foreground text-base capitalize">{today}</p>
        </div>
        <button
          onClick={() => navigate("/parametres")}
          className="flex items-center justify-center h-10 w-10 rounded-lg hover:bg-muted transition-colors"
          aria-label="Parametres"
        >
          <Settings size={22} className="text-muted-foreground" />
        </button>
      </div>

      <div className="flex flex-col gap-3 mb-8">
        <Card
          className="cursor-pointer active:opacity-80 transition-opacity"
          onClick={() => navigate("/analyses")}
          role="button"
          tabIndex={0}
          onKeyDown={(event) =>
            handleCardKeyDown(event, () => navigate("/analyses"))
          }
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-secondary/20">
              <FlaskConical size={24} className="text-primary" />
            </div>
            <div>
              <p className="font-medium text-base">Analyser mes resultats</p>
              <p className="text-sm text-muted-foreground">
                Photo ou saisie manuelle
              </p>
            </div>
          </div>
        </Card>

        <Card
          className="cursor-pointer active:opacity-80 transition-opacity"
          onClick={() => navigate("/journal")}
          role="button"
          tabIndex={0}
          onKeyDown={(event) =>
            handleCardKeyDown(event, () => navigate("/journal"))
          }
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent/20">
              <BookHeart size={24} className="text-accent" />
            </div>
            <div>
              <p className="font-medium text-base">Ecrire dans mon journal</p>
              <p className="text-sm text-muted-foreground">
                Comment vous sentez-vous aujourd'hui ?
              </p>
            </div>
          </div>
        </Card>

        <Card
          className="cursor-pointer active:opacity-80 transition-opacity"
          onClick={() => navigate("/bilan")}
          role="button"
          tabIndex={0}
          onKeyDown={(event) =>
            handleCardKeyDown(event, () => navigate("/bilan"))
          }
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-primary/10">
              <FileText size={24} className="text-primary" />
            </div>
            <div>
              <p className="font-medium text-base">Preparer mon rendez-vous</p>
              <p className="text-sm text-muted-foreground">
                Generer un bilan pour votre medecin
              </p>
            </div>
          </div>
        </Card>
      </div>

      <h2 className="text-lg font-semibold font-[var(--font-heading)] mb-3">
        Activite recente
      </h2>

      {error && <ErrorBanner message={error} onRetry={retry} />}

      {isLoading ? (
        <LoadingSpinner />
      ) : !error && timeline.length === 0 ? (
        <p className="text-muted-foreground text-base py-4">
          Aucune activite pour le moment. Commencez par ecrire dans votre
          journal ou analyser un resultat.
        </p>
      ) : !error ? (
        <div className="flex flex-col gap-2">
          {timeline.map((item, index) => {
            const Icon = ICON_MAP[item.type];
            return (
              <div
                key={`${item.type}-${index}`}
                className="flex items-center gap-3 py-2"
              >
                <Icon size={18} className="text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground truncate">
                    {item.label}
                  </p>
                </div>
                <span className="text-xs text-muted-foreground shrink-0">
                  {item.date ? formatDateShort(item.date) : ""}
                </span>
              </div>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
