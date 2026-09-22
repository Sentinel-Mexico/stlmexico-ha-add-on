<div align="center">

# Home Assistant Add-ons

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--ons-41BDF5?style=for-the-badge&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![Standard](https://img.shields.io/badge/Standard-agentskills.io-black?style=for-the-badge)](https://agentskills.io)

**Community add-ons for Home Assistant by [Sentinel Mexico](https://github.com/Sentinel-Mexico).**

</div>

---

## Available Add-ons

| Add-on | Description | Version |
|--------|-------------|---------|
| [FreeLLMApi for HA](freellmapi/) | OpenAI-compatible LLM gateway with 34+ free providers | 1.0.10 |
| [Vaultwarden for HA](vaultwarden/) | Self-hosted Bitwarden-compatible password manager | 1.0.1 |
| [Vikunja for HA](vikunja/) | Self-hosted task and project management | 1.0.15 |
| [Linkwarden for HA](linkwarden/) | Self-hosted bookmark manager and web archive | 1.0.1 |
| [AFFiNE for HA](affine/) | Self-hosted knowledge base — docs, whiteboards, and databases | 1.0.0 |
| [Syncthing for HA](syncthing/) | Continuous file synchronization between devices | 1.0.0 |
| [OpenSpeedTest for HA](openspeedtest/) | Self-hosted network speed test | 1.0.0 |
| [Netdata for HA](netdata/) | Real-time infrastructure monitoring with interactive dashboards | 1.0.0 |

---

## FreeLLMApi for HA

A port of [FreeLLMApi](https://github.com/tashfeenahmed/freellmapi) by [Tashfeen Ahmed](https://github.com/tashfeenahmed). Aggregates the free tiers from 34+ AI providers (Google, Groq, Mistral, Cohere, NVIDIA, and more) behind a single OpenAI-compatible `/v1` endpoint. Includes smart routing, automatic failover, AES-256-GCM encrypted key storage, and per-key usage tracking.

**Use it with:** Hermes, OpenClaw, or any service that speaks the OpenAI API format.

```
Home Assistant
├── FreeLLMApi for HA
│   ├── API Server (:3001/v1)   ◄── Hermes / OpenClaw / any client
│   ├── Dashboard (Ingress)     ◄── HA Web UI
│   ├── CLI Tools               ◄── Add-on Terminal
│   └── SQLite / MariaDB        ◄── Encrypted key storage
```

[Full documentation →](freellmapi/README.md)

---

## Vaultwarden for HA

A port of [Vaultwarden](https://github.com/dani-garcia/vaultwarden) by [Daniel Garcia](https://github.com/dani-garcia). Lightweight, Rust-based Bitwarden server that supports passwords, TOTP, passkeys, file attachments, Bitwarden Send, organizations, and emergency access — using under 50 MB of RAM.

**Use it with:** any official Bitwarden client (browser extension, desktop, mobile, CLI).

```
Home Assistant
├── Vaultwarden Add-on
│   ├── Vaultwarden Server (:8080)  ◄── Bitwarden clients
│   ├── Web Vault (Ingress)         ◄── HA Web UI sidebar
│   ├── Admin Panel (/admin)        ◄── Server management
│   └── SQLite DB                   ◄── Encrypted vault storage
```

[Full documentation →](vaultwarden/README.md)

---

## Vikunja for HA

A port of [Vikunja](https://vikunja.io) by the [Vikunja team](https://github.com/go-vikunja). Full-featured task management with lists, kanban boards, Gantt charts, calendar views, reminders, team collaboration, and CalDAV sync with native apps like Apple Reminders.

**Use it with:** any web browser, CalDAV-compatible apps (Apple Reminders, Thunderbird).

```
Home Assistant
├── Vikunja Add-on
│   ├── Vikunja Server (:3456)   ◄── Web browser / mobile apps
│   ├── Web Interface (Ingress)  ◄── HA Web UI sidebar
│   ├── CalDAV Endpoint          ◄── Apple Reminders / Thunderbird
│   └── SQLite DB                ◄── Task and project storage
```

[Full documentation →](vikunja/README.md)

---

## Linkwarden for HA

A port of [Linkwarden](https://linkwarden.app) by [Daniel](https://github.com/daniel31x13). A collaborative bookmark manager that automatically archives web pages as screenshots, PDFs, and readable articles. Supports collections, tags, full-text search, browser extensions, and a REST API.

**Use it with:** any web browser, browser extensions (Chrome, Firefox, Safari).

```
Home Assistant
├── Linkwarden Add-on
│   ├── Linkwarden Server (:3000)  ◄── Web browser / extensions
│   ├── Web Interface (Ingress)    ◄── HA Web UI sidebar
│   ├── PostgreSQL DB              ◄── Bookmark and user storage
│   └── Archive Storage            ◄── Screenshots, PDFs, articles
```

[Full documentation →](linkwarden/README.md)

---

## AFFiNE for HA

A port of [AFFiNE](https://affine.pro) by [TOEVERYTHING](https://github.com/toeverything). A next-gen knowledge base that combines documents, whiteboards, and databases in one app. Supports rich-text Markdown editing, infinite-canvas whiteboards, real-time collaboration, offline editing, and an AI assistant with bring-your-own-key support.

**Use it with:** any web browser, AFFiNE desktop app.

```
Home Assistant
├── AFFiNE Add-on
│   ├── AFFiNE Server (:3010)      ◄── Web browser / desktop app
│   ├── Web Interface (Ingress)    ◄── HA Web UI sidebar
│   ├── PostgreSQL DB              ◄── Document and user storage
│   ├── Redis Cache                ◄── Real-time sync and sessions
│   └── File Storage               ◄── Uploaded files and attachments
```

[Full documentation →](affine/README.md)

---

## Syncthing for HA

A port of [Syncthing](https://syncthing.net) by the [Syncthing team](https://github.com/syncthing). Continuous file synchronization that keeps your files in sync across computers, phones, and NAS devices — encrypted end-to-end, peer-to-peer, and without any cloud service.

**Use it with:** Syncthing apps on Windows, macOS, Linux, Android (or Möbius Sync on iOS).

```
Home Assistant
├── Syncthing Add-on
│   ├── Syncthing Server             ◄── Peer-to-peer sync engine
│   ├── Web GUI (:8384)              ◄── Web browser / Ingress sidebar
│   ├── Sync Protocol (:22000)       ◄── Device-to-device transfers
│   ├── Local Discovery (:21027)     ◄── LAN device detection
│   └── HA Directories               ◄── /share, /media, /backup
```

[Full documentation →](syncthing/README.md)

---

## OpenSpeedTest for HA

A port of [OpenSpeedTest](https://openspeedtest.com) by the [OpenSpeedTest team](https://github.com/openspeedtest). An HTML5-based network speed test that measures download, upload, ping, and jitter entirely in the browser. All data stays on your local network — nothing is sent to external servers.

**Use it with:** any web browser on your network (desktop, mobile, smart TV).

```
Home Assistant
├── OpenSpeedTest Add-on
│   ├── Nginx Web Server (:3000)   ◄── Any web browser on the network
│   ├── Web Interface (Ingress)    ◄── HA Web UI sidebar
│   └── HTML5 Speed Test Engine    ◄── Runs entirely in the browser
```

[Full documentation →](openspeedtest/README.md)

---

## Netdata for HA

A port of [Netdata](https://www.netdata.cloud) by the [Netdata team](https://github.com/netdata). Real-time infrastructure monitoring that collects thousands of per-second metrics — CPU, memory, disk, network, processes, and applications — with beautiful interactive dashboards, intelligent alerts, and an efficient time-series database. Everything runs locally with no cloud dependency.

**Use it with:** any web browser on your network.

```
Home Assistant
├── Netdata Add-on
│   ├── Netdata Agent              ◄── Metric collection engine
│   ├── Web Dashboard (:19999)     ◄── Interactive charts / Ingress
│   ├── Time-Series DB (dbengine)  ◄── Persistent metric storage
│   └── Plugin Collectors          ◄── CPU, memory, disk, network, etc.
```

[Full documentation →](netdata/README.md)

---

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click the three-dot menu (top-right) → **Repositories**.
3. Paste this repository URL and click **Add**:
   ```
   https://github.com/Sentinel-Mexico/ha-add-ons
   ```
4. All add-ons will appear in the store. Install whichever you need.

## Repository Structure

```
.
├── freellmapi/              # FreeLLMApi add-on
│   ├── cli/                 # CLI tools for coding agents
│   ├── client/              # React dashboard (Vite)
│   ├── server/              # Node.js API server
│   ├── shared/              # Shared modules
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── vaultwarden/             # Vaultwarden add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── vikunja/                 # Vikunja add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── linkwarden/              # Linkwarden add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── affine/                  # AFFiNE add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── syncthing/               # Syncthing add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── openspeedtest/           # OpenSpeedTest add-on
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── netdata/                 # Netdata add-on
│   ├── translations/        # Add-on translations
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Multi-stage build
│   └── run.sh               # Startup script (bashio)
├── README.md                # This file
└── repository.yaml          # Add-on repository manifest
```

## Contributing

Contributions are welcome. To contribute:

1. Fork this repository.
2. Create a branch from `main` with a descriptive name.
3. Make your changes and ensure the Docker build works correctly.
4. Open a Pull Request describing the changes.

For contributions to the upstream projects, visit [FreeLLMApi](https://github.com/tashfeenahmed/freellmapi), [Vaultwarden](https://github.com/dani-garcia/vaultwarden), [Vikunja](https://github.com/go-vikunja/vikunja), [Linkwarden](https://github.com/linkwarden/linkwarden), [AFFiNE](https://github.com/toeverything/AFFiNE), [Syncthing](https://github.com/syncthing/syncthing), [OpenSpeedTest](https://github.com/openspeedtest/Docker-Image), or [Netdata](https://github.com/netdata/netdata).

## Credits

- **FreeLLMApi** by [Tashfeen Ahmed](https://github.com/tashfeenahmed) — MIT License
- **Vaultwarden** by [Daniel Garcia](https://github.com/dani-garcia) — AGPL-3.0 License
- **Vikunja** by the [Vikunja team](https://github.com/go-vikunja) — AGPL-3.0 License
- **Linkwarden** by [Daniel](https://github.com/daniel31x13) — AGPL-3.0 License
- **AFFiNE** by [TOEVERYTHING](https://github.com/toeverything) — MIT License
- **Syncthing** by the [Syncthing team](https://github.com/syncthing) — MPL-2.0 License
- **OpenSpeedTest** by the [OpenSpeedTest team](https://github.com/openspeedtest) — MIT License
- **Netdata** by the [Netdata team](https://github.com/netdata) — GPL-3.0 License

---

<div align="center">

**Maintained by [Sentinel Mexico](https://github.com/Sentinel-Mexico)**

</div>
