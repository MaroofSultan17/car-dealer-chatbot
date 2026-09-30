import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../public',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': process.env.API_URL ?? 'http://localhost:8000',
    },
  },
})
