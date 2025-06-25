// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    host: true, // Allow external connections (useful for mobile testing)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Add timeout configuration
        timeout: 30000,
        // Add error handling logging
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying request:', req.method, req.url);
          });
        }
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Media proxy error:', err);
          });
        }
      },
    },
  },
  optimizeDeps: {
    include: ['quill', 'react-quill-new'], // pre-bundle both editors
    // Add exclude for packages that should not be pre-bundled
    exclude: ['@vite/client', '@vite/env']
  },
  css: {
    preprocessorOptions: {
      css: {
        charset: false
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  // Add build optimizations
  build: {
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        // Optimize chunk splitting
        manualChunks: {
          vendor: ['react', 'react-dom'],
          editor: ['quill', 'react-quill-new']
        }
      }
    }
  },
  // Add environment variable handling
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  // Enable source maps for development
  esbuild: {
    sourcemap: true,
  }
});
