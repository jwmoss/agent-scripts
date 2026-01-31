---
name: radarr
description: Interact with Radarr API to manage movies on mossflix. Use when discussing movies in the library, searching for films, or checking what's available. Triggers on questions about "what movies do I have", "mossflix movies", or Radarr-related tasks.
---

# Radarr

Query and manage movies in Radarr via the API.

## Setup

Requires environment variables:
- `RADARR_URL` - Base URL (e.g., `http://localhost:7878`)
- `RADARR_API_KEY` - API key from Radarr Settings → General

## Usage

Run the wrapper script with `uv run`:

```bash
# List all movies in library
uv run scripts/radarr.py list

# Search for a movie
uv run scripts/radarr.py search "inception"

# Get movie details by ID
uv run scripts/radarr.py get 123
```

## API Reference

See [references/api_reference.md](references/api_reference.md) for full endpoint documentation.
