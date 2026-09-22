# FreeLLMApi for Home Assistant

> Community port of [FreeLLMApi](https://github.com/tashfeenahmed/freellmapi)
> for Home Assistant. Maintained by [Sentinel Mexico](https://github.com/Sentinel-Mexico).

## What it does

FreeLLMApi aggregates free tiers from 34+ AI providers (Google, Groq, Mistral,
Cohere, NVIDIA, and more) behind a single OpenAI-compatible `/v1` endpoint.
It provides smart routing, automatic failover when a provider is rate-limited,
encrypted key storage, and per-key usage tracking so you stay under every
free-tier cap.

## Integration with Hermes, OpenClaw, and other AI services

Once the add-on is running, point any OpenAI-compatible client at:

```
http://<YOUR_HA_IP>:39101/v1
```

Or from another add-on on the same Home Assistant host:

```
http://homeassistant.local:39101/v1
```

### Hermes

In the Hermes add-on or integration configuration, set:

- **LLM Base URL**: `http://homeassistant.local:39101/v1`
- **API Key**: the unified API key from your FreeLLMApi dashboard

### OpenClaw

In the OpenClaw bridge configuration:

- **LLM_BASE_URL**: `http://homeassistant.local:39101/v1`
- **LLM_API_KEY**: the unified API key from your FreeLLMApi dashboard

### Any OpenAI SDK client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://<YOUR_HA_IP>:39101/v1",
    api_key="freellmapi-..."  # from the dashboard
)

response = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Database

### SQLite (default — currently the only active engine)

FreeLLMApi uses **SQLite** for all data storage. The database is stored
automatically in the add-on's persistent storage — no configuration needed.

### MariaDB / MySQL (pre-configured for future support)

The add-on configuration includes MariaDB/MySQL connection settings, pre-filled
with defaults that match the **MariaDB** add-on for Home Assistant:

- **database_host**: `core-mariadb` (the HA MariaDB add-on)
- **database_port**: `3306`
- **database_name**: `freellmapi`
- **database_user**: `freellmapi`

To prepare for MySQL support:

1. Install the **MariaDB** add-on from the Home Assistant Add-on Store.
2. In the MariaDB add-on configuration, add a database and user:
   ```yaml
   databases:
     - freellmapi
   logins:
     - username: freellmapi
       password: YOUR_SECURE_PASSWORD
   rights:
     - username: freellmapi
       database: freellmapi
   ```
3. Start (or restart) the MariaDB add-on.
4. In this FreeLLMApi add-on's configuration, set:
   - **database_type**: `mysql` or `mariadb`
   - **database_password**: the password you chose in step 2
5. Restart FreeLLMApi.

> **Note:** The upstream FreeLLMApi server currently uses SQLite as its storage
> engine. The MySQL/MariaDB configuration is saved and the connection string is
> exported, but the server will continue using SQLite until the upstream project
> adds MySQL support. No data will be lost — your SQLite database remains
> active. When MySQL support is added upstream, the add-on will automatically
> switch to your configured MariaDB instance.

### Encryption key

Your provider API keys are encrypted at rest with AES-256-GCM. The add-on
auto-generates an encryption key on first start and persists it. You only need
to set this manually if you are migrating from an existing FreeLLMApi instance.

### API port

The default port is `39101`. Change it only if another service already uses
that port on your Home Assistant host.

## CLI tools

Open the add-on's terminal tab in Home Assistant to access the FreeLLMApi CLI:

```bash
freellmapi list              # Show supported coding agent tools
freellmapi setup-claude      # Configure Claude Code
freellmapi setup-cursor      # Configure Cursor
freellmapi setup-generic     # Configure any OpenAI-compatible client
```

## Endpoints

| Path | Description |
|------|-------------|
| `/v1/chat/completions` | Chat completions (streaming supported) |
| `/v1/completions` | Text completions |
| `/v1/embeddings` | Text embeddings |
| `/v1/images/generations` | Image generation |
| `/v1/audio/transcriptions` | Audio transcription |
| `/v1/models` | List available models |

## Support

- [This add-on's repository](https://github.com/Sentinel-Mexico/freellmapi-ha-add-on)
- [Original FreeLLMApi project](https://github.com/tashfeenahmed/freellmapi)
