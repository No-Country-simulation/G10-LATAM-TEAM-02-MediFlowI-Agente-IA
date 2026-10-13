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
    <div className="min-h-screen flex flex-col bg-[#f5f7fb] relative overflow-x-hidden">
      {/* Orbes de ambiente difuminados con los colores distintivos de MediFlow */}
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden z-0">
        <div className="absolute -top-24 left-[15%] w-[600px] h-[600px] bg-[#ffe4ec] rounded-full blur-[90px] opacity-60" />
        <div className="absolute -top-40 right-[10%] w-[700px] h-[700px] bg-[#e8dcff] rounded-full blur-[100px] opacity-70" />
        <div className="absolute top-[35%] right-[5%] w-[550px] h-[550px] bg-[#d6f5e3] rounded-full blur-[85px] opacity-55" />
        <div className="absolute bottom-[5%] left-[25%] w-[500px] h-[500px] bg-[#e0f2fe] rounded-full blur-[90px] opacity-50" />
      </div>

      {/* Barra superior compacta solo para pantallas móviles/tablets (< lg) */}
      <header className="lg:hidden sticky top-0 z-10 bg-[#FAF9F5]/95 backdrop-blur-md border-b border-[#E8E6DF] px-4 py-3 flex items-center justify-between shadow-xs">
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label="Abrir menú"
          className="p-2 text-[#2C3E50] hover:bg-[#EBE8E1] rounded-lg transition-colors cursor-pointer border-0 bg-transparent"
        >
          <LuMenu size={24} />
        </button>
        <img src={logo} alt="MediFlow" className="h-10 sm:h-12 w-auto object-contain" />
        <div className="w-8" />
      </header>

      <div className="flex flex-1 relative z-10">
        {/* Sidebar Nav */}
        <Sidebar isOpen={sidebarOpen} closeSidebar={closeSidebar} />

        {/* Contenido principal de la aplicación con espaciado equilibrado y responsive */}
        <main className="flex-1 w-full lg:ml-[250px] min-h-screen transition-all duration-300 flex flex-col">
          <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-10 flex-1">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
