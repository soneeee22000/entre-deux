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
const API_TOKEN = import.meta.env.VITE_API_TOKEN as string | undefined;

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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (API_TOKEN) {
    headers["Authorization"] = `Bearer ${API_TOKEN}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { ...headers, ...(options.headers as Record<string, string>) },
    ...options,
  });

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
