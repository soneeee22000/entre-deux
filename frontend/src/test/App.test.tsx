import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import App from "../App";

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("redirects to onboarding when no patient is stored", () => {
    render(<App />);
    expect(screen.getByText("Entre Deux")).toBeInTheDocument();
    expect(screen.getByText("Commencer")).toBeInTheDocument();
  });
});
