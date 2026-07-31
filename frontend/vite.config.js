import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // The SPA calls relative /api paths, so this proxy makes dev single-origin
    // and CORS a non-issue. Flask runs separately on :5000.
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Served by Flask in production (see backend/__init__.py::_register_spa).
    outDir: 'dist',
    emptyOutDir: true,
  },
})
