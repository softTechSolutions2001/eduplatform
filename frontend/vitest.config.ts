/// <reference types="vite/client" />
/// <reference types="vitest" />
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
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
        timeout: 30000,
        configure: (proxy, _options) => {
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
        configure: (proxy, _options) => {
          proxy.on('error', (err, req, res) => {
            console.error('Media proxy error:', err);
          });
        }
      },
    },
  },
  optimizeDeps: {
    include: ['quill', 'react-quill-new'], // pre-bundle both editors
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
  build: {
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          editor: ['quill', 'react-quill-new']
        }
      }
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
  esbuild: {
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    include: ['./test/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        'test/setup.ts',
        'vite.config.ts'
      ],
    },
    // Add TypeScript-specific test configuration
    typecheck: {
      checker: 'tsc',
      include: ['**/*.{test,spec}.{ts,tsx}'],
    },
    // Mock handling for tests
    deps: {
      inline: ['@testing-library/jest-dom']
    }
  },
});
