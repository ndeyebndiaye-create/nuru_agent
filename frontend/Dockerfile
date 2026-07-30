FROM node:20-slim

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

ENV NEXT_PUBLIC_API_URL=http://backend:8080
ENV PORT=3000

EXPOSE 3000

RUN npm run build

CMD ["npm", "start"]
