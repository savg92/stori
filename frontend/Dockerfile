# Frontend Dockerfile for Stori Expense Tracker
# Multi-stage build for production optimization

# Stage 1: Build the React application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install bun directly from official source
RUN apk add --no-cache curl unzip bash \
    && curl -fsSL https://bun.sh/install | bash \
    && ln -s /root/.bun/bin/bun /usr/local/bin/bun

# Copy dependency files
COPY package*.json bun.lock ./

# Install all dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Set environment variables for build
ENV VITE_SUPABASE_URL=https://placeholder.supabase.co
ENV VITE_SUPABASE_PUBLISHABLE_KEY=placeholder
ENV VITE_API_BASE_URL=http://localhost:8000

# Build the application
RUN bun run build

# Stage 2: Production server with nginx
FROM nginx:alpine AS production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add environment variable substitution script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx with environment variable substitution
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]