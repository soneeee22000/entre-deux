import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { usePatient } from "@/lib/use-patient";
import { api, ApiRequestError } from "@/lib/api";
import heroImage from "@/assets/hero.png";

type Step = "welcome" | "register";

export function OnboardingPage() {
  const [step, setStep] = useState<Step>("welcome");
  const [givenName, setGivenName] = useState("");
  const [familyName, setFamilyName] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { register } = usePatient();

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const patient = await api.createPatient({
        given_name: givenName.trim(),
        family_name: familyName.trim(),
        identifier: identifier.trim(),
      });

      await api.createConsent({
        patient_id: patient.id,
        scope: "ai-processing",
      });

      register(patient);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiRequestError && err.status === 409) {
        setError("Cet identifiant est deja utilise.");
      } else {
        setError("Quelque chose s'est mal passe. Veuillez reessayer.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (step === "welcome") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center px-6">
        <div className="w-full max-w-sm text-center">
          <img
            src={heroImage}
            alt="Entre Deux"
            className="mx-auto mb-8 h-40 w-40 rounded-2xl object-cover"
          />
          <h1 className="text-3xl font-bold font-[var(--font-heading)] text-foreground mb-3">
            Entre Deux
          </h1>
          <p className="text-lg text-muted-foreground mb-2">
            Votre compagnon IA entre les rendez-vous
          </p>
          <p className="text-base text-muted-foreground mb-10">
            Suivi intelligent et bienveillant de votre sante au quotidien
          </p>
          <Button className="w-full" onClick={() => setStep("register")}>
            <Heart size={18} className="mr-2" />
            Commencer
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold font-[var(--font-heading)] text-foreground mb-2">
          Creer votre profil
        </h1>
        <p className="text-base text-muted-foreground mb-8">
          Ces informations restent sur votre appareil et ne sont partagees
          qu'avec votre medecin.
        </p>

        <form onSubmit={handleRegister} className="flex flex-col gap-4">
          <div>
            <label
              htmlFor="givenName"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Prenom
            </label>
            <Input
              id="givenName"
              value={givenName}
              onChange={(event) => setGivenName(event.target.value)}
              placeholder="Marie"
              required
              autoFocus
            />
          </div>

          <div>
            <label
              htmlFor="familyName"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Nom
            </label>
            <Input
              id="familyName"
              value={familyName}
              onChange={(event) => setFamilyName(event.target.value)}
              placeholder="Dupont"
              required
            />
          </div>

          <div>
            <label
              htmlFor="identifier"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Identifiant patient
            </label>
            <Input
              id="identifier"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              placeholder="Numero de securite sociale ou identifiant"
              required
            />
          </div>

          {error && (
            <p className="text-destructive text-sm" role="alert">
              {error}
            </p>
          )}

          {isSubmitting ? (
            <LoadingSpinner message="Creation du profil..." />
          ) : (
            <Button type="submit" className="w-full mt-2">
              Creer mon profil
            </Button>
          )}
        </form>

        <button
          onClick={() => setStep("welcome")}
          className="mt-6 w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Retour
        </button>
      </div>
    </div>
  );
}
