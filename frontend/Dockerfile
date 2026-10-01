# Stage: install dependencies
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage: build the application
FROM base AS build
COPY --from=base /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage: development server (default target, used by docker-compose)
FROM base AS default
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/package.json ./
COPY --from=base /app/package-lock.json ./
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage: production server
FROM base AS runner
ENV NODE_ENV=production
COPY --from=base /app/node_modules ./node_modules
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
