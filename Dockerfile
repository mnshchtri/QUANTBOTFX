# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Build the frontend with relative API path mapping to hit the Nginx reverse proxy
RUN REACT_APP_API_URL="" npm run build

# Stage 2: Build the C++ Backend
FROM ubuntu:22.04 AS backend-builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    cmake build-essential libpq-dev wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
# Copy all backend source files
COPY backend/ ./
# Build the binary using CMake
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
RUN cmake --build build -j$(nproc)

# Stage 3: Production Runner
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    libpq5 nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the compiled backend binary
COPY --from=backend-builder /app/backend/build/quantbot_backend /app/quantbot_backend

# Copy the compiled React frontend to Nginx's serving directory
COPY --from=frontend-builder /app/frontend/build /var/www/html

# Configure Nginx as a reverse proxy for the backend and file server for the frontend
RUN echo 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /var/www/html;\n\
    index index.html;\n\
    \n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass http://127.0.0.1:8080;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Create a startup script to run both Nginx and the C++ Backend
RUN echo '#!/bin/bash\n\
nginx\n\
./quantbot_backend\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]
