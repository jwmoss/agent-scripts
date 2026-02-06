---
name: tracearr
description: Query Tracearr API for media server monitoring - active streams, user activity, account sharing violations, and playback history. Use when discussing streaming activity, who's watching, account sharing detection, or trust scores. Triggers on "tracearr", "who is streaming", "active streams", "violations", "trust score", "stream history".
---

# Tracearr

Monitor Plex/Jellyfin/Emby servers via Tracearr's public API - track active streams, detect account sharing, and analyze user behavior.

## Setup

Requires environment variables:
- `TRACEARR_URL` - Base URL (e.g., `http://192.168.1.254:3002`)
- `TRACEARR_API_KEY` - API key from Tracearr Settings → General (format: `trr_pub_...`)

## Usage

Run the wrapper script with `uv run`:

```bash
# Server health and connectivity
uv run scripts/tracearr.py health

# Dashboard statistics
uv run scripts/tracearr.py stats

# Active streams (detailed)
uv run scripts/tracearr.py streams

# Active streams (summary only)
uv run scripts/tracearr.py streams --summary

# List users with activity
uv run scripts/tracearr.py users

# List violations
uv run scripts/tracearr.py violations
uv run scripts/tracearr.py violations --severity high --acknowledged false

# Session history
uv run scripts/tracearr.py history
uv run scripts/tracearr.py history --media-type movie --start-date 2026-01-01
```

## API Reference

See [references/api.md](references/api.md) for full endpoint documentation.
