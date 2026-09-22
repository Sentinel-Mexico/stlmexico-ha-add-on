# Changelog

## 1.0.13 — 2026-09-22

### Fixed

- Fixed MariaDB startup error (`Error 1049: Unknown database 'vikunja'`): the
  add-on now automatically creates the database if it does not exist when using
  MySQL/MariaDB. It also waits for MariaDB to be ready before starting Vikunja.
- Fixed nginx warning about duplicate MIME type `text/html`.

### Changed

- Added `mariadb-client` to the Docker image so the add-on can verify and
  auto-create the database on startup.

## 1.0.12 — 2026-09-22

### Fixed

- Fixed blank white screen: patched `history.pushState` and `replaceState`
  immediately (synchronously) instead of deferring to a microtask. The previous
  timing allowed Vue Router to call `pushState` before the patches were active,
  causing navigation to escape the ingress prefix and leaving the content area
  empty while the app shell rendered.
- Added `window.open` patching so links opened from JavaScript also go through
  the ingress proxy.

### Changed

- MariaDB default configuration now points to the HA MariaDB add-on
  (`core-mariadb:3306`) with pre-filled database name and user. Just install the
  MariaDB add-on, set the password, and switch `database_type` to `mysql`.
- Updated documentation with step-by-step MariaDB setup guide.

## 1.0.11 — 2026-09-22

### Fixed

- Fixed blank white screen caused by `<base>` tag conflicting with sub_filter
  path rewrites: removed the dynamic `<base>` tag, kept sub_filter to convert
  absolute paths to relative, and simplified the ingress fix script to only
  handle URL rewriting and Vue Router patching.
- Added dedicated nginx location blocks for static assets (`/assets/`,
  `/fonts/`, favicon, manifest) so they proxy directly without sub_filter
  processing, preventing accidental mangling of JavaScript and CSS content.
- Moved `Accept-Encoding ""` header (which disables upstream compression for
  sub_filter inspection) to only the HTML location block instead of globally,
  so static assets are served efficiently.

## 1.0.10 — 2026-09-22

### Fixed

- Completely redesigned ingress proxy: inject fix script at the start of
  `<head>` instead of the end so it runs before all other scripts; dynamically
  create `<base>` tag via JS for correct asset resolution; patch
  `history.pushState`/`replaceState` so Vue Router navigation stays within
  ingress; add separate nginx location blocks for API and DAV endpoints to
  avoid unintended body rewriting.

### Added

- MySQL / MariaDB database support: choose between SQLite (default) or an
  external MySQL/MariaDB server in the add-on configuration.

## 1.0.9 — 2026-09-22

### Fixed

- Fixed infinite loading screen: improved ingress fix script to also handle
  Request objects, full same-origin URLs, and prevent double-rewriting, so all
  API calls from Vikunja reach the backend correctly.

## 1.0.8 — 2026-09-22

### Fixed

- Fixed 502 Bad Gateway caused by inline JavaScript in the nginx config
  containing special characters that nginx interpreted as variables. Moved the
  ingress fix script to a separate static file served by nginx.

## 1.0.7 — 2026-09-22

### Changed

- Redesigned ingress proxy strategy: added absolute `<base>` tag derived from
  HA's ingress path, converted absolute asset paths to relative via sub_filter,
  and injected a script to strip the ingress prefix for Vue Router and patch
  fetch/XHR for API routing.

## 1.0.6 — 2026-09-19

### Fixed

- Fixed blank screen in HA ingress: disabled upstream gzip so nginx can rewrite
  content, injected script to patch fetch/XHR to use relative URLs, and added
  base href so HTML asset references route through ingress correctly.

## 1.0.5 — 2026-09-19

### Fixed

- Fixed blank screen when accessing Vikunja through Home Assistant ingress:
  rewrote absolute asset paths to relative so JS/CSS/API requests route through
  the ingress proxy correctly.

## 1.0.4 — 2026-09-19

### Fixed

- Disabled CORS (not needed behind Home Assistant ingress proxy) to resolve
  "service.publicurl is required" startup error.
- Set publicurl from frontend_url when provided.

## 1.0.3 — 2026-09-18

### Fixed

- Added missing openssl package required for service secret generation at
  startup.

## 1.0.2 — 2026-09-18

### Fixed

- Fixed Docker build: removed reference to non-existent frontend directory
  (frontend is embedded in the Vikunja binary).

## 1.0.1 — 2026-09-18

### Changed

- Updated icon and logo to official Vikunja branding.

## 1.0.0 — 2026-09-18

### Added

- Initial release of Vikunja as a Home Assistant add-on.
- Based on Vikunja 2.5.0.
- Web interface accessible via Home Assistant Ingress sidebar.
- Direct access on port 3456 for API and client connections.
- SQLite database with persistent storage.
- Configurable registration, email (SMTP), frontend URL, and service secret.
- CalDAV support for syncing with native calendar/reminder apps.
- Multi-architecture support: amd64 and aarch64.
