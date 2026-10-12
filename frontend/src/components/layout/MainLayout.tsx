import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import logo from "../../assets/login/logo.png";
import { LuMenu } from "react-icons/lu";

const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5FBF7]">
      {/* Barra superior compacta solo para pantallas móviles/tablets (< lg) */}
      <header className="lg:hidden sticky top-0 z-30 bg-[#FAF9F5] border-b border-[#E8E6DF] px-4 py-2.5 flex items-center justify-between shadow-xs">
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label="Abrir menú"
          className="p-2 text-[#2C3E50] hover:bg-[#EBE8E1] rounded-lg transition-colors cursor-pointer border-0 bg-transparent"
        >
          <LuMenu size={22} />
        </button>
        <img src={logo} alt="MediFlow" className="h-8 w-auto object-contain" />
        <div className="w-8" />
      </header>

      <div className="flex flex-1 relative">
        {/* Sidebar Nav */}
        <Sidebar isOpen={sidebarOpen} closeSidebar={closeSidebar} />

        {/* Contenido principal de la aplicación */}
        <main className="flex-1 w-full lg:ml-[240px] min-h-screen transition-all duration-300">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
