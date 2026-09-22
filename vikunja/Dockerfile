ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"
ARG VIKUNJA_VERSION="2.5.0"

# ---------------------------------------------------------------------------
# Stage 1 — Pull the official Vikunja image to copy binaries & frontend
# ---------------------------------------------------------------------------
FROM vikunja/vikunja:${VIKUNJA_VERSION} AS upstream

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="Vikunja"
LABEL io.hass.description="Self-hosted task and project management"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        nginx \
        jq \
        curl \
        ca-certificates \
        libgcc \
        openssl

RUN mkdir -p /app/vikunja /data/vikunja/files /db

COPY --from=upstream /app/vikunja/vikunja /app/vikunja/vikunja

RUN chmod +x /app/vikunja/vikunja

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf
COPY ha-ingress-fix.js /etc/nginx/ha-ingress-fix.js

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://127.0.0.1:3456/api/v1/info >/dev/null || exit 1

CMD [ "/run.sh" ]
