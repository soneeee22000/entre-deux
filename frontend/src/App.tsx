import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/lib/auth-context";
import { PatientProvider } from "@/lib/patient-context";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";
import { AppShell } from "@/components/layout/AppShell";
import { OnboardingPage } from "@/pages/OnboardingPage";
import { LoginPage } from "@/pages/LoginPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { JournalPage } from "@/pages/JournalPage";
import { LabResultsPage } from "@/pages/LabResultsPage";
import { VisitBriefPage } from "@/pages/VisitBriefPage";
import { SettingsPage } from "@/pages/SettingsPage";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <PatientProvider>
            <Routes>
              <Route path="/connexion" element={<LoginPage />} />
              <Route path="/bienvenue" element={<OnboardingPage />} />
              <Route element={<AppShell />}>
                <Route index element={<DashboardPage />} />
                <Route path="analyses" element={<LabResultsPage />} />
                <Route path="journal" element={<JournalPage />} />
                <Route path="bilan" element={<VisitBriefPage />} />
                <Route path="parametres" element={<SettingsPage />} />
              </Route>
            </Routes>
          </PatientProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
