interface FhirCoding {
  system?: string;
  code?: string;
  display?: string;
}

interface FhirCodeableConcept {
  coding?: FhirCoding[];
  text?: string;
}

interface FhirReference {
  reference?: string;
  display?: string;
}

interface FhirQuantity {
  value?: number;
  unit?: string;
}

interface FhirHumanName {
  given?: string[];
  family?: string;
}

interface FhirIdentifier {
  system?: string;
  value?: string;
}

export interface FhirPatient {
  resourceType: "Patient";
  id: string;
  name?: FhirHumanName[];
  identifier?: FhirIdentifier[];
}

export interface FhirObservation {
  resourceType: "Observation";
  id: string;
  status: string;
  code: FhirCodeableConcept;
  subject?: FhirReference;
  effectiveDateTime?: string;
  valueQuantity?: FhirQuantity;
  referenceRange?: Array<{
    low?: FhirQuantity;
    high?: FhirQuantity;
  }>;
}

interface FhirQuestionnaireResponseItem {
  linkId: string;
  text?: string;
  answer?: Array<{
    valueString?: string;
    valueCoding?: FhirCoding;
  }>;
}

export interface FhirQuestionnaireResponse {
  resourceType: "QuestionnaireResponse";
  id: string;
  status: string;
  subject?: FhirReference;
  authored?: string;
  item?: FhirQuestionnaireResponseItem[];
}

interface FhirCompositionSection {
  title?: string;
  text?: {
    status?: string;
    div?: string;
  };
}

export interface FhirComposition {
  resourceType: "Composition";
  id: string;
  status: string;
  type?: FhirCodeableConcept;
  subject?: FhirReference[];
  date?: string;
  title?: string;
  section?: FhirCompositionSection[];
}

export interface FhirConsent {
  resourceType: "Consent";
  id: string;
  status: string;
  subject?: FhirReference;
  date?: string;
  provision?: Array<{
    purpose?: FhirCoding[];
  }>;
}

export interface CreatePatientRequest {
  given_name: string;
  family_name: string;
  identifier: string;
}

export interface AnalyzeLabImageRequest {
  patient_id: string;
  image_base64: string;
}

export interface CreateObservationRequest {
  patient_id: string;
  loinc_code: string;
  loinc_display: string;
  value: number;
  unit: string;
  reference_range_low?: number;
  reference_range_high?: number;
}

export interface CreateJournalEntryRequest {
  patient_id: string;
  transcript: string;
}

export interface GenerateVisitBriefRequest {
  patient_id: string;
  period_start: string;
  period_end: string;
}

export interface CreateConsentRequest {
  patient_id: string;
  scope: string;
}

export interface PatientTimeline {
  patient: FhirPatient;
  observations: FhirObservation[];
  questionnaire_responses: FhirQuestionnaireResponse[];
  compositions: FhirComposition[];
}

export interface LabAnalysisResult {
  diagnostic_report: Record<string, unknown>;
  observations: FhirObservation[];
  explanation: string;
}

export function getPatientDisplayName(patient: FhirPatient): string {
  const name = patient.name?.[0];
  if (!name) return "Patient";
  const given = name.given?.[0] ?? "";
  const family = name.family ?? "";
  return `${given} ${family}`.trim() || "Patient";
}

export function getPatientFirstName(patient: FhirPatient): string {
  return patient.name?.[0]?.given?.[0] ?? "Patient";
}

export function getObservationDisplay(observation: FhirObservation): {
  name: string;
  value: string;
  unit: string;
  isOutOfRange: boolean;
} {
  const coding = observation.code?.coding?.[0];
  const name = coding?.display ?? coding?.code ?? "Observation";
  const rawValue = observation.valueQuantity?.value;
  const value = rawValue !== undefined ? String(rawValue) : "--";
  const unit = observation.valueQuantity?.unit ?? "";

  let isOutOfRange = false;
  if (rawValue !== undefined && observation.referenceRange?.[0]) {
    const range = observation.referenceRange[0];
    if (range.low?.value !== undefined && rawValue < range.low.value) {
      isOutOfRange = true;
    }
    if (range.high?.value !== undefined && rawValue > range.high.value) {
      isOutOfRange = true;
    }
  }

  return { name, value, unit, isOutOfRange };
}

function findItemByLinkId(
  items: FhirQuestionnaireResponseItem[] | undefined,
  linkId: string,
): string | undefined {
  return items?.find((item) => item.linkId === linkId)?.answer?.[0]
    ?.valueString;
}

export function getJournalTranscript(
  response: FhirQuestionnaireResponse,
): string {
  return findItemByLinkId(response.item, "transcript") ?? "";
}

export function getJournalAiResponse(
  response: FhirQuestionnaireResponse,
): string {
  return findItemByLinkId(response.item, "ai-response") ?? "";
}

export function getJournalSymptoms(
  response: FhirQuestionnaireResponse,
): string[] {
  const raw = findItemByLinkId(response.item, "symptoms");
  if (!raw) return [];
  return raw
    .split(",")
    .map((symptom) => symptom.trim())
    .filter(Boolean);
}

export function getJournalEmotionalState(
  response: FhirQuestionnaireResponse,
): string {
  return findItemByLinkId(response.item, "emotional-state") ?? "";
}
