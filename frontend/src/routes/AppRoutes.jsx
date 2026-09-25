import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import MainLayout from "../components/layout/MainLayout";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import NewDocument from "../pages/NewDocument";
import DocumentDetail from "../pages/DocumentDetail";
import Documents from "../pages/Documents";
import Audit from "../pages/Audit";
import AuditDetail from "../pages/AuditDetail";
import TriageConsoleView from "../pages/TriageConsoleView";
import UsersManagementView from "../pages/UsersManagementView";
import StorageSettingsView from "../pages/StorageSettingsView";
import DocumentationView from "../pages/DocumentationView";

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Route */}
      <Route path="/login" element={<Login />} />

      {/* Protected Routes */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/documentos" element={<Documents />} />
        <Route path="/documentos/nuevo" element={<NewDocument />} />
        <Route path="/documentos/:id" element={<DocumentDetail />} />
        <Route path="/auditoria" element={<Audit />} />
        <Route path="/auditoria/:id" element={<AuditDetail />} />
        <Route path="/triaje" element={<TriageConsoleView />} />
        <Route path="/admin-triaje" element={<TriageConsoleView />} />
        <Route path="/usuarios" element={<UsersManagementView />} />
        <Route path="/admin-usuarios" element={<UsersManagementView />} />
        <Route path="/configuracion" element={<StorageSettingsView />} />
        <Route path="/documentacion" element={<DocumentationView />} />
      </Route>

      {/* Catch-all fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes;
