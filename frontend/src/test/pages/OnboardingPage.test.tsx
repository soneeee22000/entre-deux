import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { OnboardingPage } from "@/pages/OnboardingPage";

const TEST_PASS = "password123";

vi.mock("@/assets/hero.png", () => ({ default: "hero.png" }));

const mockRegister = vi.fn();
const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("@/lib/use-auth", () => ({
  useAuth: () => ({
    isAuthenticated: false,
    isLoading: false,
    patientId: null,
    login: vi.fn(),
    register: mockRegister,
    logout: vi.fn(),
  }),
}));

function renderOnboarding() {
  return render(
    <MemoryRouter>
      <OnboardingPage />
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
    expect(screen.getByText("Creer votre compte")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Prenom")).toBeInTheDocument();
  });

  it("renders registration form fields including email and password", () => {
    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument();
    expect(screen.getByLabelText("Prenom")).toBeInTheDocument();
    expect(screen.getByLabelText("Nom")).toBeInTheDocument();
    expect(screen.getByLabelText("Identifiant patient")).toBeInTheDocument();
    expect(screen.getByText("Creer mon compte")).toBeInTheDocument();
  });

  it("submits form and navigates on success", async () => {
    mockRegister.mockResolvedValue(undefined);

    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "marie@exemple.fr" },
    });
    fireEvent.change(screen.getByLabelText("Mot de passe"), {
      target: { value: TEST_PASS },
    });
    fireEvent.change(screen.getByLabelText("Prenom"), {
      target: { value: "Marie" },
    });
    fireEvent.change(screen.getByLabelText("Nom"), {
      target: { value: "Dupont" },
    });
    fireEvent.change(screen.getByLabelText("Identifiant patient"), {
      target: { value: "TEST-001" },
    });
    fireEvent.click(screen.getByText("Creer mon compte"));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        email: "marie@exemple.fr",
        password: TEST_PASS,
        given_name: "Marie",
        family_name: "Dupont",
        identifier: "TEST-001",
      });
    });
  });

  it("shows error on 409 conflict", async () => {
    const { ApiRequestError } = await import("@/lib/api");
    mockRegister.mockRejectedValue(
      new ApiRequestError(409, "CONFLICT", "Already exists"),
    );

    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "marie@exemple.fr" },
    });
    fireEvent.change(screen.getByLabelText("Mot de passe"), {
      target: { value: TEST_PASS },
    });
    fireEvent.change(screen.getByLabelText("Prenom"), {
      target: { value: "Marie" },
    });
    fireEvent.change(screen.getByLabelText("Nom"), {
      target: { value: "Dupont" },
    });
    fireEvent.change(screen.getByLabelText("Identifiant patient"), {
      target: { value: "TEST-001" },
    });
    fireEvent.click(screen.getByText("Creer mon compte"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Cet email ou identifiant est deja utilise.",
      );
    });
  });

  it("shows back button on register step", () => {
    renderOnboarding();
    fireEvent.click(screen.getByText("Commencer"));
    expect(screen.getByText("Retour")).toBeInTheDocument();
  });

  it("has link to login page", () => {
    renderOnboarding();
    expect(screen.getByText("Se connecter")).toBeInTheDocument();
  });
});
