# Interfaz web de BusTrack: se compila con Node y se sirve con nginx.

# Etapa 1: compilación de React + Vite
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Etapa 2: servidor web liviano (solo archivos estáticos + proxy hacia la API)
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
