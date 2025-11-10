import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // forward API calls to your Flask backend during local dev
      '/api': 'http://localhost:5000'
    }
  }
})
