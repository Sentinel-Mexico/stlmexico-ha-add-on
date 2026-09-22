# Changelog

## 1.0.7 — 2026-09-22

### Fixed

- Fixed Docker build failure introduced in 1.0.6: the `npm` package was removed
  from the runtime image but is still required during the build to rebuild
  the better-sqlite3 native module. It is now installed as a temporary build
  dependency and removed after the rebuild completes.

## 1.0.6 — 2026-09-22

### Fixed

- Removed non-functional MariaDB/MySQL database option. The upstream FreeLLMApi
  server only supports SQLite; the MariaDB settings added in 1.0.5 set an
  environment variable the server never reads, so they had no effect. SQLite
  remains the only database engine and requires no configuration.
- Fixed slow startup on low-power devices (Raspberry Pi, small VMs):
  - Docker healthcheck start period increased from 15 s to 90 s so the add-on
    is not marked unhealthy while Node.js is still loading modules.
  - Healthcheck timeout raised from 5 s to 10 s for constrained hardware.
  - V8 heap capped at 256 MB to prevent memory pressure on small hosts.
  - Removed `npm` from the runtime image (only `nodejs` is needed), reducing
    image size and memory footprint.
  - Database path now uses the correct `FREEAPI_DB_PATH` environment variable
    that the server actually reads.

## 1.0.5 — 2026-09-18

### Fixed

- Fixed blank screen when opening the dashboard through Home Assistant Ingress.
  Asset paths are now relative and routing uses hash-based navigation so the
  interface loads correctly behind the Ingress sub-path proxy.

## 1.0.4 — 2026-09-18

### Changed

- Replaced icons with pixel-perfect renders of the official FreeLLMApi SVG logo
  (white circle + green dot on dark rounded square).

## 1.0.3 — 2026-09-18

### Fixed

- Fixed startup crash caused by better-sqlite3 native module incompatibility.
  The module is now rebuilt against Alpine musl libc during the Docker build.

## 1.0.2 — 2026-09-18

### Changed

- Replaced placeholder icons with the official FreeLLMApi logo.

## 1.0.1 — 2026-09-18

### Changed

- Default API port changed from 39101 to avoid conflicts with other services.
- Healthcheck now uses the configured port instead of a hardcoded value.

## 1.0.0 — 2026-09-18

### Added

- Initial release: port of FreeLLMApi as a Home Assistant add-on.
- Based on FreeLLMApi (https://github.com/tashfeenahmed/freellmapi).
- OpenAI-compatible `/v1` endpoint exposed on port 39101.
- Built-in dashboard accessible via Home Assistant Ingress.
- SQLite database with persistent encrypted key storage (AES-256-GCM).
- CLI tools included for coding agent configuration.
- Ready for integration with Hermes, OpenClaw, and any OpenAI-compatible client.
- Multi-architecture support: amd64 and aarch64.
- Maintained by Sentinel Mexico.
