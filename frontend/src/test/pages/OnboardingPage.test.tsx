import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { OnboardingPage } from "@/pages/OnboardingPage";
import { PatientContext } from "@/lib/patient-context-value";

vi.mock("@/assets/hero.png", () => ({ default: "hero.png" }));

const mockRegister = vi.fn();
const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderOnboarding() {
  const contextValue = {
    patientId: null,
    patient: null,
    isLoading: false,
    register: mockRegister,
    refresh: vi.fn(),
    logout: vi.fn(),
  };

  return render(
    <MemoryRouter>
      <PatientContext value={contextValue}>
        <OnboardingPage />
      </PatientContext>
    </MemoryRouter>,
  );
}

describe("OnboardingPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockRegister.mockClear();
    mockNavigate.mockClear();
  });

  it("shows welcome step by default", () => {
    renderOnboarding();
    expect(screen.getByText("Entre Deux")).toBeInTheDocument();
    expect(screen.getByText("Commencer")).toBeInTheDocument();
  });

  it("transitions to register step on click", () => {
    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));
    expect(screen.getByText("Creer votre profil")).toBeInTheDocument();
    expect(screen.getByLabelText("Prenom")).toBeInTheDocument();
  });

  it("renders registration form fields", () => {
    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    expect(screen.getByLabelText("Prenom")).toBeInTheDocument();
    expect(screen.getByLabelText("Nom")).toBeInTheDocument();
    expect(screen.getByLabelText("Identifiant patient")).toBeInTheDocument();
    expect(screen.getByText("Creer mon profil")).toBeInTheDocument();
  });

  it("submits form and navigates on success", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "createPatient").mockResolvedValue({
      resourceType: "Patient",
      id: "new-id",
      name: [{ given: ["Marie"], family: "Dupont" }],
    });
    vi.spyOn(mockApi.api, "createConsent").mockResolvedValue({
      resourceType: "Consent",
      id: "consent-id",
      status: "active",
    });

    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    fireEvent.change(screen.getByLabelText("Prenom"), {
      target: { value: "Marie" },
    });
    fireEvent.change(screen.getByLabelText("Nom"), {
      target: { value: "Dupont" },
    });
    fireEvent.change(screen.getByLabelText("Identifiant patient"), {
      target: { value: "TEST-001" },
    });
    fireEvent.click(screen.getByText("Creer mon profil"));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalled();
    });
  });

  it("shows error on 409 conflict", async () => {
    const mockApi = await import("@/lib/api");
    vi.spyOn(mockApi.api, "createPatient").mockRejectedValue(
      new mockApi.ApiRequestError(409, "CONFLICT", "Already exists"),
    );

    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    fireEvent.change(screen.getByLabelText("Prenom"), {
      target: { value: "Marie" },
    });
    fireEvent.change(screen.getByLabelText("Nom"), {
      target: { value: "Dupont" },
    });
    fireEvent.change(screen.getByLabelText("Identifiant patient"), {
      target: { value: "TEST-001" },
    });
    fireEvent.click(screen.getByText("Creer mon profil"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Cet identifiant est deja utilise.",
      );
    });
  });

  it("shows back button on register step", () => {
    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));
    expect(screen.getByText("Retour")).toBeInTheDocument();
  });
});
