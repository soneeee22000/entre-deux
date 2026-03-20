import { createContext } from "react";
import type { FhirPatient } from "./fhir";

export interface PatientContextValue {
  patientId: string | null;
  patient: FhirPatient | null;
  isLoading: boolean;
  register: (patient: FhirPatient) => void;
  refresh: () => Promise<void>;
  logout: () => void;
}

export const PatientContext = createContext<PatientContextValue | null>(null);
