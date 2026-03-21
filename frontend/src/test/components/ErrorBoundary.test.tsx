import React, { useState } from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";

function ThrowingComponent(): React.ReactNode {
  throw new Error("Test explosion");
}

function SafeComponent() {
  return <div>Safe content</div>;
}

function RecoverableWrapper() {
  const [shouldThrow, setShouldThrow] = useState(true);
  return (
    <ErrorBoundary onReset={() => setShouldThrow(false)}>
      {shouldThrow ? <ThrowingComponent /> : <SafeComponent />}
    </ErrorBoundary>
  );
}

describe("ErrorBoundary", () => {
  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Safe content")).toBeInTheDocument();
  });

  it("renders fallback UI when a child throws", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );
    expect(
      screen.getByText("Quelque chose s'est mal passe"),
    ).toBeInTheDocument();
    expect(screen.getByText("Reessayer")).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it("calls onReset and recovers when retry is clicked", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});

    render(<RecoverableWrapper />);

    expect(
      screen.getByText("Quelque chose s'est mal passe"),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByText("Reessayer"));

    expect(screen.getByText("Safe content")).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it("renders custom fallback when provided", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(
      <ErrorBoundary fallback={<div>Custom fallback</div>}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Custom fallback")).toBeInTheDocument();
    vi.restoreAllMocks();
  });
});
