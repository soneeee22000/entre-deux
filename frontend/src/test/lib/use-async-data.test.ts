import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { useAsyncData } from "@/lib/use-async-data";

describe("useAsyncData", () => {
  it("returns data on successful fetch", async () => {
    const fetcher = vi.fn().mockResolvedValue({ items: [1, 2, 3] });

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual({ items: [1, 2, 3] });
    expect(result.current.error).toBeNull();
  });

  it("returns error message on failure", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe("Network error");
  });

  it("retry re-fetches data", async () => {
    let callCount = 0;
    const fetcher = vi.fn().mockImplementation(() => {
      callCount += 1;
      if (callCount === 1) {
        return Promise.reject(new Error("fail"));
      }
      return Promise.resolve("success");
    });

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.error).toBe("fail");
    });

    result.current.retry();

    await waitFor(() => {
      expect(result.current.data).toBe("success");
      expect(result.current.error).toBeNull();
    });
  });
});
