# Sonarr API Reference

Base URL: `{SONARR_URL}/api/v3`
Auth: Header `X-Api-Key: {SONARR_API_KEY}`

## Series Endpoints

### List All Series
```
GET /series
GET /series?includeSeasonImages=true
```
Returns array of SeriesResource.

### Search Series (Lookup)
```
GET /series/lookup?term={query}
```
Search for new series to add. Returns array of SeriesResource.

### Get Series by ID
```
GET /series/{id}
```
Returns single SeriesResource with full details.

### Add Series
```
POST /series
Body: SeriesResource (tvdbId, title, qualityProfileId, rootFolderPath required)
```

### Update Series
```
PUT /series/{id}
Body: SeriesResource
```

### Delete Series
```
DELETE /series/{id}?deleteFiles=false&addImportListExclusion=false
```

## SeriesResource Fields

Key fields returned:
- `id` - Internal Sonarr ID
- `title` - Series title
- `tvdbId` - TVDB identifier
- `year` - First air year
- `ended` - Boolean, true if series ended
- `episodeCount` - Total episodes
- `episodeFileCount` - Downloaded episodes
- `status` - "continuing" or "ended"
- `overview` - Series description
- `network` - TV network
- `genres` - Array of genre strings
- `path` - Local file path
- `qualityProfileId` - Quality profile ID
- `seasonCount` - Number of seasons

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
Upcoming episodes (ISO 8601 dates).

### System Status
```
GET /system/status
```
Version, OS, paths, etc.
