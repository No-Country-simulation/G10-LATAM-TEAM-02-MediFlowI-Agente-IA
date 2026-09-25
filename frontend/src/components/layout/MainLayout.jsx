import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      <Navbar toggleSidebar={toggleSidebar} />

      <div className="d-flex flex-grow-1" style={{ paddingTop: "60px" }}>
        <Sidebar isOpen={sidebarOpen} closeSidebar={closeSidebar} />

        <main
          className="flex-grow-1 p-3 p-md-4 main-content-wrapper"
          style={{
            marginLeft: "0px",
            minHeight: "calc(100vh - 120px)"
          }}
        >
          <div className="container-fluid max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>

      <footer className="footer mt-auto py-3 bg-white border-top text-center text-muted small position-relative" style={{ zIndex: 1020 }}>
        <div className="container">
          <span>MediFlow © 2026 - Sistema de Triaje Inteligente de Documentos Clínicos</span>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
