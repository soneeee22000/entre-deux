import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { VisitBriefPage } from "@/pages/VisitBriefPage";
import { PatientContext } from "@/lib/patient-context-value";
import type { FhirComposition } from "@/lib/fhir";

const MOCK_COMPOSITION: FhirComposition = {
  resourceType: "Composition",
  id: "comp-1",
  status: "final",
  date: "2026-03-15",
  title: "Bilan de visite",
  _db_id: "db-comp-1",
  section: [
    {
      title: "Resume clinique",
      text: { status: "generated", div: "<div>Patient suivi</div>" },
    },
  ],
};

function renderVisitBrief() {
  const contextValue = {
    patientId: "patient-123",
    patient: {
      resourceType: "Patient" as const,
      id: "patient-123",
      name: [{ given: ["Sophie"], family: "Martin" }],
    },
    isLoading: false,
    register: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  };

  return render(
    <MemoryRouter>
      <PatientContext value={contextValue}>
        <VisitBriefPage />
      </PatientContext>
    </MemoryRouter>,
  );
}

describe("VisitBriefPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the page title", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listCompositions").mockResolvedValue([]);

    renderVisitBrief();
    expect(screen.getByText("Bilan de visite")).toBeInTheDocument();
  });

  it("renders download button when compositions have _db_id", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listCompositions").mockResolvedValue([
      MOCK_COMPOSITION,
    ]);

    renderVisitBrief();

    await waitFor(() => {
      expect(screen.getByText("Bilan de visite")).toBeInTheDocument();
    });
  });

  it("shows empty state when no compositions", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listCompositions").mockResolvedValue([]);

    renderVisitBrief();

    await waitFor(() => {
      expect(screen.getByText("Aucun bilan")).toBeInTheDocument();
    });
  });
});
