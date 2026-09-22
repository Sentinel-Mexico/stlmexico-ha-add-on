#!/usr/bin/with-contenv bashio
# ==============================================================================
# Vikunja Home Assistant Add-on — startup script
# ==============================================================================
set -e

# ---------- Read add-on options via bashio -----------------------------------

SERVICE_SECRET=$(bashio::config 'service_secret')
FRONTEND_URL=$(bashio::config 'frontend_url')
LOG_LEVEL=$(bashio::config 'log_level')
REGISTRATION_ENABLED=$(bashio::config 'registration_enabled')

DB_TYPE=$(bashio::config 'database_type')
DB_HOST=$(bashio::config 'database_host')
DB_PORT=$(bashio::config 'database_port')
DB_NAME=$(bashio::config 'database_name')
DB_USER=$(bashio::config 'database_user')
DB_PASS=$(bashio::config 'database_password')

MAILER_ENABLED=$(bashio::config 'mailer_enabled')
MAILER_HOST=$(bashio::config 'mailer_host')
MAILER_PORT=$(bashio::config 'mailer_port')
MAILER_USERNAME=$(bashio::config 'mailer_username')
MAILER_PASSWORD=$(bashio::config 'mailer_password')
MAILER_FROM_EMAIL=$(bashio::config 'mailer_from_email')

# ---------- Persistent data directory -----------------------------------------

DATA_DIR="/data/vikunja"
DB_DIR="/db"
FILES_DIR="${DATA_DIR}/files"
mkdir -p "${DATA_DIR}" "${DB_DIR}" "${FILES_DIR}"

# ---------- Generate service secret if not set --------------------------------

if [ -z "${SERVICE_SECRET}" ]; then
    SECRET_FILE="${DATA_DIR}/.service_secret"
    if [ -f "${SECRET_FILE}" ]; then
        SERVICE_SECRET=$(cat "${SECRET_FILE}")
        bashio::log.info "Loaded existing service secret from persistent storage."
    else
        SERVICE_SECRET=$(openssl rand -hex 32)
        echo "${SERVICE_SECRET}" > "${SECRET_FILE}"
        chmod 600 "${SECRET_FILE}"
        bashio::log.info "Generated new service secret and saved to persistent storage."
    fi
fi

# ---------- Export environment for Vikunja ------------------------------------

export VIKUNJA_SERVICE_ROOTPATH="/app/vikunja/"
export VIKUNJA_SERVICE_INTERFACE=":3456"
export VIKUNJA_SERVICE_SECRET="${SERVICE_SECRET}"
export VIKUNJA_LOG_LEVEL="${LOG_LEVEL}"
export VIKUNJA_SERVICE_ENABLEREGISTRATION="${REGISTRATION_ENABLED}"

export VIKUNJA_FILES_BASEPATH="${FILES_DIR}"

export VIKUNJA_CORS_ENABLE="false"

# ---------- Database configuration -------------------------------------------

if [ "${DB_TYPE}" = "mysql" ] && [ -n "${DB_HOST}" ]; then
    export VIKUNJA_DATABASE_TYPE="mysql"
    export VIKUNJA_DATABASE_HOST="${DB_HOST}"
    export VIKUNJA_DATABASE_PORT="${DB_PORT}"
    export VIKUNJA_DATABASE_DATABASE="${DB_NAME}"
    export VIKUNJA_DATABASE_USER="${DB_USER}"
    export VIKUNJA_DATABASE_PASSWORD="${DB_PASS}"
    bashio::log.info "Database: MySQL/MariaDB at ${DB_HOST}:${DB_PORT}/${DB_NAME}"

    # Auto-create the database if it does not exist yet.
    bashio::log.info "Checking if database '${DB_NAME}' exists..."
    MAX_RETRIES=15
    RETRY=0
    DB_READY=false
    while [ "${RETRY}" -lt "${MAX_RETRIES}" ]; do
        if mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" \
            -e "SELECT 1;" >/dev/null 2>&1; then
            DB_READY=true
            break
        fi
        RETRY=$((RETRY + 1))
        bashio::log.info "Waiting for MariaDB to be ready... (${RETRY}/${MAX_RETRIES})"
        sleep 2
    done

    if [ "${DB_READY}" = "true" ]; then
        if ! mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" \
            -e "USE ${DB_NAME};" >/dev/null 2>&1; then
            bashio::log.info "Database '${DB_NAME}' does not exist. Attempting to create it..."
            if mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" \
                -e "CREATE DATABASE \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1; then
                bashio::log.info "Database '${DB_NAME}' created successfully."
            else
                bashio::log.warning "Could not auto-create database '${DB_NAME}'. Please create it manually in MariaDB."
                bashio::log.warning "The user '${DB_USER}' may not have CREATE DATABASE privileges."
            fi
        else
            bashio::log.info "Database '${DB_NAME}' already exists."
        fi
    else
        bashio::log.warning "Could not connect to MariaDB at ${DB_HOST}:${DB_PORT} after ${MAX_RETRIES} attempts."
        bashio::log.warning "Vikunja will try to connect on its own — it may fail if the database does not exist."
    fi
