import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'


export default defineConfig({
  plugins: [react()],
  // Sobe apenas 1 nível (sai de 'frontend' e vai para a raiz onde está o .env)
  envDir: '../',
  server:{
    host: true,
    port: 5173,
  }
})
