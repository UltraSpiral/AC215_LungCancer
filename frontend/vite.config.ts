import fs from 'node:fs';
import path from 'node:path';
import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vite';

const SAMPLE_DIR = path.resolve(import.meta.dirname, 'sample-slides');

/**
 * Dev only: serve the original sample .svs files at /sample-slides/<name>.svs so the
 * HTTP adapter can upload a sample slide to the model server. Never part of a build.
 */
function sampleSlides(): Plugin {
  return {
    name: 'sample-slides',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/sample-slides', (req, res, next) => {
        const name = decodeURIComponent((req.url ?? '').split('?')[0].replace(/^\//, ''));
        if (!/^[\w.-]+\.svs$/i.test(name)) return next();
        const file = path.join(SAMPLE_DIR, name);
        fs.stat(file, (err, stat) => {
          if (err || !stat.isFile()) return next();
          res.setHeader('Content-Type', 'application/octet-stream');
          res.setHeader('Content-Length', stat.size);
          fs.createReadStream(file).pipe(res);
        });
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), sampleSlides()],
  // Pre-bundle up front so the first dev load doesn't trigger a re-optimise + reload.
  optimizeDeps: { include: ['react', 'react-dom/client', 'zustand', 'openseadragon'] },
  build: {
    rollupOptions: {
      output: {
        // Keep the large viewer library out of the app chunk so it caches separately.
        manualChunks(id) {
          if (id.includes('node_modules/openseadragon')) return 'openseadragon';
          if (id.includes('node_modules/react') || id.includes('node_modules/scheduler')) return 'react';
        },
      },
    },
  },
});
