# Tautulli API Reference

API endpoint: `{TAUTULLI_URL}/api/v2?apikey={TAUTULLI_API_KEY}&cmd={command}`

## History & Activity

### get_history
Playback history with filtering.

| Param | Description |
|-------|-------------|
| `length` | Number of records (default 25) |
| `start_date` | YYYY-MM-DD format |
| `user` | Filter by username |
| `media_type` | movie, episode, track, live, collection, playlist |
| `transcode_decision` | direct play, transcode, copy |
| `search` | Search title/user |
| `order_column` | date, friendly_name, title, etc. |
| `order_dir` | desc, asc |

Returns: `data[]` with `user`, `full_title`, `media_type`, `started`, `stopped`, `duration`, `transcode_decision`, `ip_address`, `player`, `platform`, `quality_profile`

### get_activity
Current streaming sessions.

Returns: `stream_count`, `sessions[]` with `user`, `full_title`, `state`, `progress_percent`, `transcode_decision`, `quality_profile`, `platform`, `player`, `ip_address`, `bandwidth`

## Users

### get_users
All users.

Returns array: `user_id`, `username`, `friendly_name`, `email`, `last_seen`, `do_notify`, `is_active`

### get_user
Single user details.

| Param | Description |
|-------|-------------|
| `user_id` | User ID (required) |

### get_library_user_stats
User stats per library.

| Param | Description |
|-------|-------------|
| `section_id` | Library ID (required) |

Returns: `user_id`, `username`, `total_plays`, `total_duration`

## Libraries

### get_libraries
All library sections.

Returns array: `section_id`, `section_name`, `section_type`, `count`, `parent_count`, `child_count`, `is_active`

### get_library_media_info
Media items in library.

| Param | Description |
|-------|-------------|
| `section_id` | Library ID (required) |
| `length` | Results count |
| `search` | Search term |
| `order_column` | title, year, rating, etc. |

### get_recently_added
Recently added items.

| Param | Description |
|-------|-------------|
| `count` | Number of items |
| `media_type` | movie, show, artist, album |
| `section_id` | Specific library |

## Statistics & Graphs

### get_home_stats
Homepage statistics. Key stat_ids:

- `top_movies`, `popular_movies` - Movie stats
- `top_tv`, `popular_tv` - TV stats
- `top_music`, `popular_music` - Music stats
- `top_users` - Most active users
- `top_platforms` - Most used platforms
- `last_watched` - Recent plays
- `most_concurrent` - Peak concurrent streams

| Param | Description |
|-------|-------------|
| `time_range` | Days (default 30) |
| `stats_count` | Results per stat |
| `stat_id` | Specific stat only |

### get_plays_by_date
Daily play counts.

| Param | Description |
|-------|-------------|
| `time_range` | Days |
| `y_axis` | plays, duration |
| `user_id` | Filter by user |

### get_plays_by_dayofweek
Weekly patterns.

### get_plays_by_hourofday
Hourly patterns.

### get_plays_by_stream_type
Direct play vs transcode breakdown.

### get_plays_by_top_10_users
Top user activity.

### get_plays_by_top_10_platforms
Platform distribution.

### get_library_watch_time_stats
Library viewing stats.

| Param | Description |
|-------|-------------|
| `section_id` | Library ID (required) |
| `query_days` | Comma-separated day ranges (e.g., "1,7,30") |

Returns: `query_days`, `total_time`, `total_plays`

## Data Export

### export_metadata
Export library/user data.

| Param | Description |
|-------|-------------|
| `section_id` | Library ID |
| `user_id` | User ID |
| `rating_key` | Specific item |
| `file_format` | csv, json, xml, m3u8 |
| `metadata_level` | 0-3 detail level |

### get_exports_table
List completed exports.

## Server Info

### get_server_info
Server configuration and version.

### get_servers_info
All connected servers.

### get_server_identity
Server identification.

### get_geoip_lookup
IP geolocation.

| Param | Description |
|-------|-------------|
| `ip_address` | IP to look up |
