import type { Page } from "@playwright/test";

const PATIENT_ID = "00000000-0000-0000-0000-000000000001";

const MOCK_PATIENT = {
  resourceType: "Patient",
  id: PATIENT_ID,
  identifier: [{ system: "https://entredeux.health/fhir", value: "TEST-001" }],
  name: [{ given: ["Marie"], family: "Laurent" }],
};

const MOCK_OBSERVATION = {
  resourceType: "Observation",
  id: "obs-1",
  status: "final",
  code: {
    coding: [{ system: "http://loinc.org", code: "59261-8", display: "HbA1c" }],
  },
  subject: { reference: `Patient/${PATIENT_ID}` },
  valueQuantity: { value: 6.5, unit: "%" },
  effectiveDateTime: "2026-03-01T00:00:00Z",
};

const MOCK_JOURNAL_ENTRY = {
  resourceType: "QuestionnaireResponse",
  id: "qr-1",
  status: "completed",
  authored: "2026-03-15T10:00:00Z",
  item: [
    {
      linkId: "transcript",
      text: "Raw transcript",
      answer: [{ valueString: "Je me sens bien aujourd'hui" }],
    },
    {
      linkId: "ai-response",
      text: "AI empathetic response",
      answer: [{ valueString: "Merci de partager, c'est formidable !" }],
    },
    {
      linkId: "symptoms",
      text: "Symptoms",
      answer: [],
    },
    {
      linkId: "emotional_state",
      text: "Emotional state",
      answer: [{ valueString: "positive" }],
    },
  ],
};

const MOCK_COMPOSITION = {
  resourceType: "Composition",
  id: "comp-1",
  status: "final",
  type: {
    coding: [
      { system: "http://loinc.org", code: "11488-4", display: "Consult note" },
    ],
  },
  subject: [{ reference: `Patient/${PATIENT_ID}` }],
  author: [{ reference: "Device/entre-deux" }],
  date: "2026-03-15T00:00:00Z",
  title: "Visit Brief",
  section: [
    {
      title: "Changements cles",
      text: { status: "generated", div: "<div>HbA1c amelioree</div>" },
    },
  ],
};

const MOCK_CONSENT = {
  resourceType: "Consent",
  id: "consent-1",
  status: "active",
  date: "2026-03-01",
  provision: [
    {
      purpose: [
        {
          system: "https://entredeux.health/fhir",
          code: "ai-processing",
          display: "Consent for ai-processing",
        },
      ],
    },
  ],
};

const MOCK_TIMELINE = {
  patient: MOCK_PATIENT,
  observations: [MOCK_OBSERVATION],
  questionnaire_responses: [MOCK_JOURNAL_ENTRY],
  compositions: [MOCK_COMPOSITION],
};

export async function mockAllApiRoutes(page: Page): Promise<void> {
  await page.route("**/api/v1/patients", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, json: MOCK_PATIENT });
    } else {
      await route.fallback();
    }
  });

  await page.route(`**/api/v1/patients/${PATIENT_ID}`, async (route) => {
    await route.fulfill({ json: MOCK_PATIENT });
  });

  await page.route(
    `**/api/v1/patients/${PATIENT_ID}/timeline`,
    async (route) => {
      await route.fulfill({ json: MOCK_TIMELINE });
    },
  );

  await page.route("**/api/v1/observations/analyze-image", async (route) => {
    await route.fulfill({
      json: {
        diagnostic_report: { resourceType: "DiagnosticReport" },
        observations: [MOCK_OBSERVATION],
        explanation: "Votre HbA1c est dans la cible.",
      },
    });
  });

  await page.route(
    `**/api/v1/observations/patients/${PATIENT_ID}`,
    async (route) => {
      await route.fulfill({ json: [MOCK_OBSERVATION] });
    },
  );

  await page.route("**/api/v1/questionnaire-responses", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, json: MOCK_JOURNAL_ENTRY });
    } else {
      await route.fallback();
    }
  });

  await page.route(
    `**/api/v1/questionnaire-responses/patients/${PATIENT_ID}`,
    async (route) => {
      await route.fulfill({ json: [MOCK_JOURNAL_ENTRY] });
    },
  );

  await page.route("**/api/v1/compositions/visit-brief", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, json: MOCK_COMPOSITION });
    } else {
      await route.fallback();
    }
  });

  await page.route(
    `**/api/v1/compositions/patients/${PATIENT_ID}`,
    async (route) => {
      await route.fulfill({ json: [MOCK_COMPOSITION] });
    },
  );

  await page.route("**/api/v1/consents", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, json: MOCK_CONSENT });
    } else {
      await route.fallback();
    }
  });

  await page.route(
    `**/api/v1/consents/patients/${PATIENT_ID}`,
    async (route) => {
      await route.fulfill({ json: [MOCK_CONSENT] });
    },
  );

  await page.route("**/api/v1/health", async (route) => {
    await route.fulfill({
      json: { status: "healthy", service: "entre-deux-api" },
    });
  });
}

export async function registerAndNavigateToDashboard(
  page: Page,
): Promise<void> {
  await mockAllApiRoutes(page);

  await page.goto("/bienvenue");
  await page.getByRole("button", { name: "Commencer" }).click();
  await page.getByLabel("Prenom").fill("Marie");
  await page.getByLabel("Nom", { exact: true }).fill("Laurent");
  await page.getByLabel("Identifiant patient").fill("TEST-001");
  await page.getByRole("button", { name: "Creer mon profil" }).click();

  await page.waitForURL("/");
}

export { PATIENT_ID, MOCK_PATIENT, MOCK_OBSERVATION, MOCK_JOURNAL_ENTRY };
