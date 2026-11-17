import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { clearSession, isLoggedIn, setRole, setSession } from "../auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(!isLoggedIn());

  const refresh = useCallback(async () => {
    if (!isLoggedIn()) {
      setUser(null);
      setReady(true);
      return;
    }
    try {
      const me = await api.getMe();
      setRole(me.user_role);
      setUser(me);
    } catch {
      // Expired or invalid token: fall back to a logged-out state.
      clearSession();
      setUser(null);
    }
    setReady(true);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const signIn = useCallback(
    async (session) => {
      setSession(session);
      await refresh();
    },
    [refresh]
  );

  const signOut = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, ready, signIn, signOut, refresh }),
    [user, ready, signIn, signOut, refresh]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
