import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import App from "../App";

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("redirects to login when no auth token is stored", () => {
    render(<App />);
    expect(screen.getByText("Connexion")).toBeInTheDocument();
  });
});
