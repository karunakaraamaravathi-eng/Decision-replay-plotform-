# ==============================================================================
# Multi-stage Dockerfile for React + Vite Frontend
# Stage 1: Build static assets
# Stage 2: Serve optimized assets with Nginx
# ==============================================================================

# --- Stage 1: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests and install dependencies
COPY package*.json ./
RUN npm ci || npm install

# Copy frontend source code
COPY . .

# Build argument for API base URL (defaults to /api/v1 for reverse proxying)
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Compile production bundle
RUN npm run build

# --- Stage 2: Production Nginx Server ---
FROM nginx:alpine AS runner

# Remove default nginx welcome site
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
