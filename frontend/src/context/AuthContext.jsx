import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user session exists in localStorage
    const storedUser = localStorage.getItem("mediflow_auth_user");
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        if (parsed && (parsed.username === "admin" || parsed.rol === "AUDITOR_LEAD")) {
          parsed.rol = "ADMINISTRADOR";
        }
        setUser(parsed);
      } catch (e) {
        localStorage.removeItem("mediflow_auth_user");
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    // Demo credential validation: username === 'admin' and password === 'admin'
    const trimmedUser = (username || "").trim();
    const trimmedPass = (password || "").trim();

    if (trimmedUser === "admin" && trimmedPass === "admin") {
      const userData = {
        username: "admin",
        nombre: "Administrador Clínico",
        email: "admin@mediflow.com",
        rol: "ADMINISTRADOR",
        token: "mock-jwt-token-mediflow-admin-2026"
      };
      setUser(userData);
      localStorage.setItem("mediflow_auth_user", JSON.stringify(userData));
      return { success: true, user: userData };
    } else {
      return {
        success: false,
        message: "Credenciales inválidas. Usuario o contraseña incorrectos."
      };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("mediflow_auth_user");
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
