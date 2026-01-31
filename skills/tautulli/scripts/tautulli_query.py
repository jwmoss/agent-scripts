#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "tabulate"]
# ///
"""
Tautulli API query tool for media server analytics.

Environment variables required:
    TAUTULLI_URL: Base URL (e.g., http://localhost:8181)
    TAUTULLI_API_KEY: API key from Tautulli settings

Usage:
    uv run tautulli_query.py <command> [options]

Commands:
    history         View playback history
    users           List users and stats
    libraries       List libraries
    watching        Current activity
    popular         Most watched content
    stats           Server statistics
    user-history    History for specific user
    search          Search history
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

import requests
from tabulate import tabulate


def get_config() -> tuple[str, str]:
    """Get Tautulli URL and API key from environment."""
    url = os.environ.get("TAUTULLI_URL")
    api_key = os.environ.get("TAUTULLI_API_KEY")

    if not url or not api_key:
        print("Error: TAUTULLI_URL and TAUTULLI_API_KEY environment variables required", file=sys.stderr)
        sys.exit(1)

    return url.rstrip("/"), api_key


def api_call(cmd: str, **params) -> dict[str, Any]:
    """Make Tautulli API call."""
    url, api_key = get_config()

    params = {k: v for k, v in params.items() if v is not None}
    params["apikey"] = api_key
    params["cmd"] = cmd

    response = requests.get(f"{url}/api/v2", params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    if data.get("response", {}).get("result") != "success":
        msg = data.get("response", {}).get("message", "Unknown error")
        print(f"API Error: {msg}", file=sys.stderr)
        sys.exit(1)

    return data.get("response", {}).get("data", {})


def format_duration(seconds: int | str | None) -> str:
    """Format seconds as human-readable duration."""
    if not seconds:
        return "0m"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_date(timestamp: int | str | None) -> str:
    """Format Unix timestamp as date string."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")


def cmd_history(args):
    """Get playback history."""
    params = {"length": args.limit}

    if args.days:
        start = datetime.now() - timedelta(days=args.days)
        params["start_date"] = start.strftime("%Y-%m-%d")

    if args.user:
        params["user"] = args.user

    if args.media_type:
        params["media_type"] = args.media_type

    data = api_call("get_history", **params)
    records = data.get("data", [])

    if args.json:
        print(json.dumps(records, indent=2))
        return

    if not records:
        print("No history found")
        return

    table = []
    for r in records:
        table.append([
            format_date(r.get("started")),
            r.get("user", "Unknown")[:15],
            r.get("full_title", "Unknown")[:40],
            r.get("media_type", "?"),
            format_duration(r.get("duration")),
            r.get("transcode_decision", "direct")[:10],
        ])

    headers = ["Date", "User", "Title", "Type", "Duration", "Transcode"]
    print(tabulate(table, headers=headers, tablefmt="simple"))
    print(f"\nTotal: {len(records)} plays")


