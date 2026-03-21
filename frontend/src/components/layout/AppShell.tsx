import { Outlet, Navigate } from "react-router-dom";
import { usePatient } from "@/lib/use-patient";
import { useAuth } from "@/lib/use-auth";
import { BottomNav } from "@/components/ui/BottomNav";
import { OfflineBanner } from "@/components/ui/OfflineBanner";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";

export function AppShell() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { patientId, isLoading } = usePatient();

  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner message="Chargement..." />
      </div>
    );
  }

  if (!isAuthenticated || !patientId) {
    return <Navigate to="/connexion" replace />;
  }

  return (
    <div className="flex min-h-screen flex-col pb-14">
      <OfflineBanner />
      <main className="flex-1">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
      <BottomNav />
    </div>
  );
}
