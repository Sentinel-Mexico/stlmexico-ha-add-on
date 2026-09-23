ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"
ARG AFFINE_VERSION="0.27.4"

# ---------------------------------------------------------------------------
# Stage 1 — Pull the official AFFiNE image to copy the built app
# ---------------------------------------------------------------------------
FROM ghcr.io/toeverything/affine:${AFFINE_VERSION} AS upstream

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="AFFiNE"
LABEL io.hass.description="Self-hosted knowledge base — docs, whiteboards, and databases"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        nginx \
        jq \
        curl \
        openssl \
        ca-certificates \
        nodejs \
        npm \
        postgresql16 \
        postgresql16-client \
        postgresql16-contrib \
        redis \
        libgcc \
        libstdc++ \
        gcompat

RUN mkdir -p /data/affine/pgdata \
             /data/affine/storage \
             /data/affine/config \
             /run/postgresql \
             /run/redis \
             /opt/affine

COPY --from=upstream /app /opt/affine

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -sf http://127.0.0.1:3010 >/dev/null || exit 1

CMD [ "/run.sh" ]
