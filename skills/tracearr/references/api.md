# Tracearr API Reference

Base URL: `{TRACEARR_URL}/api/v1/public`
Auth: Header `Authorization: Bearer {TRACEARR_API_KEY}`

All endpoints are read-only (GET requests).

## Core Endpoints

### Health Check

```
GET /health
```

Returns system health status and media server connectivity.

**Response:**

```json
{
  "status": "ok",
  "timestamp": "2026-02-05T12:00:00.000Z",
  "servers": [
    {
      "id": "uuid",
      "name": "Mossflix 3.0",
      "type": "plex",
      "online": true,
      "activeStreams": 3
    }
  ]
}
```

### Dashboard Statistics

```
GET /stats?serverId={uuid}
```

Returns aggregate statistics for dashboard overview.

**Query Parameters:**

- `serverId` (optional) - Filter to specific server UUID

**Response:**

```json
{
  "activeStreams": 5,
  "totalUsers": 24,
  "totalSessions": 1847,
  "recentViolations": 3,
  "timestamp": "2026-02-05T12:00:00.000Z"
}
```

### Active Streams

```
GET /streams?serverId={uuid}&summary={boolean}
```

Returns currently active playback sessions with transcode details.

**Query Parameters:**

- `serverId` (optional) - Filter to specific server UUID
- `summary` (optional, boolean) - If true, returns only summary statistics (omits data array)

**Response (default mode):**

```json
{
  "data": [
    {
      "id": "uuid",
      "serverId": "uuid",
      "serverName": "Mossflix 3.0",
      "username": "John Doe",
      "userThumb": "/photo/abc123",
      "userAvatarUrl": "/api/v1/images/proxy?...",
      "mediaTitle": "Inception",
      "mediaType": "movie",
      "showTitle": null,
      "seasonNumber": null,
      "episodeNumber": null,
      "year": 2010,
      "thumbPath": "/library/metadata/12345/thumb",
      "posterUrl": "/api/v1/images/proxy?...",
      "durationMs": 8880000,
      "state": "playing",
      "progressMs": 3600000,
      "startedAt": "2026-02-05T11:00:00.000Z",
      "isTranscode": false,
      "videoDecision": "directplay",
      "audioDecision": "directplay",
      "bitrate": 20000,
      "device": "Apple TV",
      "player": "Plex for Apple TV",
      "product": "Plex for Apple TV",
      "platform": "tvOS"
    }
  ],
  "summary": {
    "total": 5,
    "transcodes": 2,
    "directStreams": 1,
    "directPlays": 2,
    "totalBitrate": "45.2 Mbps",
    "byServer": [...]
  }
}
```

**Response (summary mode):**

```json
{
  "summary": {
    "total": 5,
    "transcodes": 2,
    "directStreams": 1,
    "directPlays": 2,
    "totalBitrate": "45.2 Mbps",
    "byServer": [
      {
        "serverId": "uuid",
        "serverName": "Mossflix 3.0",
        "total": 3,
        "transcodes": 1,
        "directStreams": 1,
        "directPlays": 1,
        "totalBitrate": "22.5 Mbps"
      }
    ]
  }
}
```

### Users

```
GET /users?page={int}&pageSize={int}&serverId={uuid}
```

Returns paginated user list with activity metrics and trust scores.

**Query Parameters:**

- `page` (default: 1) - Page number (1-indexed)
- `pageSize` (default: 25, max: 100) - Items per page
- `serverId` (optional) - Filter to specific server UUID

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "username": "john_doe",
      "displayName": "John Doe",
      "thumbUrl": "/photo/abc123",
      "avatarUrl": "/api/v1/images/proxy?...",
      "role": "viewer",
      "trustScore": 95,
      "totalViolations": 2,
      "serverId": "uuid",
      "serverName": "Mossflix 3.0",
      "lastActivityAt": "2026-02-05T10:30:00.000Z",
      "sessionCount": 147,
      "createdAt": "2025-01-01T00:00:00.000Z"
    }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "pageSize": 25
  }
}
```

### Violations

```
GET /violations?page={int}&pageSize={int}&serverId={uuid}&severity={string}&acknowledged={boolean}
```

Returns paginated list of rule violations (account sharing detection).

**Query Parameters:**

- `page` (default: 1) - Page number
- `pageSize` (default: 25, max: 100) - Items per page
- `serverId` (optional) - Filter to specific server UUID
- `severity` (optional) - Filter by severity: `low`, `warning`, `high`
- `acknowledged` (optional, boolean) - Filter by acknowledged status

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "serverId": "uuid",
      "serverName": "Mossflix 3.0",
      "severity": "high",
      "acknowledged": false,
      "data": {},
      "createdAt": "2026-02-05T09:00:00.000Z",
      "rule": {
        "id": "uuid",
        "type": "concurrent_streams",
        "name": "Max 2 concurrent streams"
      },
      "user": {
        "id": "uuid",
        "username": "John Doe",
        "thumbUrl": "/photo/abc123",
        "avatarUrl": "/api/v1/images/proxy?..."
      }
    }
  ],
  "meta": {
    "total": 15,
    "page": 1,
    "pageSize": 25
  }
}
```

### History

```
GET /history?page={int}&pageSize={int}&serverId={uuid}&state={string}&mediaType={string}&startDate={date}&endDate={date}
```

Returns paginated session playback history with filtering.

**Query Parameters:**

- `page` (default: 1) - Page number
- `pageSize` (default: 25, max: 100) - Items per page
- `serverId` (optional) - Filter to specific server UUID
- `state` (optional) - Filter by playback state: `playing`, `paused`, `stopped`
- `mediaType` (optional) - Filter by media type: `movie`, `episode`, `track`, `live`, `photo`, `unknown`
- `startDate` (optional, ISO 8601) - Filter sessions after this date
- `endDate` (optional, ISO 8601) - Filter sessions before this date

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "serverId": "uuid",
      "serverName": "Mossflix 3.0",
      "state": "stopped",
      "mediaType": "movie",
      "mediaTitle": "Inception",
      "showTitle": null,
      "seasonNumber": null,
      "episodeNumber": null,
      "year": 2010,
      "thumbPath": "/library/metadata/12345/thumb",
      "posterUrl": "/api/v1/images/proxy?...",
      "durationMs": 8880000,
      "progressMs": 8850000,
      "startedAt": "2026-02-04T20:00:00.000Z",
      "stoppedAt": "2026-02-04T22:28:00.000Z",
      "device": "Apple TV",
      "player": "Plex for Apple TV",
      "user": {
        "id": "uuid",
        "username": "John Doe",
        "thumbUrl": "/photo/abc123",
        "avatarUrl": "/api/v1/images/proxy?..."
      }
    }
  ],
  "meta": {
    "total": 1847,
    "page": 1,
    "pageSize": 25
  }
}
```

## Enums and Constants

### Media Types

- `movie` - Feature films
- `episode` - TV show episodes
- `track` - Music tracks
- `live` - Live TV
- `photo` - Photos
- `unknown` - Unknown media type

### Playback States

- `playing` - Currently playing
- `paused` - Paused
- `stopped` - Stopped/ended

### Severity Levels

- `low` - Low severity violation
- `warning` - Warning level violation
- `high` - High severity violation

### Server Types

- `plex` - Plex Media Server
- `jellyfin` - Jellyfin
- `emby` - Emby

### User Roles

- `owner` - Server owner
- `admin` - Administrator
- `viewer` - Regular viewer
- `member` - Member
- `disabled` - Disabled account
- `pending` - Pending activation
