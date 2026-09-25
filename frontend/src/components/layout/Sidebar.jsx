import React from "react";
import { NavLink } from "react-router-dom";
import { FaTachometerAlt, FaFileUpload, FaClipboardCheck, FaHistory, FaUserCog, FaCog } from "react-icons/fa";

const Sidebar = ({ isOpen, closeSidebar }) => {
  const navItems = [
    {
      path: "/dashboard",
      label: "Dashboard",
      icon: <FaTachometerAlt className="me-2 fs-5" />
    },
    {
      path: "/documentos/nuevo",
      label: "Subir Archivo",
      icon: <FaFileUpload className="me-2 fs-5" />
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
      path: "/admin-triaje",
      label: "Consola & Usuarios",
      icon: <FaUserCog className="me-2 fs-5" />
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 bg-dark opacity-50 d-lg-none"
          style={{ zIndex: 1030 }}
          onClick={closeSidebar}
        ></div>
      )}

      <aside
        className={`bg-white border-end position-fixed top-0 bottom-0 start-0 shadow-sm ${
          isOpen ? "d-block" : "d-none d-lg-block"
        }`}
        style={{
          width: "250px",
          paddingTop: "65px",
          zIndex: 1035,
          transition: "all 0.3s ease-in-out"
        }}
      >
        <div className="py-3 px-3">
          <div className="text-uppercase text-muted fw-bold small mb-2 px-3">Menú Principal</div>
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
                  onClick={closeSidebar}
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
