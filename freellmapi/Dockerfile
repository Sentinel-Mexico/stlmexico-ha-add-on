ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"

# ---------------------------------------------------------------------------
# Stage 1 — install deps & build (server + cli + client)
# ---------------------------------------------------------------------------
FROM node:20-bookworm-slim AS builder

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 make g++ \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY package.json package-lock.json ./
COPY shared/package.json ./shared/
COPY server/package.json ./server/
COPY client/package.json ./client/
COPY cli/package.json ./cli/

RUN npm ci

COPY shared ./shared
COPY server ./server
COPY client ./client
COPY cli ./cli

RUN npm run build
RUN npm prune --omit=dev

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="FreeLLMApi for HA"
LABEL io.hass.description="Port of FreeLLMApi for Home Assistant - 34+ free LLM providers behind one OpenAI-compatible endpoint"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        nodejs \
        nginx \
        jq \
        curl \
        openssl

RUN mkdir -p /data/freellmapi /opt/freellmapi

COPY --from=builder /build/package.json /build/package-lock.json /opt/freellmapi/
COPY --from=builder /build/node_modules /opt/freellmapi/node_modules
COPY --from=builder /build/server/node_modules /opt/freellmapi/server/node_modules
COPY --from=builder /build/shared /opt/freellmapi/shared
COPY --from=builder /build/server/package.json /opt/freellmapi/server/package.json
COPY --from=builder /build/server/dist /opt/freellmapi/server/dist
COPY --from=builder /build/client/dist /opt/freellmapi/client/dist
COPY --from=builder /build/cli/dist /opt/freellmapi/cli/dist
COPY --from=builder /build/cli/package.json /opt/freellmapi/cli/package.json

# Rebuild native modules (better-sqlite3) against Alpine musl libc
RUN apk add --no-cache --virtual .build-deps python3 make g++ \
  && cd /opt/freellmapi && npm rebuild better-sqlite3 \
  && apk del .build-deps

RUN ln -sf /opt/freellmapi/cli/dist/index.js /usr/local/bin/freellmapi 2>/dev/null || true

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -sf http://127.0.0.1:${PORT:-39101}/v1/models >/dev/null || exit 1

CMD [ "/run.sh" ]
