---
name: jellyseerr
description: Request movies and TV shows on mossflix through Jellyseerr at requests.mossflix.com. Use when the user wants to request media, add a film or show to the library, or check the status of a request. Triggers on "request a movie", "add to jellyseerr", "request season", "mossflix requests", or "add X to my library".
---

# Jellyseerr

Jellyseerr is the request front end for mossflix. It runs at `https://requests.mossflix.com`.
It reads the library from Jellyfin. It sends approved requests to Radarr and Sonarr.

Use this skill to request media. Use the `radarr` or `sonarr` skill to change the library
directly, or to add many titles at once.

## Credentials

```bash
URL=https://requests.mossflix.com
KEY=$(op read "op://Private/Jellyseerr API Key/credential")
```

Send the `X-Api-Key` header on every call. The API returns 401 with no key and 403 with a bad key.

## Search

```bash
curl -s --get "$URL/api/v1/search" --data-urlencode "query=dune" -H "X-Api-Key: $KEY" \
  | jq -r '.results[] | select(.mediaType != "person")
      | "\(.id)\t\(.mediaType)\t\(.title // .name)\t\(.releaseDate // .firstAirDate)"'
```

The `id` field is the TMDB ID. Use it as `mediaId` in a request.

## Request

```bash
# Movie
curl -s -X POST "$URL/api/v1/request" -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"mediaType":"movie","mediaId":438631}'

# TV, all seasons
curl -s -X POST "$URL/api/v1/request" -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"mediaType":"tv","mediaId":1396,"seasons":"all"}'

# TV, specific seasons
curl -s -X POST "$URL/api/v1/request" -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"mediaType":"tv","mediaId":1396,"seasons":[1,2]}'
```

Add `"is4k":true` for a 4K request.

TV requests need the `seasons` field. Jellyseerr rejects a TV request without it.

## Status

```bash
curl -s "$URL/api/v1/request?take=20&sort=added" -H "X-Api-Key: $KEY" \
  | jq -r '.results[] | "\(.id)\t\(.type)\t\(.media.tmdbId)\tstatus=\(.status)\tmedia=\(.media.status)"'
```

| Field | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| request `status` | Pending | Approved | Declined | — | — |
| `media.status` | Unknown | Pending | Processing | Partially available | Available |

## Notes

- Confirm the correct title with the user when the search gives more than one close match.
  Ask which version you must request, for example The Office US or UK.
- A duplicate request returns 409. Treat that as "already requested" and continue.
- For a bulk job, such as a whole franchise, use `radarr` and `sonarr` instead. Those skills
  set the quality profile and start the search in one call per title.
