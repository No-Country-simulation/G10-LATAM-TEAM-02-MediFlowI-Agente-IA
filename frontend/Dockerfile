FROM node:20-alpine

WORKDIR /app

# Instalar dependencias cuando el desarrollador inicialice package.json
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 8501

# Servidor de desarrollo Vite en el puerto 8501
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8501"]
