#!/usr/bin/env python3
"""Minimal Sonarr API wrapper. Requires SONARR_URL and SONARR_API_KEY env vars."""
# /// script
# dependencies = ["httpx"]
# ///

import os
import sys
import json
import httpx

BASE_URL = os.environ.get("SONARR_URL", "").rstrip("/")
API_KEY = os.environ.get("SONARR_API_KEY", "")

def api(endpoint: str, params: dict = None) -> dict:
    """Make authenticated GET request to Sonarr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set SONARR_URL and SONARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v3/{endpoint.lstrip('/')}"
    resp = httpx.get(url, params=params, headers={"X-Api-Key": API_KEY}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def list_series():
    """List all series in library."""
    series = api("series")
    for s in sorted(series, key=lambda x: x["title"]):
        status = "Ended" if s.get("ended") else "Continuing"
        eps = f"{s.get('episodeFileCount', 0)}/{s.get('episodeCount', 0)} eps"
        print(f"{s['title']} ({s.get('year', '?')}) - {status} - {eps}")

def search_series(term: str):
    """Search for series by name."""
    results = api("series/lookup", {"term": term})
    for s in results[:10]:
        print(f"{s['title']} ({s.get('year', '?')}) - TVDB: {s.get('tvdbId', 'N/A')}")

def get_series(series_id: int):
    """Get details for a specific series."""
    s = api(f"series/{series_id}")
    print(json.dumps(s, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sonarr.py <command> [args]")
        print("Commands: list, search <term>, get <id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        list_series()
    elif cmd == "search" and len(sys.argv) > 2:
        search_series(" ".join(sys.argv[2:]))
    elif cmd == "get" and len(sys.argv) > 2:
        get_series(int(sys.argv[2]))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
