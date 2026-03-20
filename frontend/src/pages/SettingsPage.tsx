import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { usePatient } from "@/lib/use-patient";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { getPatientDisplayName, type FhirConsent } from "@/lib/fhir";

export function SettingsPage() {
  const { patient, patientId, logout } = usePatient();
  const navigate = useNavigate();
  const [consents, setConsents] = useState<FhirConsent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    api
      .listConsents(patientId)
      .then((data) => {
        if (!cancelled) setConsents(data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  async function handleRevoke(consentId: string) {
    setRevokingId(consentId);
    try {
      const updated = await api.revokeConsent(consentId);
      setConsents((prev) =>
        prev.map((consent) => (consent.id === consentId ? updated : consent)),
      );
    } catch {
      // Silently fail — consent may already be revoked
    } finally {
      setRevokingId(null);
    }
  }

  function handleLogout() {
    logout();
    navigate("/bienvenue", { replace: true });
  }

  const displayName = patient ? getPatientDisplayName(patient) : "";
  const identifier = patient?.identifier?.[0]?.value ?? "";

  return (
    <div>
      <PageHeader title="Parametres" showBack />

      <div className="px-4 py-4 flex flex-col gap-6">
        <Card>
          <h3 className="font-semibold font-[var(--font-heading)] text-base mb-2">
            Informations du patient
          </h3>
          <div className="flex flex-col gap-1">
            <p className="text-base text-foreground">{displayName}</p>
            {identifier && (
              <p className="text-sm text-muted-foreground">
                Identifiant : {identifier}
              </p>
            )}
          </div>
        </Card>

        <div>
          <h3 className="font-semibold font-[var(--font-heading)] text-base mb-3 flex items-center gap-2">
            <ShieldCheck size={18} />
            Consentements
          </h3>

          {isLoading ? (
            <LoadingSpinner />
          ) : consents.length === 0 ? (
            <p className="text-muted-foreground text-base">
              Aucun consentement enregistre.
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {consents.map((consent) => {
                const scope =
                  consent.provision?.[0]?.purpose?.[0]?.display ??
                  consent.provision?.[0]?.purpose?.[0]?.code ??
                  "Consentement";
                const isActive = consent.status === "active";
                const isRevoking = revokingId === consent.id;

                return (
                  <Card key={consent.id}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-base font-medium">{scope}</p>
                        <p className="text-sm text-muted-foreground">
                          {consent.date ? formatDate(consent.date) : ""}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={isActive ? "accent" : "default"}>
                          {isActive ? "Actif" : "Revoque"}
                        </Badge>
                        {isActive && (
                          <Button
                            variant="ghost"
                            className="text-sm min-h-[36px] px-3"
                            onClick={() => handleRevoke(consent.id)}
                            disabled={isRevoking}
                          >
                            {isRevoking ? "..." : "Revoquer"}
                          </Button>
                        )}
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        <Button
          variant="ghost"
          className="text-destructive"
          onClick={handleLogout}
        >
          <LogOut size={18} className="mr-2" />
          Se deconnecter
        </Button>
      </div>
    </div>
  );
}
