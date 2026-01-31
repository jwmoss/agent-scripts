---
name: jellyseerr
description: Search for movies and TV shows and request them via Jellyseerr/Seerr API. Use when the user wants to request media, find movies or TV shows to add to their library, or interact with their Jellyseerr instance. Triggers on phrases like "request a movie", "add to jellyseerr", "find and request", "search jellyseerr", or mentions of requesting media content.
---

# Jellyseerr Media Requests

Request movies and TV shows through the Jellyseerr/Seerr API.

## Prerequisites

Set these environment variables:
- `JELLYSEERR_URL` - Base URL (e.g., `http://localhost:5055`)
- `JELLYSEERR_API_KEY` - API key from Jellyseerr Settings > General

## Workflow

### 1. Search for Media

```bash
curl -s "${JELLYSEERR_URL}/api/v1/search?query=SEARCH_TERM" \
  -H "X-Api-Key: ${JELLYSEERR_API_KEY}" | jq
```

Response contains `results` array with:
- `id` - TMDB ID (use this for requests)
- `mediaType` - "movie" or "tv"
- `title` (movies) or `name` (TV)
- `overview` - Description
- `releaseDate` or `firstAirDate`

### 2. Create Request

**Movie:**
```bash
curl -s -X POST "${JELLYSEERR_URL}/api/v1/request" \
  -H "X-Api-Key: ${JELLYSEERR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"mediaType": "movie", "mediaId": TMDB_ID}'
```

**TV Show (all seasons):**
```bash
curl -s -X POST "${JELLYSEERR_URL}/api/v1/request" \
  -H "X-Api-Key: ${JELLYSEERR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"mediaType": "tv", "mediaId": TMDB_ID, "seasons": "all"}'
```

**TV Show (specific seasons):**
```bash
curl -s -X POST "${JELLYSEERR_URL}/api/v1/request" \
  -H "X-Api-Key: ${JELLYSEERR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"mediaType": "tv", "mediaId": TMDB_ID, "seasons": [1, 2, 3]}'
```

### Request Options

| Field | Type | Description |
|-------|------|-------------|
| `mediaType` | string | Required: "movie" or "tv" |
| `mediaId` | number | Required: TMDB ID from search |
| `seasons` | array\|"all" | TV only: season numbers or "all" |
| `is4k` | boolean | Request 4K version |

### Response Status Codes

Request `status` field:
- `1` = Pending approval
- `2` = Approved
- `3` = Declined

Media availability `status`:
- `3` = Processing
- `4` = Partially available
- `5` = Available

## Examples

**User:** "Request the movie Dune"
1. Search: `query=Dune`
2. Find the correct result (check year/overview)
3. POST request with `mediaType: "movie"` and the `id`

**User:** "Add Breaking Bad to Jellyseerr"
1. Search: `query=Breaking Bad`
2. Confirm it's the right show
3. POST request with `mediaType: "tv"`, `seasons: "all"`

**User:** "Request season 1 of The Office"
1. Search: `query=The Office`
2. Clarify which version if ambiguous (US/UK)
3. POST with `seasons: [1]`

## Script

Use `scripts/jellyseerr.py` for a streamlined workflow:

```bash
# Search
uv run scripts/jellyseerr.py search "Movie Name"

# Request movie
uv run scripts/jellyseerr.py request movie TMDB_ID

# Request TV (all seasons)
uv run scripts/jellyseerr.py request tv TMDB_ID

# Request specific seasons
uv run scripts/jellyseerr.py request tv TMDB_ID --seasons 1 2 3
```
