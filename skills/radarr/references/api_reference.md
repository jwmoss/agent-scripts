# Radarr API Reference

Base URL: `{RADARR_URL}/api/v3`
Auth: Header `X-Api-Key: {RADARR_API_KEY}`

## Movie Endpoints

### List All Movies
```
GET /movie
GET /movie?page=1&pageSize=10
```
Returns array of MovieResource.

### Search Movies (Lookup)
```
GET /movie/lookup?term={query}
```
Search for new movies to add. Returns array of MovieResource.

### Get Movie by ID
```
GET /movie/{id}
```
Returns single MovieResource with full details.

### Add Movie
```
POST /movie
Body: MovieResource (tmdbId, title, qualityProfileId, rootFolderPath required)
```

### Update Movie
```
PUT /movie/{id}
Body: MovieResource
```

### Delete Movie
```
DELETE /movie/{id}?deleteFiles=false&addImportExclusion=false
```

## MovieResource Fields

Key fields returned:
- `id` - Internal Radarr ID
- `title` - Movie title
- `tmdbId` - TMDB identifier
- `imdbId` - IMDB identifier
- `year` - Release year
- `hasFile` - Boolean, true if movie file exists
- `status` - "released", "announced", "inCinemas"
- `overview` - Movie description
- `studio` - Production studio
- `genres` - Array of genre strings
- `path` - Local file path
- `qualityProfileId` - Quality profile ID
- `runtime` - Runtime in minutes
- `ratings` - Rating info (imdb, tmdb, etc.)

## Other Useful Endpoints

### Queue
```
GET /queue
```
Current download queue.

### Calendar
```
GET /calendar?start={date}&end={date}
```
Upcoming releases (ISO 8601 dates).

### System Status
```
GET /system/status
```
Version, OS, paths, etc.
