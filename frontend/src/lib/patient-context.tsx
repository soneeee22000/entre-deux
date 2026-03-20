import { useState, useEffect, useCallback, type ReactNode } from "react";
import type { FhirPatient } from "./fhir";
import { api } from "./api";
import { PatientContext } from "./patient-context-value";

const STORAGE_KEY = "entre-deux-patient-id";

export function PatientProvider({ children }: { children: ReactNode }) {
  const [patientId, setPatientId] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEY),
  );
  const [patient, setPatient] = useState<FhirPatient | null>(null);
  const [isLoading, setIsLoading] = useState(
    !!localStorage.getItem(STORAGE_KEY),
  );

  const fetchPatient = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      const data = await api.getPatient(id);
      setPatient(data);
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setPatientId(null);
      setPatient(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (patientId && !patient) {
      void fetchPatient(patientId);
    }
  }, [patientId, patient, fetchPatient]);

  const register = useCallback((newPatient: FhirPatient) => {
    localStorage.setItem(STORAGE_KEY, newPatient.id);
    setPatientId(newPatient.id);
    setPatient(newPatient);
    setIsLoading(false);
  }, []);

  const refresh = useCallback(async () => {
    if (patientId) {
      await fetchPatient(patientId);
    }
  }, [patientId, fetchPatient]);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setPatientId(null);
    setPatient(null);
  }, []);

  return (
    <PatientContext
      value={{ patientId, patient, isLoading, register, refresh, logout }}
    >
      {children}
    </PatientContext>
  );
}
