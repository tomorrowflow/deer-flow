# Accept NODE_ENV as a build argument with a default value of development
ARG NODE_ENV=development

##### DEPENDENCIES

FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat openssl
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml\* ./

RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm i --frozen-lockfile; \
    else echo "Lockfile not found." && exit 1; \
    fi

##### BUILDER FOR PRODUCTION

FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ARG NODE_ENV
ENV NODE_ENV=${NODE_ENV}
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

# Build the application if in production mode
RUN if [ -f yarn.lock ]; then SKIP_ENV_VALIDATION=1 yarn build; \
    elif [ -f package-lock.json ]; then SKIP_ENV_VALIDATION=1 npm run build; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && SKIP_ENV_VALIDATION=1 pnpm run build; \
    else echo "Lockfile not found." && exit 1; \
    fi

##### RUNNER FOR PRODUCTION

FROM gcr.io/distroless/nodejs20-debian12 AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["server.js"]

##### DEVELOPMENT RUNNER

FROM node:20-alpine AS development
WORKDIR /app
ARG NODE_ENV
ENV NODE_ENV=${NODE_ENV}
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Install pnpm globally for development
RUN npm install -g pnpm

COPY --from=deps /app/node_modules ./node_modules
COPY . .

EXPOSE 3000

# Start the development server
CMD \
    if [ -f yarn.lock ]; then yarn dev; \
    elif [ -f package-lock.json ]; then npm run dev; \
    elif [ -f pnpm-lock.yaml ]; then pnpm run dev; \
    else echo "Lockfile not found." && exit 1; \
    fi
