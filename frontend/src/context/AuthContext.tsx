import { useState, useEffect, type ReactNode } from "react";
import { getCurrentUser, loginUser, logoutUser } from "../api/auth.api";
import { AuthContext, type LoginResult, type SessionUser } from './auth-context'

function readStoredToken(): string | null {
  try {
    const stored = localStorage.getItem('mediflow_auth_session')
    return stored ? JSON.parse(stored).access_token ?? null : null
  } catch {
    localStorage.removeItem('mediflow_auth_session')
    return null
  }
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [initialToken] = useState(readStoredToken)
  const [loading, setLoading] = useState(Boolean(initialToken));

  useEffect(() => {
    if (!initialToken) return
    let active = true
    getCurrentUser(initialToken)
      .then((currentUser) => active && setUser({ ...currentUser, token: initialToken }))
      .catch(() => localStorage.removeItem("mediflow_auth_session"))
      .finally(() => active && setLoading(false));
    return () => { active = false }
  }, [initialToken]);

  const login = async (documentoIdentidad: string, password: string): Promise<LoginResult> => {
    try {
      const session = await loginUser(documentoIdentidad, password);
      const userData = { ...session.user, token: session.access_token };
      setUser(userData);
      localStorage.setItem(
        "mediflow_auth_session",
        JSON.stringify({ access_token: session.access_token }),
      );
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : 'Error al iniciar sesión' };
    }
  };

  const logout = () => {
    if (user?.token) logoutUser(user.token);
    setUser(null);
    localStorage.removeItem("mediflow_auth_session");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token: user?.token ?? null,
        isAuthenticated: !!user,
        loading,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
