import type {
  FhirPatient,
  FhirObservation,
  FhirQuestionnaireResponse,
  FhirComposition,
  FhirConsent,
  CreatePatientRequest,
  AnalyzeLabImageRequest,
  CreateObservationRequest,
  CreateJournalEntryRequest,
  GenerateVisitBriefRequest,
  CreateConsentRequest,
  PatientTimeline,
} from "./fhir";

const BASE_URL = "/api/v1";
const AUTH_TOKEN_KEY = "entre-deux-access-token";

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  patient_id: string;
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

function getToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = { ...extra };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function tryRefreshAndRetry(
  path: string,
  options: RequestInit,
): Promise<Response | null> {
  const refreshToken = localStorage.getItem("entre-deux-refresh-token");
  if (!refreshToken) return null;

  try {
    const refreshResponse = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!refreshResponse.ok) return null;

    const tokens = (await refreshResponse.json()) as TokenResponse;
    localStorage.setItem(AUTH_TOKEN_KEY, tokens.access_token);
    localStorage.setItem("entre-deux-refresh-token", tokens.refresh_token);

    const retryHeaders = {
      ...(options.headers as Record<string, string>),
      Authorization: `Bearer ${tokens.access_token}`,
    };
    const retryResponse = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: retryHeaders,
    });
    if (retryResponse.ok) return retryResponse;
  } catch {
    /* refresh failed */
  }
  return null;
}

function clearAuthAndRedirect(): never {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem("entre-deux-refresh-token");
  localStorage.removeItem("entre-deux-patient-id");
  window.location.href = "/connexion";
  throw new ApiRequestError(401, "UNAUTHORIZED", "Session expiree");
}

async function handleResponse(
  response: Response,
  path: string,
  options: RequestInit,
): Promise<Response> {
  if (response.status === 401) {
    const retried = await tryRefreshAndRetry(path, options);
    if (retried) return retried;
    clearAuthAndRedirect();
  }

  if (!response.ok) {
    let code = "UNKNOWN";
    let message = "Une erreur est survenue";
    try {
      const body = await response.json();
      code = body.code ?? body.detail ?? code;
      message = body.detail ?? body.message ?? message;
    } catch {
      message = response.statusText;
    }
    throw new ApiRequestError(response.status, code, message);
  }

  return response;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = authHeaders({ "Content-Type": "application/json" });
  const init: RequestInit = {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string>) },
  };

  const response = await fetch(`${BASE_URL}${path}`, init);
  const validated = await handleResponse(response, path, init);
  return validated.json() as Promise<T>;
}

async function requestRaw(
  path: string,
  options: RequestInit,
): Promise<Response> {
  const headers = authHeaders(
    options.headers as Record<string, string> | undefined,
  );
  const init: RequestInit = { ...options, headers };
  const response = await fetch(`${BASE_URL}${path}`, init);
  return handleResponse(response, path, init);
}

export const api = {
  auth: {
    register(data: {
      email: string;
      password: string;
      given_name: string;
      family_name: string;
      identifier: string;
    }): Promise<TokenResponse> {
      return request("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    login(email: string, password: string): Promise<TokenResponse> {
      return request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
    },

    refresh(refreshToken: string): Promise<TokenResponse> {
      return fetch(`${BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      }).then((r) => {
        if (!r.ok) throw new ApiRequestError(r.status, "REFRESH_FAILED", "");
        return r.json() as Promise<TokenResponse>;
      });
    },
  },

  createPatient(data: CreatePatientRequest): Promise<FhirPatient> {
    return request("/patients", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getPatient(patientId: string): Promise<FhirPatient> {
    return request(`/patients/${patientId}`);
  },

  getPatientTimeline(patientId: string): Promise<PatientTimeline> {
    return request(`/patients/${patientId}/timeline`);
  },

  analyzeLabImage(
    data: AnalyzeLabImageRequest,
  ): Promise<Record<string, unknown>> {
    return request("/observations/analyze-image", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  createObservation(data: CreateObservationRequest): Promise<FhirObservation> {
    return request("/observations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  listObservations(patientId: string): Promise<FhirObservation[]> {
    return request(`/observations/patients/${patientId}`);
  },

  createJournalEntry(
    data: CreateJournalEntryRequest,
  ): Promise<FhirQuestionnaireResponse> {
    return request("/questionnaire-responses", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  listJournalEntries(patientId: string): Promise<FhirQuestionnaireResponse[]> {
    return request(`/questionnaire-responses/patients/${patientId}`);
  },

  async createJournalEntryAudio(
    patientId: string,
    audioBlob: Blob,
  ): Promise<FhirQuestionnaireResponse> {
    const formData = new FormData();
    formData.append("patient_id", patientId);
    formData.append("audio", audioBlob, "recording.webm");

    const response = await requestRaw("/questionnaire-responses/audio", {
      method: "POST",
      body: formData,
    });
    return response.json() as Promise<FhirQuestionnaireResponse>;
  },

  generateVisitBrief(
    data: GenerateVisitBriefRequest,
  ): Promise<FhirComposition> {
    return request("/compositions/visit-brief", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  listCompositions(patientId: string): Promise<FhirComposition[]> {
    return request(`/compositions/patients/${patientId}`);
  },

  async downloadCompositionPdf(compositionId: string): Promise<Blob> {
    const response = await requestRaw(`/compositions/${compositionId}/pdf`, {
      method: "GET",
    });
    return response.blob();
  },

  createConsent(data: CreateConsentRequest): Promise<FhirConsent> {
    return request("/consents", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  revokeConsent(consentId: string): Promise<FhirConsent> {
    return request(`/consents/${consentId}/revoke`, { method: "PUT" });
  },

  listConsents(patientId: string): Promise<FhirConsent[]> {
    return request(`/consents/patients/${patientId}`);
  },
};
