import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SettingsPage } from "@/pages/SettingsPage";
import { PatientContext } from "@/lib/patient-context-value";
import type { FhirConsent } from "@/lib/fhir";

const MOCK_CONSENT: FhirConsent = {
  resourceType: "Consent",
  id: "consent-1",
  status: "active",
  date: "2025-03-01",
  provision: [
    {
      purpose: [
        {
          system: "https://entre-deux.health",
          code: "ai-processing",
          display: "Consent for ai-processing",
        },
      ],
    },
  ],
};

const mockLogout = vi.fn();
const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderSettings() {
  const contextValue = {
    patientId: "patient-123",
    patient: {
      resourceType: "Patient" as const,
      id: "patient-123",
      name: [{ given: ["Marie"], family: "Dupont" }],
      identifier: [{ system: "https://entre-deux.health", value: "TEST-001" }],
    },
    isLoading: false,
    register: vi.fn(),
    refresh: vi.fn(),
    logout: mockLogout,
  };

  return render(
    <MemoryRouter>
      <PatientContext value={contextValue}>
        <SettingsPage />
      </PatientContext>
    </MemoryRouter>,
  );
}

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockLogout.mockClear();
    mockNavigate.mockClear();
  });

  it("shows patient information", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents").mockResolvedValue([]);

    renderSettings();
    expect(screen.getByText("Marie Dupont")).toBeInTheDocument();
    expect(screen.getByText(/TEST-001/)).toBeInTheDocument();
  });

  it("loads and displays consents", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents").mockResolvedValue([MOCK_CONSENT]);

    renderSettings();

    await waitFor(() => {
      expect(screen.getByText("Consent for ai-processing")).toBeInTheDocument();
      expect(screen.getByText("Actif")).toBeInTheDocument();
    });
  });

  it("shows revoke button for active consents", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents").mockResolvedValue([MOCK_CONSENT]);

    renderSettings();

    await waitFor(() => {
      expect(screen.getByText("Revoquer")).toBeInTheDocument();
    });
  });

  it("revokes consent on button click", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents")
      .mockResolvedValueOnce([MOCK_CONSENT])
      .mockResolvedValueOnce([{ ...MOCK_CONSENT, status: "inactive" }]);
    vi.spyOn(mockApi.api, "revokeConsent").mockResolvedValue({
      ...MOCK_CONSENT,
      status: "inactive",
    });

    renderSettings();

    await waitFor(() => {
      expect(screen.getByText("Revoquer")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Revoquer"));

    await waitFor(() => {
      expect(screen.getByText("Revoque")).toBeInTheDocument();
    });
  });

  it("logout calls confirm and navigates on accept", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents").mockResolvedValue([]);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    renderSettings();
    fireEvent.click(screen.getByText("Se deconnecter"));
    expect(mockLogout).toHaveBeenCalled();
  });

  it("shows page header", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "listConsents").mockResolvedValue([]);

    renderSettings();
    expect(screen.getByText("Parametres")).toBeInTheDocument();
  });
});
