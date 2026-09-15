# Estágio 1: Build da aplicação React
FROM node:20-alpine AS build

WORKDIR /app

# Copia dependências e instala
COPY package*.json ./
RUN npm ci

# Copia todo o código da pasta frontend e gera o build
COPY . .
RUN npm run build

# Estágio 2: Servidor de Produção (Nginx)
FROM nginx:alpine

# Altera a porta interna do Nginx para 5000
RUN sed -i 's/listen       80;/listen       5000;/g' /etc/nginx/conf.d/default.conf

# Configura o Nginx para redirecionar todas as rotas para o index.html do React
RUN sed -i '/location \/ {/a \        try_files $uri $uri/ /index.html;' /etc/nginx/conf.d/default.conf

# Copia os arquivos gerados pelo Vite no Estágio 1
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 5000

CMD ["nginx", "-g", "daemon off;"]