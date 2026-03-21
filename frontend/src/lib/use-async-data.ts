import { useState, useEffect, useCallback, useRef } from "react";
import { ApiRequestError } from "./api";

interface AsyncDataState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
  retry: () => void;
}

function getErrorMessage(err: unknown): string {
  if (err instanceof ApiRequestError) {
    if (err.status === 502) {
      return "Le service d'IA est temporairement indisponible. Reessayez dans quelques instants.";
    }
    if (err.status === 504) {
      return "Le service d'IA met trop de temps a repondre. Reessayez dans quelques instants.";
    }
    return err.message;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "Une erreur est survenue.";
}

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  deps: unknown[],
): AsyncDataState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const load = useCallback(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetcherRef
      .current()
      .then((result) => {
        if (!cancelled) {
          setData(result);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(getErrorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    return load();
  }, [load]);

  const retry = useCallback(() => {
    load();
  }, [load]);

  return { data, error, isLoading, retry };
}

export { getErrorMessage };
