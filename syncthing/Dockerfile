ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"
ARG SYNCTHING_VERSION="2.1.5"

# ---------------------------------------------------------------------------
# Stage 1 — Pull the official Syncthing image to copy the binary
# ---------------------------------------------------------------------------
FROM syncthing/syncthing:${SYNCTHING_VERSION} AS upstream

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="Syncthing"
LABEL io.hass.description="Continuous file synchronization between devices"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        nginx \
        jq \
        curl \
        openssl \
        ca-certificates

RUN mkdir -p /data/syncthing/config \
             /data/syncthing/sync

COPY --from=upstream /bin/syncthing /usr/local/bin/syncthing

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://127.0.0.1:8384/rest/noauth/health >/dev/null || exit 1

CMD [ "/run.sh" ]
