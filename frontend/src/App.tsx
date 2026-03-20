import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PatientProvider } from "@/lib/patient-context";
import { AppShell } from "@/components/layout/AppShell";
import { OnboardingPage } from "@/pages/OnboardingPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { JournalPage } from "@/pages/JournalPage";
import { LabResultsPage } from "@/pages/LabResultsPage";
import { VisitBriefPage } from "@/pages/VisitBriefPage";
import { SettingsPage } from "@/pages/SettingsPage";

export default function App() {
  return (
    <BrowserRouter>
      <PatientProvider>
        <Routes>
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
    </BrowserRouter>
  );
}
