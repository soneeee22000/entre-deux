import { describe, it, expect } from "vitest";
import {
  getPatientDisplayName,
  getPatientFirstName,
  getObservationDisplay,
  getJournalTranscript,
  getJournalAiResponse,
  getJournalSymptoms,
  getJournalEmotionalState,
  type FhirPatient,
  type FhirObservation,
  type FhirQuestionnaireResponse,
} from "@/lib/fhir";

const PATIENT: FhirPatient = {
  resourceType: "Patient",
  id: "test-id",
  name: [{ given: ["Marie"], family: "Dupont" }],
  identifier: [{ system: "https://entre-deux.health", value: "TEST-001" }],
};

const OBSERVATION: FhirObservation = {
  resourceType: "Observation",
  id: "obs-1",
  status: "final",
  code: {
    coding: [{ system: "http://loinc.org", code: "59261-8", display: "HbA1c" }],
  },
  valueQuantity: { value: 6.5, unit: "%" },
  referenceRange: [
    { low: { value: 4.0, unit: "%" }, high: { value: 5.6, unit: "%" } },
  ],
};

const QR: FhirQuestionnaireResponse = {
  resourceType: "QuestionnaireResponse",
  id: "qr-1",
  status: "completed",
  item: [
    {
      linkId: "transcript",
      answer: [{ valueString: "Je me sens fatigue" }],
    },
    {
      linkId: "ai-response",
      answer: [{ valueString: "Je comprends ta fatigue." }],
    },
    {
      linkId: "symptoms",
      answer: [{ valueString: "fatigue, maux de tete" }],
    },
    {
      linkId: "emotional-state",
      answer: [{ valueString: "anxieux" }],
    },
  ],
};

describe("getPatientDisplayName", () => {
  it("returns full name", () => {
    expect(getPatientDisplayName(PATIENT)).toBe("Marie Dupont");
  });

  it("returns 'Patient' when no name", () => {
    const noName: FhirPatient = { resourceType: "Patient", id: "x" };
    expect(getPatientDisplayName(noName)).toBe("Patient");
  });
});

describe("getPatientFirstName", () => {
  it("returns first given name", () => {
    expect(getPatientFirstName(PATIENT)).toBe("Marie");
  });

  it("returns 'Patient' when no name", () => {
    const noName: FhirPatient = { resourceType: "Patient", id: "x" };
    expect(getPatientFirstName(noName)).toBe("Patient");
  });
});

describe("getObservationDisplay", () => {
  it("returns name, value, unit from observation", () => {
    const display = getObservationDisplay(OBSERVATION);
    expect(display.name).toBe("HbA1c");
    expect(display.value).toBe("6.5");
    expect(display.unit).toBe("%");
  });

  it("detects out-of-range high values", () => {
    const display = getObservationDisplay(OBSERVATION);
    expect(display.isOutOfRange).toBe(true);
  });

  it("detects in-range values", () => {
    const inRange: FhirObservation = {
      ...OBSERVATION,
      valueQuantity: { value: 5.0, unit: "%" },
    };
    const display = getObservationDisplay(inRange);
    expect(display.isOutOfRange).toBe(false);
  });

  it("returns '--' for missing value", () => {
    const noValue: FhirObservation = {
      ...OBSERVATION,
      valueQuantity: { unit: "%" },
    };
    const display = getObservationDisplay(noValue);
    expect(display.value).toBe("--");
  });
});

describe("getJournalTranscript", () => {
  it("extracts transcript from QR items", () => {
    expect(getJournalTranscript(QR)).toBe("Je me sens fatigue");
  });

  it("returns empty string when no items", () => {
    const empty: FhirQuestionnaireResponse = {
      resourceType: "QuestionnaireResponse",
      id: "x",
      status: "completed",
    };
    expect(getJournalTranscript(empty)).toBe("");
  });
});

describe("getJournalAiResponse", () => {
  it("extracts AI response", () => {
    expect(getJournalAiResponse(QR)).toBe("Je comprends ta fatigue.");
  });
});

describe("getJournalSymptoms", () => {
  it("parses comma-separated symptoms", () => {
    expect(getJournalSymptoms(QR)).toEqual(["fatigue", "maux de tete"]);
  });

  it("returns empty array when no symptoms", () => {
    const empty: FhirQuestionnaireResponse = {
      resourceType: "QuestionnaireResponse",
      id: "x",
      status: "completed",
    };
    expect(getJournalSymptoms(empty)).toEqual([]);
  });
});

describe("getJournalEmotionalState", () => {
  it("extracts emotional state", () => {
    expect(getJournalEmotionalState(QR)).toBe("anxieux");
  });
});
