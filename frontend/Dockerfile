# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with specific flags for faster installation
RUN npm install --legacy-peer-deps --prefer-offline --no-audit

# Copy the rest of the application
COPY . .

# Development stage
FROM node:18-alpine

WORKDIR /app

# Copy node_modules and package files from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 3000

# Start the application in development mode
CMD ["npm", "run", "dev"] 