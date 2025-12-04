import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  // Production build settings
  build: {
    outDir: 'dist',
    sourcemap: false
  },
  // Define environment variables for client
  define: {
    // Fallback for production API URL if not set
    'import.meta.env.VITE_API_BASE': JSON.stringify(
      process.env.VITE_API_BASE || ''
    )
  }
})


