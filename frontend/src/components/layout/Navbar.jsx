import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { FaUserCircle, FaBars, FaStethoscope, FaSignOutAlt } from "react-icons/fa";

const Navbar = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm fixed-top" style={{ zIndex: 1050 }}>
      <div className="container-fluid px-3">
        <button
          className="btn btn-link text-white me-3 p-1 border-0 d-flex align-items-center rounded"
          type="button"
          onClick={toggleSidebar}
          aria-label="Toggle navigation"
          title="Mostrar / Ocultar Menú"
        >
          <FaBars size={22} />
        </button>

        <a className="navbar-brand d-flex align-items-center fw-bold fs-4 me-auto" href="/dashboard">
          <FaStethoscope className="me-2" size={26} />
          MediFlow
          <span className="badge bg-light text-primary fs-7 ms-2 py-1 px-2 rounded-pill">Triaje IA</span>
        </a>

        <div className="d-flex align-items-center text-white">
          <div className="text-end me-3 d-none d-sm-block">
            <div className="fw-semibold small">{user?.nombre || "admin"}</div>
            <div className="text-light opacity-75" style={{ fontSize: "0.75rem" }}>
              Usuario: <strong className="text-white">{user?.username || "admin"}</strong>
            </div>
          </div>
          <FaUserCircle size={30} className="me-3" />

          <button
            className="btn btn-outline-light btn-sm fw-semibold d-flex align-items-center rounded-pill px-3"
            onClick={handleLogout}
            title="Cerrar sesión"
          >
            <FaSignOutAlt className="me-1.5" />
            <span className="d-none d-sm-inline">Salir</span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
