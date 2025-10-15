import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';
  const isAnalyze = mode === 'analyze';

  return {
    plugins: [
      react(),
      // Bundle analyzer plugin
      isAnalyze && visualizer({
        filename: 'dist/bundle-analysis.html',
        open: true,
        gzipSize: true,
        brotliSize: true,
        template: 'treemap' // or 'sunburst', 'treemap', 'network'
      })
    ].filter(Boolean),

    // Build configuration
    build: {
      // Enable source maps for debugging
      sourcemap: !isProduction,
      
      // Optimize chunk splitting
      rollupOptions: {
        output: {
          // Enhanced manual chunk splitting for optimal bundle sizes
          manualChunks: (id) => {
            // Core React libraries
            if (id.includes('react') && !id.includes('react-router')) {
              return 'react-core';
            }
            
            // React Router
            if (id.includes('react-router')) {
              return 'react-router';
            }
            
            // React Query
            if (id.includes('@tanstack/react-query')) {
              return 'react-query';
            }
            
            // UI Libraries
            if (id.includes('react-hot-toast') || id.includes('framer-motion')) {
              return 'ui-libs';
            }
            
            // HTTP and WebSocket
            if (id.includes('axios') || id.includes('socket.io')) {
              return 'network';
            }
            
            // Chart libraries
            if (id.includes('chart.js') || id.includes('react-chartjs-2')) {
              return 'charts';
            }
            
            // Utility libraries
            if (id.includes('date-fns') || id.includes('js-cookie') || id.includes('dompurify')) {
              return 'utils';
            }
            
            // Syntax highlighting
            if (id.includes('react-syntax-highlighter')) {
              return 'syntax';
            }
            
            // Sentry
            if (id.includes('@sentry')) {
              return 'monitoring';
            }
            
            // Web Vitals
            if (id.includes('web-vitals')) {
              return 'performance';
            }
            
            // Feature-based chunks
            if (id.includes('/src/pages/Tickets') || id.includes('/src/components/Ticket')) {
              return 'tickets';
            }
            
            if (id.includes('/src/pages/KnowledgeBase') || id.includes('/src/components/KnowledgeBase')) {
              return 'knowledge-base';
            }
            
            if (id.includes('/src/pages/Dashboard') || id.includes('/src/components/Dashboard')) {
              return 'dashboard';
            }
            
            if (id.includes('/src/pages/Profile') || id.includes('/src/components/Profile')) {
              return 'profile';
            }
            
            if (id.includes('/src/pages/Performance') || id.includes('/src/components/Performance')) {
              return 'performance';
            }
            
            // Context providers
            if (id.includes('/src/contexts/')) {
              return 'contexts';
            }
            
            // Utilities and hooks
            if (id.includes('/src/utils/') || id.includes('/src/hooks/')) {
              return 'shared';
            }
            
            // Large node_modules
            if (id.includes('node_modules')) {
              // Group by package name for better caching
              const packageName = id.split('node_modules/')[1]?.split('/')[0];
              if (packageName) {
                return `vendor-${packageName}`;
              }
            }
          },
          
          // Optimize chunk file names
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId
              ? chunkInfo.facadeModuleId.split('/').pop().replace('.jsx', '').replace('.js', '')
              : 'chunk';
            return `js/${facadeModuleId}-[hash].js`;
          },
          
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const ext = assetInfo.name.split('.').pop();
            if (ext === 'css') {
              return 'css/[name]-[hash].[ext]';
            }
            return 'assets/[name]-[hash].[ext]';
          }
        },
        
        // Tree shaking configuration
        treeshake: {
          moduleSideEffects: false,
          propertyReadSideEffects: false,
          tryCatchDeoptimization: false
        }
      },
      
      // Chunk size warnings
      chunkSizeWarningLimit: 500, // 500KB for better performance
      
      // Target modern browsers for better optimization
      target: 'es2020',
      
      // CSS code splitting
      cssCodeSplit: true,
      
      // Minification
      minify: isProduction ? 'terser' : false,
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug']
        },
        mangle: {
          safari10: true
        }
      } : undefined
    },

    // Development server configuration
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },

    // Preview server configuration
    preview: {
      port: 4173,
      host: true
    },

    // Path resolution
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@pages': resolve(__dirname, 'src/pages'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@contexts': resolve(__dirname, 'src/contexts'),
        '@hooks': resolve(__dirname, 'src/hooks')
      }
    },

    // CSS configuration
    css: {
      devSourcemap: !isProduction,
      postcss: {
        plugins: [
          require('autoprefixer'),
          require('tailwindcss')
        ]
      }
    },

    // Environment variables
    define: {
      __BUNDLE_ANALYZER__: isAnalyze,
      __DEV__: !isProduction
    },

    // Optimize dependencies
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@tanstack/react-query',
        'axios',
        'socket.io-client'
      ],
      exclude: ['@vite/client', '@vite/env']
    },

    // Performance optimizations
    esbuild: {
      target: 'es2020',
      format: 'esm',
      treeShaking: true,
      minifyIdentifiers: isProduction,
      minifySyntax: isProduction,
      minifyWhitespace: isProduction
    },
    
  };
});
