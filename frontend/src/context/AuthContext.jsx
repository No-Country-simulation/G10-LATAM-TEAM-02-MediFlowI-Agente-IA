import React, { createContext, useState, useEffect } from "react";
import { getCurrentUser, loginUser, logoutUser } from "../api/auth.api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedSession = localStorage.getItem("mediflow_auth_session");
    if (storedSession) {
      try {
        const session = JSON.parse(storedSession);
        getCurrentUser(session.access_token)
          .then((currentUser) => setUser({ ...currentUser, token: session.access_token }))
          .catch(() => localStorage.removeItem("mediflow_auth_session"))
          .finally(() => setLoading(false));
        return;
      } catch (e) {
        localStorage.removeItem("mediflow_auth_session");
      }
    }
    setLoading(false);
  }, []);

  const login = async (documentoIdentidad, password) => {
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
      return { success: false, message: error.message };
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