def cmd_users(args):
    """List users with stats."""
    data = api_call("get_users")

    if args.json:
        print(json.dumps(data, indent=2))
        return

    if not data:
        print("No users found")
        return

    table = []
    for u in data:
        if u.get("username") == "Local":
            continue
        table.append([
            u.get("username", "Unknown"),
            u.get("friendly_name", ""),
            u.get("email", ""),
            format_date(u.get("last_seen")),
        ])

    headers = ["Username", "Friendly Name", "Email", "Last Seen"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def cmd_libraries(args):
    """List libraries."""
    data = api_call("get_libraries")

    if args.json:
        print(json.dumps(data, indent=2))
        return

    if not data:
        print("No libraries found")
        return

    table = []
    for lib in data:
        table.append([
            lib.get("section_id"),
            lib.get("section_name"),
            lib.get("section_type"),
            lib.get("count", 0),
            lib.get("parent_count", 0),
            lib.get("child_count", 0),
        ])

    headers = ["ID", "Name", "Type", "Items", "Shows/Artists", "Episodes/Tracks"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def cmd_watching(args):
    """Get current activity."""
    data = api_call("get_activity")
    sessions = data.get("sessions", [])

    if args.json:
        print(json.dumps(data, indent=2))
        return

    stream_count = data.get("stream_count", 0)
    print(f"Active streams: {stream_count}")

    if not sessions:
        print("No active streams")
        return

    print()
    table = []
    for s in sessions:
        progress = int(float(s.get("progress_percent", 0)))
        table.append([
            s.get("user", "Unknown"),
            s.get("full_title", "Unknown")[:40],
            s.get("state", "?"),
            f"{progress}%",
            s.get("quality_profile", "?"),
            s.get("transcode_decision", "direct"),
            s.get("platform", "?"),
        ])

    headers = ["User", "Title", "State", "Progress", "Quality", "Transcode", "Platform"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def cmd_popular(args):
    """Get most watched content."""
    stat_type = {
        "movies": "popular_movies",
        "shows": "popular_tv",
        "music": "popular_music",
    }.get(args.type, "popular_movies")

    params = {"stat_id": stat_type, "stats_count": args.limit}

    if args.days:
        params["time_range"] = args.days

    data = api_call("get_home_stats", **params)

    # Find the matching stat
    stats = None
    for item in data:
        if item.get("stat_id") == stat_type:
            stats = item.get("rows", [])
            break

    if args.json:
        print(json.dumps(stats, indent=2))
        return

    if not stats:
        print(f"No {args.type} stats found")
        return

    table = []
    for i, s in enumerate(stats, 1):
        table.append([
            i,
            s.get("title", "Unknown")[:50],
            s.get("users_watched", 0),
            s.get("total_plays", 0),
            format_duration(s.get("total_duration")),
        ])

    headers = ["#", "Title", "Users", "Plays", "Total Time"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def cmd_stats(args):
    """Get server statistics."""
    days = args.days or 30

    # Get multiple stat types
    stat_ids = ["top_users", "top_platforms", "most_concurrent"]

    data = api_call("get_home_stats", time_range=days, stats_count=10)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    print(f"Statistics for last {days} days\n")

    for stat in data:
        stat_id = stat.get("stat_id", "")
        rows = stat.get("rows", [])

        if stat_id == "top_users" and rows:
            print("TOP USERS")
            table = [[r.get("user", "?"), r.get("total_plays", 0), format_duration(r.get("total_duration"))] for r in rows[:5]]
            print(tabulate(table, headers=["User", "Plays", "Watch Time"], tablefmt="simple"))
            print()

        elif stat_id == "top_platforms" and rows:
            print("TOP PLATFORMS")
            table = [[r.get("platform", "?"), r.get("total_plays", 0)] for r in rows[:5]]
            print(tabulate(table, headers=["Platform", "Plays"], tablefmt="simple"))
            print()

        elif stat_id == "most_concurrent" and rows:
            print("PEAK CONCURRENT STREAMS")
            table = [[format_date(r.get("started")), r.get("count", 0)] for r in rows[:3]]
            print(tabulate(table, headers=["Time", "Streams"], tablefmt="simple"))
            print()


def cmd_user_history(args):
    """Get detailed history for a specific user."""
    data = api_call("get_history", user=args.username, length=args.limit)
    records = data.get("data", [])

    if args.json:
        print(json.dumps(records, indent=2))
        return

    if not records:
        print(f"No history found for user: {args.username}")
        return

    # Group by media type
    by_type = {}
    total_duration = 0
    for r in records:
        mtype = r.get("media_type", "unknown")
        by_type.setdefault(mtype, []).append(r)
        total_duration += int(r.get("duration") or 0)

    print(f"History for: {args.username}")
    print(f"Total plays: {len(records)}")
    print(f"Total watch time: {format_duration(total_duration)}")
    print()

    for mtype, items in by_type.items():
        print(f"{mtype.upper()}: {len(items)} plays")

    print("\nRecent activity:")
    table = []
    for r in records[:20]:
        table.append([
            format_date(r.get("started")),
            r.get("full_title", "Unknown")[:45],
            format_duration(r.get("duration")),
        ])

    headers = ["Date", "Title", "Duration"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def cmd_search(args):
    """Search history."""
    data = api_call("get_history", search=args.query, length=args.limit)
    records = data.get("data", [])

    if args.json:
        print(json.dumps(records, indent=2))
        return

    if not records:
        print(f"No results for: {args.query}")
        return

    print(f"Search results for: {args.query}\n")

    table = []
    for r in records:
        table.append([
            format_date(r.get("started")),
            r.get("user", "?")[:12],
            r.get("full_title", "Unknown")[:40],
            format_duration(r.get("duration")),
        ])

    headers = ["Date", "User", "Title", "Duration"]
    print(tabulate(table, headers=headers, tablefmt="simple"))


def main():
    parser = argparse.ArgumentParser(description="Tautulli analytics tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common(p):
        p.add_argument("--json", action="store_true", help="Output as JSON")
        p.add_argument("--limit", type=int, default=25, help="Number of results")

    # history
    p = subparsers.add_parser("history", help="View playback history")
    add_common(p)
    p.add_argument("--days", type=int, help="Limit to last N days")
    p.add_argument("--user", help="Filter by username")
    p.add_argument("--media-type", choices=["movie", "episode", "track"], help="Filter by type")
    p.set_defaults(func=cmd_history)

    # users
    p = subparsers.add_parser("users", help="List users")
    add_common(p)
    p.set_defaults(func=cmd_users)

    # libraries
    p = subparsers.add_parser("libraries", help="List libraries")
    add_common(p)
    p.set_defaults(func=cmd_libraries)

    # watching
    p = subparsers.add_parser("watching", help="Current activity")
    add_common(p)
    p.set_defaults(func=cmd_watching)

    # popular
    p = subparsers.add_parser("popular", help="Most watched content")
    add_common(p)
    p.add_argument("--type", choices=["movies", "shows", "music"], default="movies")
    p.add_argument("--days", type=int, default=30, help="Time range in days")
    p.set_defaults(func=cmd_popular)

    # stats
    p = subparsers.add_parser("stats", help="Server statistics")
    add_common(p)
    p.add_argument("--days", type=int, default=30, help="Time range in days")
    p.set_defaults(func=cmd_stats)

    # user-history
    p = subparsers.add_parser("user-history", help="History for specific user")
    add_common(p)
    p.add_argument("username", help="Username to look up")
    p.set_defaults(func=cmd_user_history)

    # search
    p = subparsers.add_parser("search", help="Search history")
    add_common(p)
    p.add_argument("query", help="Search query")
    p.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
