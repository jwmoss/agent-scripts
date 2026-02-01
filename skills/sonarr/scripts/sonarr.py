#!/usr/bin/env python3
"""Minimal Sonarr API wrapper. Requires SONARR_URL and SONARR_API_KEY env vars."""
# /// script
# dependencies = ["httpx"]
# ///

import os
import sys
import json
from typing import Any, Optional
import httpx

BASE_URL = os.environ.get("SONARR_URL", "").rstrip("/")
API_KEY = os.environ.get("SONARR_API_KEY", "")

def api(endpoint: str, params: Optional[dict] = None) -> Any:
    """Make authenticated GET request to Sonarr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set SONARR_URL and SONARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v3/{endpoint.lstrip('/')}"
    resp = httpx.get(url, params=params, headers={"X-Api-Key": API_KEY}, timeout=60)
    resp.raise_for_status()
    return resp.json()

def api_post(endpoint: str, payload: dict) -> Any:
    """Make authenticated POST request to Sonarr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set SONARR_URL and SONARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v3/{endpoint.lstrip('/')}"
    resp = httpx.post(url, json=payload, headers={"X-Api-Key": API_KEY}, timeout=60)
    resp.raise_for_status()
    return resp.json()

def api_delete(endpoint: str) -> None:
    """Make authenticated DELETE request to Sonarr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set SONARR_URL and SONARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v3/{endpoint.lstrip('/')}"
    resp = httpx.delete(url, headers={"X-Api-Key": API_KEY}, timeout=60)
    resp.raise_for_status()

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

def get_quality_profiles():
    """Return quality profiles."""
    return api("qualityprofile")

def resolve_quality_profile_id(quality: str) -> int:
    profiles = get_quality_profiles()
    if quality.isdigit():
        qid = int(quality)
        if any(p["id"] == qid for p in profiles):
            return qid
    for p in profiles:
        if p["name"].lower() == quality.lower():
            return p["id"]
    names = ", ".join(p["name"] for p in profiles)
    sys.exit(f"Error: Unknown quality profile '{quality}'. Available: {names}")

def get_root_folders():
    """Return root folders."""
    return api("rootfolder")

def resolve_root_folder_path(root: Optional[str] = None) -> str:
    folders = get_root_folders()
    if root:
        for f in folders:
            if f["path"] == root:
                return f["path"]
        paths = ", ".join(f["path"] for f in folders)
        sys.exit(f"Error: Unknown root folder '{root}'. Available: {paths}")
    if not folders:
        sys.exit("Error: No root folders configured in Sonarr")
    return folders[0]["path"]

def find_existing_series(tvdb_id: int, title: str) -> bool:
    series = api("series")
    for s in series:
        if s.get("tvdbId") == tvdb_id:
            return True
        if s.get("title", "").lower() == title.lower():
            return True
    return False

def pick_best_match(results: list, term: str) -> dict:
    term_lower = term.lower()
    for s in results:
        if s.get("title", "").lower() == term_lower:
            return s
    top = "; ".join(f"{r.get('title', 'Unknown')} ({r.get('year', '?')})" for r in results[:5])
    sys.exit(f"Error: No exact title match for '{term}'. Top results: {top}")

def add_series(term: str, quality: str, root: Optional[str] = None, search: bool = True):
    results = api("series/lookup", {"term": term})
    if not results:
        sys.exit(f"Error: No series found for '{term}'")
    series = pick_best_match(results, term)
    tvdb_id = series.get("tvdbId")
    title = series.get("title", term)
    if not tvdb_id:
        sys.exit(f"Error: Missing TVDB ID for '{title}'")
    if find_existing_series(tvdb_id, title):
        print(f"Already in library: {title}")
        return

    quality_id = resolve_quality_profile_id(quality)
    root_path = resolve_root_folder_path(root)
    payload = {
        "title": title,
        "tvdbId": tvdb_id,
        "qualityProfileId": quality_id,
        "rootFolderPath": root_path,
        "monitored": True,
        "seasonFolder": True,
        "seriesType": series.get("seriesType", "standard"),
        "addOptions": {"searchForMissingEpisodes": bool(search)},
    }
    added = api_post("series", payload)
    print(f"Added: {added.get('title', title)}")

def delete_series(term: str):
    series_list = api("series")
    match = None
    term_lower = term.lower()
    for s in series_list:
        if s.get("title", "").lower() == term_lower:
            match = s
            break
    if not match:
        sys.exit(f"Error: Series not found in library: '{term}'")
    series_id = match.get("id")
    api_delete(f"series/{series_id}?deleteFiles=false&addImportListExclusion=false")
    print(f"Deleted: {match.get('title')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sonarr.py <command> [args]")
        print("Commands: list, search <term>, get <id>, add <term> --quality <name|id> [--root <path>] [--no-search], delete <term>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        list_series()
    elif cmd == "search" and len(sys.argv) > 2:
        search_series(" ".join(sys.argv[2:]))
    elif cmd == "get" and len(sys.argv) > 2:
        get_series(int(sys.argv[2]))
    elif cmd == "add" and len(sys.argv) > 2:
        args = sys.argv[2:]
        if "--quality" not in args:
            sys.exit("Error: add requires --quality <name|id>")
        term_parts = []
        quality = None
        root = None
        search = True
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--quality" and i + 1 < len(args):
                quality = args[i + 1]
                i += 2
                continue
            if arg == "--root" and i + 1 < len(args):
                root = args[i + 1]
                i += 2
                continue
            if arg == "--no-search":
                search = False
                i += 1
                continue
            term_parts.append(arg)
            i += 1
        term = " ".join(term_parts).strip()
        if not term:
            sys.exit("Error: add requires a series term")
        if not quality:
            sys.exit("Error: add requires --quality <name|id>")
        add_series(term, quality, root=root, search=search)
    elif cmd == "delete" and len(sys.argv) > 2:
        delete_series(" ".join(sys.argv[2:]))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
