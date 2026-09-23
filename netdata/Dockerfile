ARG BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21"
ARG NETDATA_VERSION="2.11.1"

# ---------------------------------------------------------------------------
# Stage 1 — Pull the official Netdata image to copy dashboard assets
# ---------------------------------------------------------------------------
FROM netdata/netdata:v${NETDATA_VERSION} AS upstream

# ---------------------------------------------------------------------------
# Stage 2 — Home Assistant runtime
# ---------------------------------------------------------------------------
FROM ${BUILD_FROM}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.name="Netdata"
LABEL io.hass.description="Real-time infrastructure monitoring with interactive dashboards"
LABEL io.hass.version="${BUILD_VERSION}"
LABEL io.hass.type="addon"

RUN apk add --no-cache \
        netdata \
        netdata-dashboard \
        nginx \
        jq \
        curl \
        openssl \
        ca-certificates \
        procps \
        lm-sensors \
        smartmontools \
        iproute2

RUN mkdir -p /data/netdata/db \
             /data/netdata/cache \
             /var/run/netdata \
             /var/log/netdata

COPY --from=upstream /usr/share/netdata/web/ /usr/share/netdata/web/

COPY run.sh /
COPY nginx-ingress.conf /etc/nginx/http.d/ingress.conf

RUN rm -f /etc/nginx/http.d/default.conf
RUN chmod a+x /run.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -sf http://127.0.0.1:19999/api/v1/info >/dev/null || exit 1

CMD [ "/run.sh" ]
