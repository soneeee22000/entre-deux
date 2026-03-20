import { describe, it, expect, vi, beforeEach } from "vitest";
import { ApiRequestError, api } from "@/lib/api";

describe("ApiRequestError", () => {
  it("constructs with status, code, and message", () => {
    const error = new ApiRequestError(409, "CONFLICT", "Already exists");
    expect(error.status).toBe(409);
    expect(error.code).toBe("CONFLICT");
    expect(error.message).toBe("Already exists");
    expect(error.name).toBe("ApiRequestError");
    expect(error).toBeInstanceOf(Error);
  });
});

describe("api", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("createPatient sends POST with correct body", async () => {
    const mockPatient = {
      resourceType: "Patient",
      id: "123",
      name: [{ given: ["Jean"], family: "Dupont" }],
    };
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockPatient),
    } as Response);

    const result = await api.createPatient({
      given_name: "Jean",
      family_name: "Dupont",
      identifier: "TEST-001",
    });

    expect(result.id).toBe("123");
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/patients",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          given_name: "Jean",
          family_name: "Dupont",
          identifier: "TEST-001",
        }),
      }),
    );
  });

  it("throws ApiRequestError on non-ok response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: () => Promise.resolve({ detail: "Already exists" }),
    } as Response);

    await expect(
      api.createPatient({
        given_name: "Jean",
        family_name: "Dupont",
        identifier: "TEST-001",
      }),
    ).rejects.toThrow(ApiRequestError);
  });

  it("handles non-JSON error responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: () => Promise.reject(new Error("not JSON")),
    } as Response);

    await expect(api.getPatient("123")).rejects.toThrow(ApiRequestError);
  });

  it("getPatient sends GET request", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ resourceType: "Patient", id: "123" }),
    } as Response);

    const result = await api.getPatient("123");
    expect(result.id).toBe("123");
  });

  it("listObservations sends correct URL", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    } as Response);

    await api.listObservations("patient-123");
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/observations/patients/patient-123",
      expect.any(Object),
    );
  });
});
