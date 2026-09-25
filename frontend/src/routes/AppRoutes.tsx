import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import MainLayout from "../components/layout/MainLayout";
import Loading from '../components/common/Loading'

const Login = lazy(() => import('../pages/Login'))
const Dashboard = lazy(() => import('../pages/Dashboard'))
const NewDocument = lazy(() => import('../pages/NewDocument'))
const DocumentDetail = lazy(() => import('../pages/DocumentDetail'))
const Documents = lazy(() => import('../pages/Documents'))
const Audit = lazy(() => import('../pages/Audit'))
const AuditDetail = lazy(() => import('../pages/AuditDetail'))
const TriageConsoleView = lazy(() => import('../pages/TriageConsoleView'))
const UsersManagementView = lazy(() => import('../pages/UsersManagementView'))
const StorageSettingsView = lazy(() => import('../pages/StorageSettingsView'))
const DocumentationView = lazy(() => import('../pages/DocumentationView'))
const PatientsManagementView = lazy(() => import('../pages/PatientsManagementView'))

const AppRoutes = () => {
  return (
    <Suspense fallback={<Loading message="Cargando módulo..." />}>
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
        <Route path="/pacientes" element={<PatientsManagementView />} />
        <Route path="/pacientes-gestion" element={<PatientsManagementView />} />
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
    </Suspense>
  );
};

export default AppRoutes;
