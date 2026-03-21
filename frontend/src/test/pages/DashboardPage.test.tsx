import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardPage } from "@/pages/DashboardPage";
import { PatientContext } from "@/lib/patient-context-value";
import type { FhirPatient, PatientTimeline } from "@/lib/fhir";

const MOCK_PATIENT: FhirPatient = {
  resourceType: "Patient",
  id: "patient-123",
  name: [{ given: ["Marie"], family: "Dupont" }],
};

const MOCK_TIMELINE: PatientTimeline = {
  patient: MOCK_PATIENT,
  observations: [
    {
      resourceType: "Observation",
      id: "obs-1",
      status: "final",
      code: { coding: [{ display: "HbA1c" }] },
      valueQuantity: { value: 6.5, unit: "%" },
      effectiveDateTime: "2025-03-01T00:00:00Z",
    },
  ],
  questionnaire_responses: [],
  compositions: [],
};

function renderDashboard(patient: FhirPatient | null = MOCK_PATIENT) {
  const contextValue = {
    patientId: patient?.id ?? null,
    patient,
    isLoading: false,
    register: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  };

  return render(
    <MemoryRouter>
      <PatientContext value={contextValue}>
        <DashboardPage />
      </PatientContext>
    </MemoryRouter>,
  );
}

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("shows patient greeting with first name", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockResolvedValue(
      MOCK_TIMELINE,
    );

    renderDashboard();
    expect(screen.getByText(/Bonjour, Marie/)).toBeInTheDocument();
  });

  it("renders 3 quick action cards", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockResolvedValue(
      MOCK_TIMELINE,
    );

    renderDashboard();
    expect(screen.getByText("Analyser mes resultats")).toBeInTheDocument();
    expect(screen.getByText("Ecrire dans mon journal")).toBeInTheDocument();
    expect(screen.getByText("Preparer mon rendez-vous")).toBeInTheDocument();
  });

  it("loads and displays timeline items", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockResolvedValue(
      MOCK_TIMELINE,
    );

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/HbA1c/)).toBeInTheDocument();
    });
  });

  it("shows empty state when no timeline", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockResolvedValue({
      ...MOCK_TIMELINE,
      observations: [],
    });

    renderDashboard();

    await waitFor(() => {
      expect(
        screen.getByText(/Aucune activite pour le moment/),
      ).toBeInTheDocument();
    });
  });

  it("shows settings button", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockResolvedValue(
      MOCK_TIMELINE,
    );

    renderDashboard();
    expect(screen.getByLabelText("Parametres")).toBeInTheDocument();
  });

  it("shows error banner on API failure", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "getPatientTimeline").mockRejectedValue(
      new Error("Network error"),
    );

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });
});
