#!/usr/bin/env python3
"""Minimal Tracearr API wrapper. Requires TRACEARR_URL and TRACEARR_API_KEY env vars."""
# /// script
# dependencies = ["httpx"]
# ///

import os
import sys
from datetime import datetime
from typing import Any

import httpx

BASE_URL = os.environ.get("TRACEARR_URL", "").rstrip("/")
API_KEY = os.environ.get("TRACEARR_API_KEY", "")


def api(endpoint: str, params: dict | None = None) -> Any:
    """Make authenticated GET request to Tracearr API."""
    if not BASE_URL or not API_KEY:
        sys.exit("Error: Set TRACEARR_URL and TRACEARR_API_KEY environment variables")
    url = f"{BASE_URL}/api/v1/public/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = httpx.get(url, params=params, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def health():
    """Get system health and server connectivity."""
    data = api("health")
    print(f"Status: {data['status']}")
    print(f"Timestamp: {data['timestamp']}")
    print("\nServers:")
    for server in data.get("servers", []):
        status = "🟢 Online" if server["online"] else "🔴 Offline"
        streams = server.get("activeStreams", 0)
        print(
            f"  {server['name']} ({server['type']}) - {status} - {streams} active streams"
        )


def stats(server_id: str | None = None):
    """Get dashboard statistics."""
    params = {}
    if server_id:
        params["serverId"] = server_id
    data = api("stats", params)
    print(f"Active Streams: {data['activeStreams']}")
    print(f"Total Users: {data['totalUsers']}")
    print(f"Total Sessions (30d): {data['totalSessions']}")
    print(f"Recent Violations (7d): {data['recentViolations']}")
    print(f"Timestamp: {data['timestamp']}")


def streams(server_id: str | None = None, summary_only: bool = False):
    """Get active playback sessions."""
    params = {}
    if server_id:
        params["serverId"] = server_id
    if summary_only:
        params["summary"] = "true"

    data = api("streams", params)

    # Always show summary
    summary = data.get("summary", {})
    print(f"Total Streams: {summary.get('total', 0)}")
    print(f"  Transcodes: {summary.get('transcodes', 0)}")
    print(f"  Direct Streams: {summary.get('directStreams', 0)}")
    print(f"  Direct Plays: {summary.get('directPlays', 0)}")
    print(f"Total Bitrate: {summary.get('totalBitrate', 'N/A')}")

    # Show by-server breakdown if multiple servers
    by_server = summary.get("byServer", [])
    if len(by_server) > 1:
        print("\nBy Server:")
        for srv in by_server:
            print(
                f"  {srv['serverName']}: {srv['total']} streams ({srv['totalBitrate']})"
            )

    # Show detailed streams if not summary-only
    if not summary_only:
        stream_data = data.get("data", [])
        if stream_data:
            print("\nActive Streams:")
            for s in stream_data:
                media = s.get("mediaTitle", "Unknown")
                if s.get("showTitle"):
                    media = f"{s['showTitle']} - {media}"
                    if s.get("seasonNumber") and s.get("episodeNumber"):
                        media += f" (S{s['seasonNumber']:02d}E{s['episodeNumber']:02d})"

                user = s.get("username", "Unknown")
                state = s.get("state", "unknown")
                decision = (
                    "transcode"
                    if s.get("isTranscode")
                    else s.get("videoDecision", "unknown")
                )
                device = s.get("device") or s.get("player") or "Unknown"
                bitrate = f"{s.get('bitrate', 0)} kbps" if s.get("bitrate") else "N/A"

                print(f"\n  {user} - {media}")
                print(f"    State: {state} | Decision: {decision} | Device: {device}")
                print(
                    f"    Bitrate: {bitrate} | Server: {s.get('serverName', 'Unknown')}"
                )


def users(page: int = 1, page_size: int = 25, server_id: str | None = None):
    """List users with activity summary."""
    params = {"page": page, "pageSize": page_size}
    if server_id:
        params["serverId"] = server_id

    data = api("users", params)
    meta = data.get("meta", {})
    print(f"Users (Page {meta.get('page', 1)} of {meta.get('total', 0)} total):\n")

    for u in data.get("data", []):
        name = u.get("displayName", u.get("username", "Unknown"))
        trust = u.get("trustScore", 0)
        violations = u.get("totalViolations", 0)
        sessions = u.get("sessionCount", 0)
        last_activity = u.get("lastActivityAt")
        if last_activity:
            last_activity = datetime.fromisoformat(
                last_activity.replace("Z", "+00:00")
            ).strftime("%Y-%m-%d %H:%M")
        else:
            last_activity = "Never"

        print(f"{name} ({u.get('role', 'unknown')})")
        print(f"  Trust: {trust}/100 | Violations: {violations} | Sessions: {sessions}")
        print(
            f"  Server: {u.get('serverName', 'Unknown')} | Last Activity: {last_activity}\n"
        )


