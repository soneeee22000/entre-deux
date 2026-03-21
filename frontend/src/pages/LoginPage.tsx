import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { LogIn } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { useAuth } from "@/lib/use-auth";
import { ApiRequestError } from "@/lib/api";
import heroImage from "@/assets/hero.png";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login(email.trim(), password);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiRequestError && err.status === 401) {
        setError("Email ou mot de passe incorrect.");
      } else {
        setError("Quelque chose s'est mal passe. Veuillez reessayer.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <img
            src={heroImage}
            alt="Entre Deux"
            className="mx-auto mb-4 h-24 w-24 rounded-2xl object-cover"
          />
          <h1 className="text-2xl font-bold font-[var(--font-heading)] text-foreground mb-2">
            Connexion
          </h1>
          <p className="text-base text-muted-foreground">
            Accedez a votre espace sante
          </p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Email
            </label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="marie@exemple.fr"
              required
              autoFocus
              autoComplete="email"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Mot de passe
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Votre mot de passe"
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="text-destructive text-sm" role="alert">
              {error}
            </p>
          )}

          {isSubmitting ? (
            <LoadingSpinner message="Connexion..." />
          ) : (
            <Button type="submit" className="w-full mt-2">
              <LogIn size={18} className="mr-2" />
              Se connecter
            </Button>
          )}
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Pas encore de compte ?{" "}
          <Link
            to="/bienvenue"
            className="text-primary hover:underline font-medium"
          >
            S'inscrire
          </Link>
        </p>
      </div>
    </div>
  );
}
