import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    pool: "threads",
    fileParallelism: false,
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
  server: {
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      // Proxy /api → backend en dev (evita CORS)
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
