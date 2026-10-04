ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"
ARG VAULTWARDEN_VERSION="1.37.3"

# ---------------------------------------------------------------------------
# Stage 1 — Pull the official Vaultwarden image to copy binaries & web vault
# ---------------------------------------------------------------------------
FROM vaultwarden/server:${VAULTWARDEN_VERSION} AS upstream

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="Vaultwarden"
LABEL io.hass.description="Self-hosted Bitwarden-compatible password manager"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        nginx \
        jq \
        curl \
        openssl \
        ca-certificates \
        libgcc

COPY --from=upstream /vaultwarden /usr/local/bin/vaultwarden
COPY --from=upstream /web-vault /opt/vaultwarden/web-vault

RUN mkdir -p /data/vaultwarden /opt/vaultwarden \
    && chmod +x /usr/local/bin/vaultwarden

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://127.0.0.1:8080/alive >/dev/null || exit 1

CMD [ "/run.sh" ]
