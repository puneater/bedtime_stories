/* eslint-env node */
// frontend/vite.config.js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default ({ mode }) => {
  // Load env vars from .env, .env.local, etc. (only VITE_* are exposed to client)
  const env = loadEnv(mode, process.cwd(), '')
  const API_TARGET = env.VITE_API_TARGET || 'http://localhost:5000'

  return defineConfig({
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: API_TARGET,
          changeOrigin: true,
        },
        '/static': {
          target: API_TARGET,
          changeOrigin: true,
        },
      },
    },
  })
}
