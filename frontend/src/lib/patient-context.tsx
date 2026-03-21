import { useState, useEffect, useCallback, type ReactNode } from "react";
import type { FhirPatient } from "./fhir";
import { api } from "./api";
import { useAuth } from "./use-auth";
import { PatientContext } from "./patient-context-value";

export function PatientProvider({ children }: { children: ReactNode }) {
  const { patientId: authPatientId, isAuthenticated } = useAuth();
  const [patient, setPatient] = useState<FhirPatient | null>(null);
  const [isLoading, setIsLoading] = useState(!!authPatientId);

  const fetchPatient = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      const data = await api.getPatient(id);
      setPatient(data);
    } catch {
      setPatient(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authPatientId && isAuthenticated && !patient) {
      void fetchPatient(authPatientId);
    }
    if (!isAuthenticated) {
      setPatient(null);
      setIsLoading(false);
    }
  }, [authPatientId, isAuthenticated, patient, fetchPatient]);

  const register = useCallback((newPatient: FhirPatient) => {
    setPatient(newPatient);
    setIsLoading(false);
  }, []);

  const refresh = useCallback(async () => {
    if (authPatientId) {
      await fetchPatient(authPatientId);
    }
  }, [authPatientId, fetchPatient]);

  const logout = useCallback(() => {
    setPatient(null);
  }, []);

  return (
    <PatientContext
      value={{
        patientId: authPatientId,
        patient,
        isLoading,
        register,
        refresh,
        logout,
      }}
    >
      {children}
    </PatientContext>
  );
}
