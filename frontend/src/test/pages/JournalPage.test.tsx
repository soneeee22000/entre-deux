import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { JournalPage } from "@/pages/JournalPage";
import { PatientContext } from "@/lib/patient-context-value";
import type { FhirQuestionnaireResponse } from "@/lib/fhir";

const MOCK_ENTRY: FhirQuestionnaireResponse = {
  resourceType: "QuestionnaireResponse",
  id: "qr-1",
  status: "completed",
  authored: "2025-03-01T00:00:00Z",
  item: [
    {
      linkId: "transcript",
      answer: [{ valueString: "Je me sens fatigue aujourd'hui" }],
    },
    {
      linkId: "ai-response",
      answer: [{ valueString: "Je comprends que tu te sentes fatigue." }],
    },
    {
      linkId: "symptoms",
      answer: [{ valueString: "fatigue" }],
    },
    {
      linkId: "emotional-state",
      answer: [{ valueString: "anxieux" }],
    },
  ],
};

function renderJournal() {
  const contextValue = {
    patientId: "patient-123",
    patient: {
      resourceType: "Patient" as const,
      id: "patient-123",
      name: [{ given: ["Marie"], family: "Dupont" }],
    },
    isLoading: false,
    register: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  };

  return render(
    <MemoryRouter>
      <PatientContext value={contextValue}>
        <JournalPage />
      </PatientContext>
    </MemoryRouter>,
  );
}

describe("JournalPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders journal form", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([]);

    renderJournal();
    expect(screen.getByText("Mon journal")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/Comment vous sentez-vous/),
    ).toBeInTheDocument();
    expect(screen.getByText("Envoyer")).toBeInTheDocument();
  });

  it("submit button is disabled when textarea is empty", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([]);

    renderJournal();
    const submitButton = screen.getByText("Envoyer").closest("button");
    expect(submitButton).toBeDisabled();
  });

  it("enables submit when text is entered", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([]);

    renderJournal();
    const textarea = screen.getByPlaceholderText(/Comment vous sentez-vous/);
    fireEvent.change(textarea, {
      target: { value: "Je me sens bien" },
    });

    const submitButton = screen.getByText("Envoyer").closest("button");
    expect(submitButton).not.toBeDisabled();
  });

  it("submits form and shows AI response", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([]);
    vi.spyOn(mockApi.api, "createJournalEntry").mockResolvedValue(MOCK_ENTRY);

    renderJournal();

    const textarea = screen.getByPlaceholderText(/Comment vous sentez-vous/);
    fireEvent.change(textarea, {
      target: { value: "Je me sens fatigue" },
    });
    fireEvent.click(screen.getByText("Envoyer"));

    await waitFor(() => {
      expect(
        screen.getByText("Je comprends que tu te sentes fatigue."),
      ).toBeInTheDocument();
    });
  });

  it("loads and displays entry history", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([MOCK_ENTRY]);

    renderJournal();

    await waitFor(() => {
      expect(
        screen.getByText(/Je me sens fatigue aujourd'hui/),
      ).toBeInTheDocument();
    });
  });

  it("shows empty state when no entries", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listJournalEntries").mockResolvedValue([]);

    renderJournal();

    await waitFor(() => {
      expect(screen.getByText("Aucune entree")).toBeInTheDocument();
    });
  });
});
