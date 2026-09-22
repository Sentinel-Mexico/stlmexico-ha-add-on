#!/usr/bin/with-contenv bashio
# ==============================================================================
# FreeLLMApi Home Assistant Add-on — startup script
# ==============================================================================
set -e

# ---------- Read add-on options via bashio -----------------------------------

API_PORT=$(bashio::config 'api_port')
LOG_LEVEL=$(bashio::config 'log_level')
ENCRYPTION_KEY=$(bashio::config 'encryption_key')

# ---------- Generate encryption key if not set --------------------------------

DATA_DIR="/data/freellmapi"
mkdir -p "${DATA_DIR}"

if [ -z "${ENCRYPTION_KEY}" ]; then
    KEY_FILE="${DATA_DIR}/.encryption_key"
    if [ -f "${KEY_FILE}" ]; then
        ENCRYPTION_KEY=$(cat "${KEY_FILE}")
        bashio::log.info "Loaded existing encryption key from persistent storage."
    else
        ENCRYPTION_KEY=$(openssl rand -hex 32)
        echo "${ENCRYPTION_KEY}" > "${KEY_FILE}"
        chmod 600 "${KEY_FILE}"
        bashio::log.info "Generated new encryption key and saved to persistent storage."
    fi
fi

# ---------- Export environment for FreeLLMApi ---------------------------------

export PORT="${API_PORT}"
export HOST="0.0.0.0"
export LOG_LEVEL="${LOG_LEVEL}"
export FREEAPI_DB_PATH="${DATA_DIR}/freellmapi.db"
export ENCRYPTION_KEY="${ENCRYPTION_KEY}"
export DATA_DIR="${DATA_DIR}"
export NODE_ENV="production"

# Reduce V8 heap on memory-constrained devices (Pi, small VMs).
# The server idles well under 128 MB; 256 MB leaves room for peak
# request bursts without letting a leak consume the whole host.
export NODE_OPTIONS="--max-old-space-size=256"

# Make the API URL available for the CLI
export FREELLMAPI_URL="http://127.0.0.1:${API_PORT}"

bashio::log.info "Using SQLite at ${FREEAPI_DB_PATH}"

# ---------- Configure nginx Ingress -------------------------------------------

INGRESS_PORT=8099
INGRESS_ENTRY=$(bashio::addon.ingress_entry)

bashio::log.info "Ingress entry: ${INGRESS_ENTRY}"
bashio::log.info "API available at: http://0.0.0.0:${API_PORT}/v1"

# Write the actual port into the nginx config
sed -i "s|%%API_PORT%%|${API_PORT}|g" /etc/nginx/http.d/ingress.conf
sed -i "s|%%INGRESS_PORT%%|${INGRESS_PORT}|g" /etc/nginx/http.d/ingress.conf

# ---------- Start nginx (background) -----------------------------------------

bashio::log.info "Starting nginx for Ingress proxy..."
nginx -g "daemon off;" &
NGINX_PID=$!

# ---------- Graceful shutdown handler -----------------------------------------

shutdown() {
    bashio::log.info "Shutting down FreeLLMApi..."
    kill "${SERVER_PID}" 2>/dev/null || true
    kill "${NGINX_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
    wait "${NGINX_PID}" 2>/dev/null || true
    bashio::log.info "Shutdown complete."
    exit 0
}

trap shutdown SIGTERM SIGINT

# ---------- Start FreeLLMApi server -------------------------------------------

SERVER_DIR="/opt/freellmapi"

bashio::log.info "Starting FreeLLMApi server on port ${API_PORT}..."
bashio::log.info "  Log level       : ${LOG_LEVEL}"
bashio::log.info "  API endpoint    : http://0.0.0.0:${API_PORT}/v1"

cd "${SERVER_DIR}"

node server/dist/index.js &

SERVER_PID=$!

bashio::log.info "FreeLLMApi is running (PID ${SERVER_PID})."
bashio::log.info ""
bashio::log.info "==================================================================="
bashio::log.info "  To connect from Hermes, OpenClaw, or any OpenAI client:"
bashio::log.info "    Base URL : http://<HA_IP>:${API_PORT}/v1"
bashio::log.info "    Or from another add-on on the same host:"
bashio::log.info "    Base URL : http://homeassistant.local:${API_PORT}/v1"
bashio::log.info "==================================================================="
bashio::log.info ""

# Wait for the server process — if it exits, the add-on stops
wait "${SERVER_PID}"
