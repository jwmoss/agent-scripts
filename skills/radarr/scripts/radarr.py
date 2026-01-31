#!/usr/bin/env python3
"""Minimal Radarr API wrapper. Requires RADARR_URL and RADARR_API_KEY env vars."""
# /// script
# dependencies = ["httpx"]
# ///

import os
import sys
import json
import httpx

BASE_URL = os.environ.get("RADARR_URL", "").rstrip("/")
API_KEY = os.environ.get("RADARR_API_KEY", "")

def api(endpoint: str, params: dict = None) -> dict:
    """Make authenticated GET request to Radarr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set RADARR_URL and RADARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v3/{endpoint.lstrip('/')}"
    resp = httpx.get(url, params=params, headers={"X-Api-Key": API_KEY}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def list_movies():
    """List all movies in library."""
    movies = api("movie")
    for m in sorted(movies, key=lambda x: x["title"]):
        year = m.get("year", "?")
        status = "Downloaded" if m.get("hasFile") else "Missing"
        print(f"{m['title']} ({year}) - {status}")

def search_movies(term: str):
    """Search for movies by name."""
    results = api("movie/lookup", {"term": term})
    for m in results[:10]:
        year = m.get("year", "?")
        tmdb = m.get("tmdbId", "N/A")
        print(f"{m['title']} ({year}) - TMDB: {tmdb}")

def get_movie(movie_id: int):
    """Get details for a specific movie."""
    m = api(f"movie/{movie_id}")
    print(json.dumps(m, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: radarr.py <command> [args]")
        print("Commands: list, search <term>, get <id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        list_movies()
    elif cmd == "search" and len(sys.argv) > 2:
        search_movies(" ".join(sys.argv[2:]))
    elif cmd == "get" and len(sys.argv) > 2:
        get_movie(int(sys.argv[2]))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
