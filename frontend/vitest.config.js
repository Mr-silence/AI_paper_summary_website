import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    fs: {
      allow: ['..']
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['../tests/frontend/**/*.spec.js'],
    setupFiles: ['../tests/frontend/setup.js']
  }
})
