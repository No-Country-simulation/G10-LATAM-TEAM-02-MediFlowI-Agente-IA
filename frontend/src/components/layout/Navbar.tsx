import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { FaUserCircle, FaBars, FaStethoscope, FaSignOutAlt } from "react-icons/fa";

const Navbar = ({ toggleSidebar }: { toggleSidebar: () => void }) => {
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
          aria-label="Mostrar u ocultar navegación"
          title="Mostrar u ocultar navegación"
        >
          <FaBars size={22} />
        </button>

        <Link className="navbar-brand d-flex align-items-center fw-bold fs-4 me-auto" to="/dashboard" aria-label="Ir al panel principal de MediFlow">
          <FaStethoscope className="me-2" size={26} />
          MediFlow
          <span className="badge bg-light text-primary fs-7 ms-2 py-1 px-2 rounded-pill">Triaje IA</span>
        </Link>

        <div className="d-flex align-items-center text-white">
          <div className="text-end me-3 d-none d-sm-block">
            <div className="fw-semibold small">{user?.nombres || "Usuario"}</div>
            <div className="text-light opacity-75" style={{ fontSize: "0.75rem" }}>
              <strong className="text-white">{user?.rol || "Sesión clínica"}</strong>
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
