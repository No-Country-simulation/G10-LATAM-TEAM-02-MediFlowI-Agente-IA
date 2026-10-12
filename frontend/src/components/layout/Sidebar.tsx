import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import logo from "../../assets/login/logo.png";
import {
  LuPlus,
  LuSlidersVertical,
  LuFolder,
  LuSquareCheck,
  LuHouse,
  LuChevronUp,
  LuLogOut,
  LuUsers,
  LuSettings,
} from "react-icons/lu";

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
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
  const isAdmin = userRole === "ADMINISTRADOR";

  const userInitial = (
    user?.nombres?.charAt(0) ||
    user?.correo?.charAt(0) ||
    "N"
  ).toUpperCase();

  const fullName = user
    ? `${user.nombres} ${user.apellidos}`
    : "Nombre del usuario";
  const userEmail = user?.correo || "correo@axiom.ai";

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
        className={`fixed top-0 bottom-0 left-0 z-50 w-[240px] bg-[#FAF9F5]/90 sm:bg-[#FAF9F5] backdrop-blur-md border-r border-[#E8E6DF] flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
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

          {/* Opción única para usuario PENDIENTE: Inicio */}
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
              {/* Botón "+ Nuevo enrutamiento" destacado en fondo beige claro */}
              <div className="w-full mb-3">
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

              {/* Menú de opciones */}
              <nav className="flex flex-col gap-1 w-full">
                {/* 1. Solicitudes de intervención manual */}
                <NavLink
                  to="/auditoria"
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
                  <LuSlidersVertical size={16} className="text-[#4B5563] shrink-0" />
                  <span className="text-left">Solicitudes de intervención manual</span>
                </NavLink>

                {/* 2. Historial de enrutamiento */}
                <NavLink
                  to="/documentos"
                  end
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
                  <LuFolder size={16} className="text-[#4B5563] shrink-0" />
                  <span>Historial de enrutamiento</span>
                </NavLink>

                {/* 3. Solicitudes de acceso (ADMINISTRADOR) */}
                {isAdmin && (
                  <NavLink
                    to="/solicitudes"
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
                    <LuSquareCheck size={16} className="text-[#4B5563] shrink-0" />
                    <span>Solicitudes de acceso</span>
                  </NavLink>
                )}

                {/* Opciones secundarias del sistema clínico */}
                {isAdmin && (
                  <>
                    <NavLink
                      to="/pacientes"
                      className={({ isActive }) =>
                        `w-full flex items-center gap-3 px-5 py-2.5 text-[12px] text-[#64748B] hover:text-[#1E293B] hover:bg-[#F3F1EC] transition-colors no-underline mt-2 ${
                          isActive ? "bg-[#EDEBE6] text-[#1E293B] font-semibold" : ""
                        }`
                      }
                      style={{ fontFamily: "'Montserrat', sans-serif" }}
                      onClick={() => {
                        if (window.innerWidth < 1024) closeSidebar();
                      }}
                    >
                      <LuUsers size={15} className="shrink-0" />
                      <span>Pacientes</span>
                    </NavLink>
                    <NavLink
                      to="/configuracion"
                      className={({ isActive }) =>
                        `w-full flex items-center gap-3 px-5 py-2 text-[12px] text-[#64748B] hover:text-[#1E293B] hover:bg-[#F3F1EC] transition-colors no-underline ${
                          isActive ? "bg-[#EDEBE6] text-[#1E293B] font-semibold" : ""
                        }`
                      }
                      style={{ fontFamily: "'Montserrat', sans-serif" }}
                      onClick={() => {
                        if (window.innerWidth < 1024) closeSidebar();
                      }}
                    >
                      <LuSettings size={15} className="shrink-0" />
                      <span>Configuración OCI</span>
                    </NavLink>
                  </>
                )}
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
