import { useContext } from "react";
import {
  PatientContext,
  type PatientContextValue,
} from "./patient-context-value";

export function usePatient(): PatientContextValue {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error("usePatient must be used within a PatientProvider");
  }
  return context;
}
