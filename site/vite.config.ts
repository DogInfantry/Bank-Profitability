import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  base: './',
  build: { target: 'es2022', chunkSizeWarningLimit: 600 },
  test: { include: ['tests/**/*.test.ts'] },
});
