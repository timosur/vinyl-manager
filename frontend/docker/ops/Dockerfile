# Install dependencies only when needed
FROM node:20-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile

# Rebuild the source code only when needed
FROM node:20-alpine AS builder

WORKDIR /app

ARG APP_ENVIRONMENT=test
ENV APP_ENVIRONMENT=${APP_ENVIRONMENT}
ENV GRAFANA_AGENT_API_KEY=${GRAFANA_AGENT_API_KEY}

COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build && npm install --production --ignore-scripts --prefer-offline

# Production image, copy all the files and run next
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]