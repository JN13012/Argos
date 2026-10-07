# Brayford Mutual core banking platform.
#
# The application image carries the reference data and a populated test estate.
# The database is a stock Postgres sidecar with an empty volume; schema and
# fixtures load on first start, which takes about a second because the
# expensive part of the fixtures, hashing every password, is done here at build
# time instead.

FROM node:20-slim AS deps
WORKDIR /srv
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

FROM node:20-slim AS fixtures
WORKDIR /srv
COPY package.json ./
RUN npm install bcryptjs --no-audit --no-fund
COPY db/seed.js db/
RUN node db/seed.js > /srv/seed.sql && wc -l /srv/seed.sql

FROM node:20-slim
ENV NODE_ENV=production PORT=8080
WORKDIR /srv

COPY --from=deps /srv/node_modules ./node_modules
COPY src ./src
COPY views ./views
COPY public ./public
COPY db/schema.sql ./db/schema.sql
COPY --from=fixtures /srv/seed.sql ./db/seed.sql
COPY package.json ./

RUN mkdir -p /srv/uploads

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://127.0.0.1:8080/healthz',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"

CMD ["node", "src/server.js"]
