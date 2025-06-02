// vite.config.ts
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: path.resolve(__dirname, 'edamorph/frontend/src/ts/main.ts'), // ✅ tell Vite to use TS entry
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
    outDir: 'edamorph/frontend/assets/dist',
    emptyOutDir: true,
  },
})