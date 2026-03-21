import { useState, useCallback, useEffect, type ReactNode } from "react";
import { api } from "./api";
import { AuthContext } from "./auth-context-value";

export type { AuthContextValue } from "./auth-context-value";
export { AuthContext } from "./auth-context-value";

const AUTH_TOKEN_KEY = "entre-deux-access-token";
const REFRESH_TOKEN_KEY = "entre-deux-refresh-token";
const PATIENT_ID_KEY = "entre-deux-patient-id";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(() =>
    localStorage.getItem(AUTH_TOKEN_KEY),
  );
  const [patientId, setPatientId] = useState<string | null>(() =>
    localStorage.getItem(PATIENT_ID_KEY),
  );

  const storeTokens = useCallback(
    (access: string, refresh: string, pid: string) => {
      localStorage.setItem(AUTH_TOKEN_KEY, access);
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
      localStorage.setItem(PATIENT_ID_KEY, pid);
      setAccessToken(access);
      setPatientId(pid);
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(PATIENT_ID_KEY);
    setAccessToken(null);
    setPatientId(null);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await api.auth.login(email, password);
      storeTokens(
        response.access_token,
        response.refresh_token,
        response.patient_id,
      );
    },
    [storeTokens],
  );

  const register = useCallback(
    async (data: {
      email: string;
      password: string;
      given_name: string;
      family_name: string;
      identifier: string;
    }) => {
      const response = await api.auth.register(data);
      storeTokens(
        response.access_token,
        response.refresh_token,
        response.patient_id,
      );
    },
    [storeTokens],
  );

  useEffect(() => {
    const tryRefresh = async () => {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken || !accessToken) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await api.auth.refresh(refreshToken);
        storeTokens(
          response.access_token,
          response.refresh_token,
          response.patient_id,
        );
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    };
    void tryRefresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isAuthenticated = !!accessToken;

  return (
    <AuthContext
      value={{
        isAuthenticated,
        isLoading,
        patientId,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext>
  );
}
