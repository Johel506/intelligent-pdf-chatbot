import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react-swc';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],

    define: {
      '__API_BASE_URL__': JSON.stringify(env.VITE_API_BASE_URL)
    },
  };
});
