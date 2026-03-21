import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MicrophoneButton } from "@/components/ui/MicrophoneButton";

describe("MicrophoneButton", () => {
  it("renders mic icon when idle", () => {
    render(
      <MicrophoneButton
        isRecording={false}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const button = screen.getByLabelText("Enregistrer un message vocal");
    expect(button).toBeInTheDocument();
  });

  it("renders stop icon when recording", () => {
    render(
      <MicrophoneButton
        isRecording={true}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const button = screen.getByLabelText("Arreter l'enregistrement");
    expect(button).toBeInTheDocument();
  });

  it("calls onStart when clicked while idle", () => {
    const onStart = vi.fn();
    render(
      <MicrophoneButton
        isRecording={false}
        onStart={onStart}
        onStop={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(onStart).toHaveBeenCalledOnce();
  });

  it("calls onStop when clicked while recording", () => {
    const onStop = vi.fn();
    render(
      <MicrophoneButton isRecording={true} onStart={vi.fn()} onStop={onStop} />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it("is disabled when disabled prop is true", () => {
    render(
      <MicrophoneButton
        isRecording={false}
        onStart={vi.fn()}
        onStop={vi.fn()}
        disabled={true}
      />,
    );
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("has 44px minimum touch target", () => {
    render(
      <MicrophoneButton
        isRecording={false}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const button = screen.getByRole("button");
    expect(button.className).toContain("min-w-[44px]");
    expect(button.className).toContain("min-h-[44px]");
  });
});
