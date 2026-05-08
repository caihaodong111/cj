import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return

          if (id.includes('node_modules/zrender')) return 'vendor-zrender'
          if (id.includes('node_modules/echarts')) return 'vendor-echarts'
          if (id.includes('node_modules/element-plus')) return 'vendor-element-plus'
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
            return 'vendor-vue'
          }
          if (id.includes('node_modules/axios')) return 'vendor-axios'
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
