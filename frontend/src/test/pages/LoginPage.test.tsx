import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LoginPage } from "@/pages/LoginPage";

vi.mock("@/assets/hero.png", () => ({ default: "hero.png" }));

const mockLogin = vi.fn();
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
    login: mockLogin,
    register: vi.fn(),
    logout: vi.fn(),
  }),
}));

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    mockLogin.mockClear();
    mockNavigate.mockClear();
  });

  it("renders login form", () => {
    renderLogin();
    expect(screen.getByText("Connexion")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument();
    expect(screen.getByText("Se connecter")).toBeInTheDocument();
  });

  it("submits form and navigates on success", async () => {
    mockLogin.mockResolvedValue(undefined);
    renderLogin();

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "marie@exemple.fr" },
    });
    fireEvent.change(screen.getByLabelText("Mot de passe"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByText("Se connecter"));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("marie@exemple.fr", "password123");
    });
  });

  it("shows error on invalid credentials", async () => {
    const { ApiRequestError } = await import("@/lib/api");
    mockLogin.mockRejectedValue(
      new ApiRequestError(401, "UNAUTHORIZED", "Invalid"),
    );

    renderLogin();

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "wrong@email.fr" },
    });
    fireEvent.change(screen.getByLabelText("Mot de passe"), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByText("Se connecter"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Email ou mot de passe incorrect.",
      );
    });
  });

  it("has link to registration page", () => {
    renderLogin();
    expect(screen.getByText("S'inscrire")).toBeInTheDocument();
  });
});
