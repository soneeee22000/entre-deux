import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { BottomNav } from "@/components/ui/BottomNav";

function renderWithRouter(initialEntry = "/") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <BottomNav />
    </MemoryRouter>,
  );
}

describe("BottomNav", () => {
  it("renders all 4 navigation tabs", () => {
    renderWithRouter();
    expect(screen.getByText("Accueil")).toBeInTheDocument();
    expect(screen.getByText("Analyses")).toBeInTheDocument();
    expect(screen.getByText("Journal")).toBeInTheDocument();
    expect(screen.getByText("Bilan")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    renderWithRouter();
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(4);
  });

  it("highlights active tab on home route", () => {
    renderWithRouter("/");
    const homeLink = screen.getByText("Accueil").closest("a");
    expect(homeLink?.className).toContain("text-primary");
  });

  it("highlights active tab on analyses route", () => {
    renderWithRouter("/analyses");
    const analysesLink = screen.getByText("Analyses").closest("a");
    expect(analysesLink?.className).toContain("text-primary");
  });
});