else
    export VIKUNJA_DATABASE_TYPE="sqlite"
    export VIKUNJA_DATABASE_PATH="${DB_DIR}/vikunja.db"
    bashio::log.info "Database: SQLite at ${DB_DIR}/vikunja.db"
fi

# ---------- Frontend / public URL --------------------------------------------

if [ -n "${FRONTEND_URL}" ]; then
    export VIKUNJA_SERVICE_FRONTENDURL="${FRONTEND_URL}"
    export VIKUNJA_SERVICE_PUBLICURL="${FRONTEND_URL}"
    bashio::log.info "Frontend URL set to: ${FRONTEND_URL}"
fi

# ---------- Mailer configuration ----------------------------------------------

if [ "${MAILER_ENABLED}" = "true" ] && [ -n "${MAILER_HOST}" ]; then
    export VIKUNJA_MAILER_ENABLED="true"
    export VIKUNJA_MAILER_HOST="${MAILER_HOST}"
    export VIKUNJA_MAILER_PORT="${MAILER_PORT}"
    export VIKUNJA_MAILER_FROMEMAIL="${MAILER_FROM_EMAIL}"

    if [ -n "${MAILER_USERNAME}" ]; then
        export VIKUNJA_MAILER_USERNAME="${MAILER_USERNAME}"
        export VIKUNJA_MAILER_PASSWORD="${MAILER_PASSWORD}"
    fi

    bashio::log.info "Mailer configured via ${MAILER_HOST}:${MAILER_PORT}"
else
    export VIKUNJA_MAILER_ENABLED="false"
    bashio::log.info "Mailer not configured — email features disabled."
fi

# ---------- Configure nginx Ingress -------------------------------------------

INGRESS_PORT=8101
INGRESS_ENTRY=$(bashio::addon.ingress_entry)

bashio::log.info "Ingress entry: ${INGRESS_ENTRY}"

sed -i "s|%%VIKUNJA_PORT%%|3456|g" /etc/nginx/http.d/ingress.conf
sed -i "s|%%INGRESS_PORT%%|${INGRESS_PORT}|g" /etc/nginx/http.d/ingress.conf

# ---------- Start nginx (background) -----------------------------------------

bashio::log.info "Starting nginx for Ingress proxy..."
nginx -g "daemon off;" &
NGINX_PID=$!

# ---------- Graceful shutdown handler -----------------------------------------

shutdown() {
    bashio::log.info "Shutting down Vikunja..."
    kill "${VK_PID}" 2>/dev/null || true
    kill "${NGINX_PID}" 2>/dev/null || true
    wait "${VK_PID}" 2>/dev/null || true
    wait "${NGINX_PID}" 2>/dev/null || true
    bashio::log.info "Shutdown complete."
    exit 0
}

trap shutdown SIGTERM SIGINT

# ---------- Start Vikunja ----------------------------------------------------

bashio::log.info "Starting Vikunja..."
bashio::log.info "  Data directory   : ${DATA_DIR}"
bashio::log.info "  Log level        : ${LOG_LEVEL}"
bashio::log.info "  Registration     : ${REGISTRATION_ENABLED}"
bashio::log.info "  Web interface    : http://0.0.0.0:3456"

/app/vikunja/vikunja &
VK_PID=$!

bashio::log.info "Vikunja is running (PID ${VK_PID})."
bashio::log.info ""
bashio::log.info "==================================================================="
bashio::log.info "  Access Vikunja:"
bashio::log.info "    From HA sidebar : click Vikunja in the sidebar"
bashio::log.info "    Direct access   : http://<HA_IP>:3456"
bashio::log.info "==================================================================="
bashio::log.info ""

wait "${VK_PID}"
