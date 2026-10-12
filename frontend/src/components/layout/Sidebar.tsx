import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import logo from "../../assets/login/logo.png";
import {
  LuPlus,
  LuLayoutDashboard,
  LuStethoscope,
  LuUsers,
  LuSlidersVertical,
  LuFolder,
  LuSquareCheck,
  LuSettings,
  LuBookOpen,
  LuHouse,
  LuChevronUp,
  LuLogOut,
} from "react-icons/lu";

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
}

interface NavItemConfig {
  path: string;
  label: string;
  icon: React.ReactNode;
  allowedRoles?: string[];
  exact?: boolean;
}

const Sidebar = ({ isOpen, closeSidebar }: SidebarProps) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userRole = user?.rol?.toUpperCase();
  const isPendiente = userRole === "PENDIENTE";
  const canCreateRouting = userRole === "ADMINISTRADOR" || userRole === "OPERADOR";

  const userInitial = (
    user?.nombres?.charAt(0) ||
    user?.correo?.charAt(0) ||
    "N"
  ).toUpperCase();

  const fullName = user
    ? `${user.nombres} ${user.apellidos}`
    : "Nombre del usuario";
  const userEmail = user?.correo || "correo@axiom.ai";

  // Lista unificada de todos los módulos del sistema con diseño coherente
  const navModules: NavItemConfig[] = [
    {
      path: "/dashboard",
      label: "Dashboard",
      icon: <LuLayoutDashboard size={16} className="shrink-0" />,
      exact: true,
    },
    {
      path: "/triaje",
      label: "Triaje Clínico",
      icon: <LuStethoscope size={16} className="shrink-0" />,
    },
    {
      path: "/pacientes",
      label: "Pacientes",
      icon: <LuUsers size={16} className="shrink-0" />,
    },
    {
      path: "/auditoria",
      label: "Solicitudes de intervención manual",
      icon: <LuSlidersVertical size={16} className="shrink-0" />,
      allowedRoles: ["ADMINISTRADOR", "COORDINADOR", "AUDITOR", "SUPERVISOR"],
    },
    {
      path: "/documentos",
      label: "Historial de enrutamiento",
      icon: <LuFolder size={16} className="shrink-0" />,
      exact: true,
    },
    {
      path: "/solicitudes",
      label: "Solicitudes de acceso",
      icon: <LuSquareCheck size={16} className="shrink-0" />,
      allowedRoles: ["ADMINISTRADOR"],
    },
    {
      path: "/configuracion",
      label: "Configuración",
      icon: <LuSettings size={16} className="shrink-0" />,
      allowedRoles: ["ADMINISTRADOR"],
    },
    {
      path: "/documentacion",
      label: "Documentación",
      icon: <LuBookOpen size={16} className="shrink-0" />,
    },
  ];

  // Filtrado según roles
  const visibleModules = navModules.filter((item) => {
    if (!item.allowedRoles) return true;
    return userRole ? item.allowedRoles.includes(userRole) : false;
  });

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden backdrop-blur-sm"
          onClick={closeSidebar}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-[240px] bg-[#FAF9F5] border-r border-[#E8E6DF] flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{
          boxShadow: "0 0 20px rgba(0, 0, 0, 0.02)",
        }}
      >
        <div className="flex flex-col flex-1 overflow-y-auto">
          {/* Logo centrado de MediFlow */}
          <div className="pt-7 pb-5 px-5 flex justify-center items-center">
            <NavLink
              to="/dashboard"
              className="flex flex-col items-center select-none no-underline"
              onClick={() => {
                if (window.innerWidth < 1024) closeSidebar();
              }}
            >
              <img
                src={logo}
                alt="MediFlow"
                className="h-14 w-auto object-contain hover:opacity-95 transition-opacity"
              />
            </NavLink>
          </div>

          {/* Menú para usuario con rol PENDIENTE: únicamente Inicio */}
          {isPendiente ? (
            <div className="mt-2 w-full">
              <NavLink
                to="/dashboard"
                end
                className={({ isActive }) =>
                  `w-full flex items-center gap-3 px-5 py-3 text-[13px] font-medium transition-colors no-underline ${
                    isActive
                      ? "bg-[#EDEBE6] text-[#1E293B] font-semibold border-y border-[#E2DFD8]"
                      : "text-[#4B5563] hover:bg-[#F3F1EC] hover:text-[#1E293B]"
                  }`
                }
                style={{ fontFamily: "'Montserrat', sans-serif" }}
                onClick={() => {
                  if (window.innerWidth < 1024) closeSidebar();
                }}
              >
                <LuHouse size={16} className="text-[#4B5563] shrink-0" />
                <span>Inicio</span>
              </NavLink>
            </div>
          ) : (
            <>
              {/* Botón "+ Nuevo enrutamiento" destacado en barra beige */}
              {canCreateRouting && (
                <div className="w-full mb-2">
                  <NavLink
                    to="/documentos/nuevo"
                    className={({ isActive }) =>
                      `w-full flex items-center gap-2.5 px-5 py-3.5 text-[13px] font-semibold tracking-wide transition-colors no-underline ${
                        isActive
                          ? "bg-[#EDEBE6] text-[#1E293B] border-y border-[#E2DFD8]"
                          : "bg-[#EDEBE6] text-[#2C3E50] hover:bg-[#E4E0D6] border-y border-[#E2DFD8]"
                      }`
                    }
                    style={{ fontFamily: "'Montserrat', sans-serif" }}
                    onClick={() => {
                      if (window.innerWidth < 1024) closeSidebar();
                    }}
                  >
                    <LuPlus size={16} className="text-[#1E293B] stroke-[2.5] shrink-0" />
                    <span>Nuevo enrutamiento</span>
                  </NavLink>
                </div>
              )}

              {/* Lista completa de módulos con el mismo diseño uniforme */}
              <nav className="flex flex-col gap-0.5 w-full pb-3">
                {visibleModules.map((mod) => (
                  <NavLink
                    key={mod.path}
                    to={mod.path}
                    end={mod.exact}
                    className={({ isActive }) =>
                      `w-full flex items-center gap-3 px-5 py-3 text-[13px] leading-tight transition-colors no-underline ${
                        isActive
                          ? "bg-[#EDEBE6] text-[#1E293B] font-semibold"
                          : "text-[#4B5563] hover:bg-[#F3F1EC] hover:text-[#1E293B]"
                      }`
                    }
                    style={{ fontFamily: "'Montserrat', sans-serif" }}
                    onClick={() => {
                      if (window.innerWidth < 1024) closeSidebar();
                    }}
                  >
                    <span className="text-[#4B5563]">{mod.icon}</span>
                    <span className="text-left">{mod.label}</span>
                  </NavLink>
                ))}
              </nav>
            </>
          )}
        </div>

        {/* Sección inferior: Usuario logueado y Logout */}
        <div className="p-4 border-t border-[#E8E6DF] bg-[#FAF9F5]">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0 select-none shadow-sm"
                style={{ backgroundColor: "#204A79" }}
              >
                {userInitial}
              </div>
              <div className="overflow-hidden min-w-0">
                <div
                  className="text-xs font-bold text-[#1F2041] truncate"
                  style={{ fontFamily: "'Montserrat', sans-serif" }}
                  title={fullName}
                >
                  {fullName}
                </div>
                <div
                  className="text-[11px] text-[#8A92A6] truncate"
                  style={{ fontFamily: "'Montserrat', sans-serif" }}
                  title={userEmail}
                >
                  {userEmail}
                </div>
              </div>
            </div>
            <LuChevronUp size={15} className="text-[#64748B] shrink-0" />
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="flex items-center gap-2 mt-4 text-xs font-semibold text-[#204A79] hover:text-[#153457] cursor-pointer bg-transparent border-0 transition-colors p-0"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            <LuLogOut size={14} className="stroke-[2.2]" />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
