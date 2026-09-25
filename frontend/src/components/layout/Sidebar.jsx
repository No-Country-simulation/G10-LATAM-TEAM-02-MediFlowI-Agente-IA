import React from "react";
import { NavLink } from "react-router-dom";
import {
  FaTachometerAlt,
  FaStethoscope,
  FaFileUpload,
  FaUserCog,
  FaCog,
  FaClipboardCheck,
  FaHistory,
  FaBook,
  FaChevronLeft
} from "react-icons/fa";

const Sidebar = ({ isOpen, closeSidebar }) => {
  const navItems = [
    {
      path: "/dashboard",
      label: "Dashboard",
      icon: <FaTachometerAlt className="me-2 fs-5" />
    },
    {
      path: "/triaje",
      label: "Triaje Clínico",
      icon: <FaStethoscope className="me-2 fs-5" />
    },
    {
      path: "/documentos/nuevo",
      label: "Subir Archivo",
      icon: <FaFileUpload className="me-2 fs-5" />
    },
    {
      path: "/usuarios",
      label: "Gestión de Usuarios",
      icon: <FaUserCog className="me-2 fs-5" />
    },
    {
      path: "/configuracion",
      label: "Configuración",
      icon: <FaCog className="me-2 fs-5" />
    },
    {
      path: "/auditoria",
      label: "Auditoría",
      icon: <FaClipboardCheck className="me-2 fs-5" />
    },
    {
      path: "/documentos",
      label: "Historial",
      icon: <FaHistory className="me-2 fs-5" />
    },
    {
      path: "/documentacion",
      label: "Documentación",
      icon: <FaBook className="me-2 fs-5" />
    }
  ];

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
        className="bg-white border-end position-fixed start-0 bottom-0 shadow-sm"
        style={{
          width: "250px",
          top: "60px",
          zIndex: 1040,
          transition: "transform 0.3s ease-in-out",
          transform: isOpen ? "translateX(0)" : "translateX(-100%)"
        }}
      >
        <div className="py-3 px-3">
          <div className="d-flex align-items-center justify-content-between text-uppercase text-muted fw-bold small mb-2 px-3">
            <span>Menú Principal</span>
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
      </aside>
    </>
  );
};

export default Sidebar;
