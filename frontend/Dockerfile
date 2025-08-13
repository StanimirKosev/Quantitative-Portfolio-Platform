FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

# Build the app with API base URL baked in at build time
# Example: docker build --build-arg VITE_API_URL=http://localhost:8000 -t montecarlo-frontend ./frontend
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Serve the built app using Vite preview
# Honor PORT if provided by platform like Cloud Run (default 8080)
EXPOSE 8080
ENV PORT=8080
CMD ["sh", "-c", "npm run preview -- --host 0.0.0.0 --port ${PORT:-8080}"]

