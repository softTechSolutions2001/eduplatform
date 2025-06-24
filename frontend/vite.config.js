// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api':   { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/media': { target: 'http://localhost:8000', changeOrigin: true, secure: false },
    },
  },

  optimizeDeps: {
    include: ['quill', 'react-quill-new'], // pre-bundle both editors
  },

  css: {
    preprocessorOptions: { css: { charset: false } },
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
