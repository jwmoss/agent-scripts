---
name: tautulli
description: >
  Analyze Plex media server viewing data using Tautulli. Use for questions about:
  who watched what, viewing history, user statistics, popular content, watch time
  analysis, concurrent streams, transcode rates, platform usage, and media server
  analytics. Triggers on: "who watched", "viewing history", "watch time", "most
  watched", "Plex stats", "media server", "Tautulli", "streaming activity".
---

# Tautulli Media Server Analytics

Analyze Plex viewing data via Tautulli API.

## Setup

Required environment variables:
- `TAUTULLI_URL` - Base URL (e.g., `http://localhost:8181`)
- `TAUTULLI_API_KEY` - From Tautulli Settings > Web Interface > API Key

## Quick Commands

Use `scripts/tautulli_query.py` for common queries:

```bash
# Current activity
uv run scripts/tautulli_query.py watching

# Recent history
uv run scripts/tautulli_query.py history --days 7

# User list
uv run scripts/tautulli_query.py users

# Most watched movies (last 30 days)
uv run scripts/tautulli_query.py popular --type movies --days 30

# Most watched shows
uv run scripts/tautulli_query.py popular --type shows

# Server statistics
uv run scripts/tautulli_query.py stats --days 30

# Specific user's history
uv run scripts/tautulli_query.py user-history "username"

# Search history
uv run scripts/tautulli_query.py search "Breaking Bad"

# JSON output for further processing
uv run scripts/tautulli_query.py history --json
```

All commands support `--json` for raw data and `--limit N` for result count.

## Direct API Queries

For queries not covered by the script, call the API directly:

```bash
curl "${TAUTULLI_URL}/api/v2?apikey=${TAUTULLI_API_KEY}&cmd=get_history&length=50"
```

Or in Python:

```python
import os, requests

def tautulli_api(cmd, **params):
    params["apikey"] = os.environ["TAUTULLI_API_KEY"]
    params["cmd"] = cmd
    r = requests.get(f"{os.environ['TAUTULLI_URL']}/api/v2", params=params)
    return r.json()["response"]["data"]

# Examples
history = tautulli_api("get_history", length=100, user="john")
stats = tautulli_api("get_home_stats", time_range=30)
activity = tautulli_api("get_activity")
```

## Common Analysis Patterns

### Who watched a specific show/movie?
```bash
uv run scripts/tautulli_query.py search "Game of Thrones"
```

### What has a user been watching?
```bash
uv run scripts/tautulli_query.py user-history "username" --limit 50
```

### Peak usage times
Use `get_plays_by_hourofday` or `get_plays_by_dayofweek` API commands.

### Transcode vs direct play ratio
Use `get_plays_by_stream_type` API command.

### Library-specific stats
```python
# Watch time per library
tautulli_api("get_library_watch_time_stats", section_id=1, query_days="7,30,365")
```

## API Reference

See `references/api_reference.md` for complete endpoint documentation including:
- History and activity endpoints
- User statistics
- Library information
- Graphs and statistics
- Data export options
