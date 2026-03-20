import { Outlet, Navigate } from "react-router-dom";
import { usePatient } from "@/lib/use-patient";
import { BottomNav } from "@/components/ui/BottomNav";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export function AppShell() {
  const { patientId, isLoading } = usePatient();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner message="Chargement..." />
      </div>
    );
  }

  if (!patientId) {
    return <Navigate to="/bienvenue" replace />;
  }

  return (
    <div className="flex min-h-screen flex-col pb-14">
      <main className="flex-1">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
