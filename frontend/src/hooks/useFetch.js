import { useCallback, useEffect, useState } from "react";

// Runs `fetcher` on mount and whenever `deps` change. `reload()` refetches without
// flashing the loading state, so lists stay visible while they refresh.
export default function useFetch(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, error: "", loading: true });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, error: "" }));
    fetcher()
      .then((data) => !cancelled && setState({ data, error: "", loading: false }))
      .catch((err) => !cancelled && setState({ data: null, error: err.message, loading: false }));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { ...state, reload };
}