def violations(
    page: int = 1,
    page_size: int = 25,
    server_id: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
):
    """List violations with filtering."""
    params = {"page": page, "pageSize": page_size}
    if server_id:
        params["serverId"] = server_id
    if severity:
        params["severity"] = severity
    if acknowledged is not None:
        params["acknowledged"] = "true" if acknowledged else "false"

    data = api("violations", params)
    meta = data.get("meta", {})
    print(f"Violations (Page {meta.get('page', 1)} of {meta.get('total', 0)} total):\n")

    for v in data.get("data", []):
        rule = v.get("rule", {})
        user = v.get("user", {})
        severity_emoji = {"low": "🟡", "warning": "🟠", "high": "🔴"}.get(
            v.get("severity", "low"), "⚪"
        )
        ack = "✓ Acknowledged" if v.get("acknowledged") else "✗ Unacknowledged"
        created = datetime.fromisoformat(
            v["createdAt"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M")

        print(
            f"{severity_emoji} {rule.get('name', 'Unknown Rule')} - {user.get('username', 'Unknown User')}"
        )
        print(
            f"  Type: {rule.get('type', 'unknown')} | Severity: {v.get('severity', 'unknown')}"
        )
        print(f"  Status: {ack} | Created: {created}")
        print(f"  Server: {v.get('serverName', 'Unknown')}\n")


def history(
    page: int = 1,
    page_size: int = 25,
    server_id: str | None = None,
    state: str | None = None,
    media_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Get session history with filtering."""
    params = {"page": page, "pageSize": page_size}
    if server_id:
        params["serverId"] = server_id
    if state:
        params["state"] = state
    if media_type:
        params["mediaType"] = media_type
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    data = api("history", params)
    meta = data.get("meta", {})
    print(
        f"Session History (Page {meta.get('page', 1)} of {meta.get('total', 0)} total):\n"
    )

    for s in data.get("data", []):
        media = s.get("mediaTitle", "Unknown")
        if s.get("showTitle"):
            media = f"{s['showTitle']} - {media}"
            if s.get("seasonNumber") and s.get("episodeNumber"):
                media += f" (S{s['seasonNumber']:02d}E{s['episodeNumber']:02d})"

        user = s.get("user", {}).get("username", "Unknown")
        started = datetime.fromisoformat(
            s["startedAt"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M")
        stopped = s.get("stoppedAt")
        if stopped:
            stopped = datetime.fromisoformat(stopped.replace("Z", "+00:00")).strftime(
                "%Y-%m-%d %H:%M"
            )
        else:
            stopped = "In Progress"

        duration_mins = s.get("durationMs", 0) // 60000
        progress_mins = s.get("progressMs", 0) // 60000

        print(f"{media} ({s.get('year', '?')})")
        print(f"  User: {user} | Type: {s.get('mediaType', 'unknown')}")
        print(f"  Started: {started} | Stopped: {stopped}")
        print(
            f"  Progress: {progress_mins}/{duration_mins} min | Device: {s.get('device', 'Unknown')}"
        )
        print(f"  Server: {s.get('serverName', 'Unknown')}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tracearr.py <command> [options]")
        print("\nCommands:")
        print(
            "  health                                    - Server health and connectivity"
        )
        print("  stats [--server-id <uuid>]                - Dashboard statistics")
        print("  streams [--server-id <uuid>] [--summary]  - Active playback sessions")
        print("  users [--page N] [--page-size N] [--server-id <uuid>]")
        print(
            "  violations [--page N] [--page-size N] [--server-id <uuid>] [--severity low|warning|high] [--acknowledged true|false]"
        )
        print(
            "  history [--page N] [--page-size N] [--server-id <uuid>] [--state playing|paused|stopped] [--media-type movie|episode|...] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]"
        )
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    # Parse common flags
    def get_flag(flag: str, default: Any = None) -> Any:
        try:
            idx = args.index(flag)
            if idx + 1 < len(args):
                return args[idx + 1]
        except ValueError:
            pass
        return default

    def has_flag(flag: str) -> bool:
        return flag in args

    try:
        if cmd == "health":
            health()
        elif cmd == "stats":
            stats(server_id=get_flag("--server-id"))
        elif cmd == "streams":
            streams(
                server_id=get_flag("--server-id"), summary_only=has_flag("--summary")
            )
        elif cmd == "users":
            page = int(get_flag("--page", 1))
            page_size = int(get_flag("--page-size", 25))
            users(page=page, page_size=page_size, server_id=get_flag("--server-id"))
        elif cmd == "violations":
            page = int(get_flag("--page", 1))
            page_size = int(get_flag("--page-size", 25))
            severity = get_flag("--severity")
            ack = get_flag("--acknowledged")
            acknowledged = None if ack is None else ack.lower() == "true"
            violations(
                page=page,
                page_size=page_size,
                server_id=get_flag("--server-id"),
                severity=severity,
                acknowledged=acknowledged,
            )
        elif cmd == "history":
            page = int(get_flag("--page", 1))
            page_size = int(get_flag("--page-size", 25))
            history(
                page=page,
                page_size=page_size,
                server_id=get_flag("--server-id"),
                state=get_flag("--state"),
                media_type=get_flag("--media-type"),
                start_date=get_flag("--start-date"),
                end_date=get_flag("--end-date"),
            )
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
