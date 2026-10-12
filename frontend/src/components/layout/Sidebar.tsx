import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import {
  FaTachometerAlt,
  FaStethoscope,
  FaUserInjured,
  FaFileUpload,
  FaCog,
  FaClipboardCheck,
  FaHistory,
  FaBook,
  FaChevronLeft,
  FaHome,
  FaSignOutAlt,
} from "react-icons/fa";

interface SidebarProps { isOpen: boolean; closeSidebar: () => void }

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  allowedRoles?: string[];
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

  const allNavItems: NavItem[] = isPendiente
    ? [
        {
          path: "/dashboard",
          label: "Inicio",
          icon: <FaHome className="me-2 fs-5" />,
        },
      ]
    : [
        {
          path: "/dashboard",
          label: "Dashboard",
          icon: <FaTachometerAlt className="me-2 fs-5" />,
        },
        {
          path: "/pacientes",
          label: "Pacientes",
          icon: <FaUserInjured className="me-2 fs-5" />,
        },
        {
          path: "/triaje",
          label: "Triaje Clínico",
          icon: <FaStethoscope className="me-2 fs-5" />,
        },
        {
          path: "/documentos/nuevo",
          label: "Subir Archivo",
          icon: <FaFileUpload className="me-2 fs-5" />,
          allowedRoles: ["ADMINISTRADOR", "OPERADOR"],
        },
        {
          path: "/usuarios",
          label: "Solicitudes de acceso",
          icon: <FaClipboardCheck className="me-2 fs-5" />,
          allowedRoles: ["ADMINISTRADOR"],
        },
        {
          path: "/configuracion",
          label: "Configuración",
          icon: <FaCog className="me-2 fs-5" />,
          allowedRoles: ["ADMINISTRADOR"],
        },
        {
          path: "/auditoria",
          label: "Auditoría (HITL)",
          icon: <FaClipboardCheck className="me-2 fs-5" />,
          allowedRoles: ["ADMINISTRADOR", "COORDINADOR", "AUDITOR", "SUPERVISOR"],
        },
        {
          path: "/documentos",
          label: "Historial",
          icon: <FaHistory className="me-2 fs-5" />,
        },
        {
          path: "/documentacion",
          label: "Documentación",
          icon: <FaBook className="me-2 fs-5" />,
        },
      ];

  const navItems = allNavItems.filter((item) => {
    if (!item.allowedRoles) return true;
    return userRole ? item.allowedRoles.includes(userRole) : false;
  });

  const userInitial = (user?.nombres?.charAt(0) || user?.correo?.charAt(0) || "U").toUpperCase();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="position-fixed start-0 w-100 bg-dark opacity-50 d-lg-none"
          style={{ top: "60px", bottom: 0, zIndex: 1035 }}
          onClick={closeSidebar}
        ></div>
      )}

      <aside
        className="bg-white border-end position-fixed start-0 bottom-0 shadow-sm d-flex flex-column justify-content-between"
        style={{
          width: "250px",
          top: "60px",
          zIndex: 1040,
          transition: "transform 0.3s ease-in-out",
          transform: isOpen ? "translateX(0)" : "translateX(-100%)",
        }}
      >
        <div className="py-3 px-3">
          <div className="d-flex align-items-center justify-content-between text-uppercase text-muted fw-bold small mb-2 px-3">
            <span>{isPendiente ? "Bienvenida" : "Menú Principal"}</span>
            <button
              type="button"
              className="btn btn-sm btn-light text-muted p-1 border-0 rounded-circle"
              onClick={closeSidebar}
              title="Ocultar Menú"
            >
              <FaChevronLeft size={14} />
            </button>
          </div>
          <ul className="nav nav-pills flex-column mb-auto">
            {navItems.map((item) => (
              <li className="nav-item mb-1" key={item.path}>
                <NavLink
                  to={item.path}
                  end={item.path === "/documentos"}
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center px-3 py-2.5 rounded-3 fw-medium ${
                      isActive ? "active bg-primary text-white" : "text-dark hover-bg-light"
                    }`
                  }
                  onClick={() => {
                    if (window.innerWidth < 992) closeSidebar();
                  }}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </div>

        {/* Perfil en la parte inferior del Sidebar */}
        <div className="p-3 border-top bg-light/50">
          <div className="d-flex align-items-center gap-2 mb-2">
            <div
              className="d-flex align-items-center justify-content-center text-white rounded-circle fw-bold text-sm shadow-sm shrink-0"
              style={{ width: "36px", height: "36px", backgroundColor: "#1e3a5f" }}
            >
              {userInitial}
            </div>
            <div className="overflow-hidden" style={{ minWidth: 0 }}>
              <div className="fw-semibold text-truncate small text-dark">
                {user ? `${user.nombres} ${user.apellidos}` : "Usuario MediFlow"}
              </div>
              <div className="text-muted text-truncate" style={{ fontSize: "0.75rem" }}>
                {user?.correo || user?.rol || "Sin correo"}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="btn btn-sm btn-outline-danger w-100 d-flex align-items-center justify-content-center gap-1.5 py-1 text-xs"
          >
            <FaSignOutAlt size={12} />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
