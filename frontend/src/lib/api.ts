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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { ...headers, ...(options.headers as Record<string, string>) },
    ...options,
  });

  if (response.status === 401) {
    const refreshToken = localStorage.getItem("entre-deux-refresh-token");
    if (refreshToken) {
      try {
        const refreshResponse = await fetch(`${BASE_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (refreshResponse.ok) {
          const tokens = (await refreshResponse.json()) as TokenResponse;
          localStorage.setItem(AUTH_TOKEN_KEY, tokens.access_token);
          localStorage.setItem(
            "entre-deux-refresh-token",
            tokens.refresh_token,
          );
          headers["Authorization"] = `Bearer ${tokens.access_token}`;
          const retryResponse = await fetch(`${BASE_URL}${path}`, {
            headers: {
              ...headers,
              ...(options.headers as Record<string, string>),
            },
            ...options,
          });
          if (retryResponse.ok) {
            return retryResponse.json() as Promise<T>;
          }
        }
      } catch {
        /* refresh failed, fall through to error */
      }
    }
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem("entre-deux-refresh-token");
    localStorage.removeItem("entre-deux-patient-id");
    window.location.href = "/connexion";
    throw new ApiRequestError(401, "UNAUTHORIZED", "Session expiree");
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

  return response.json() as Promise<T>;
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
