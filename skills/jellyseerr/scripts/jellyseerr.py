#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Jellyseerr API client for searching and requesting media."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def get_config():
    """Get Jellyseerr URL and API key from environment."""
    url = os.environ.get("JELLYSEERR_URL")
    api_key = os.environ.get("JELLYSEERR_API_KEY")

    if not url:
        print("Error: JELLYSEERR_URL environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not api_key:
        print("Error: JELLYSEERR_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    return url.rstrip("/"), api_key


def api_request(method: str, endpoint: str, data: dict | None = None) -> dict:
    """Make an API request to Jellyseerr."""
    url, api_key = get_config()
    full_url = f"{url}/api/v1{endpoint}"

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(full_url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def search(query: str) -> None:
    """Search for movies and TV shows."""
    results = api_request("GET", f"/search?query={urllib.parse.quote(query)}")

    if not results.get("results"):
        print("No results found.")
        return

    print(f"Found {results['totalResults']} results:\n")

    for item in results["results"][:10]:
        media_type = item.get("mediaType", "unknown")
        tmdb_id = item.get("id")

        if media_type == "movie":
            title = item.get("title", "Unknown")
            date = item.get("releaseDate", "")[:4]
        elif media_type == "tv":
            title = item.get("name", "Unknown")
            date = item.get("firstAirDate", "")[:4]
        else:
            continue

        overview = item.get("overview", "")[:100]
        if len(item.get("overview", "")) > 100:
            overview += "..."

        print(f"[{media_type.upper()}] {title} ({date})")
        print(f"  TMDB ID: {tmdb_id}")
        print(f"  {overview}\n")


def request_media(media_type: str, tmdb_id: int, seasons: list[int] | None = None) -> None:
    """Request a movie or TV show."""
    data = {
        "mediaType": media_type,
        "mediaId": tmdb_id,
    }

    if media_type == "tv":
        data["seasons"] = seasons if seasons else "all"

    result = api_request("POST", "/request", data)

    status_map = {1: "Pending", 2: "Approved", 3: "Declined"}
    status = status_map.get(result.get("status"), "Unknown")

    print(f"Request created successfully!")
    print(f"  Request ID: {result.get('id')}")
    print(f"  Status: {status}")


def main():
    import urllib.parse

    parser = argparse.ArgumentParser(description="Jellyseerr media request tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for media")
    search_parser.add_argument("query", help="Search query")

    # Request command
    request_parser = subparsers.add_parser("request", help="Request media")
    request_parser.add_argument("type", choices=["movie", "tv"], help="Media type")
    request_parser.add_argument("tmdb_id", type=int, help="TMDB ID")
    request_parser.add_argument("--seasons", type=int, nargs="+", help="Specific seasons (TV only)")

    args = parser.parse_args()

    if args.command == "search":
        search(args.query)
    elif args.command == "request":
        request_media(args.type, args.tmdb_id, args.seasons)


if __name__ == "__main__":
    main()
