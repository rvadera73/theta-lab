import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api to the real FastAPI backend (port 8000, same as
// every existing page already talks to) so `npm run dev` works against real
// live data without a second CORS-enabled backend config. Production build
// is plain static output -- FastAPI serves it from the same origin as the
// API, so no proxy/CORS is needed there at all. base: "./" keeps all asset
// references relative, matching how the existing static pages are served
// (no assumption about which path prefix/gateway sits in front, same real
// bug class already hit once with today.html's absolute vs relative fetch
// paths on 2026-10-15).
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});
