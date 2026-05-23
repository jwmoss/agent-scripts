---
name: sonarr
description: Interact with Sonarr API to manage TV series on mossflix. Use when discussing TV shows in the library, searching for series, or checking what's available. Triggers on questions about "what shows do I have", "mossflix", or Sonarr-related tasks.
---

# Sonarr

Query and manage TV series in Sonarr via the API.

## Setup

Requires environment variables:
- `SONARR_URL` - Base URL. For mossflix: prefer `https://sonarr.mossflix.com` (public reverse proxy). LAN fallback: `http://192.168.1.235:8989` (NOT 192.168.1.254 — Sonarr lives on a separate host).
- `SONARR_API_KEY` - API key from Sonarr Settings → General. Stored in 1Password as **"Sonarr unRAID"** (Private vault, field `api`). Fetch with: `op item get "Sonarr unRAID" --format json | jq -r '.fields[] | select(.label=="api") | .value'`.

## Usage

Run the wrapper script with `uv run`:

```bash
# List all series in library
uv run scripts/sonarr.py list

# Search for a series
uv run scripts/sonarr.py search "breaking bad"

# Get series details by ID
uv run scripts/sonarr.py get 123
```

## API Reference

See [references/api.md](references/api.md) for full endpoint documentation.
