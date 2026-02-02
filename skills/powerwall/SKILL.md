---
name: powerwall
description: Query Tesla Powerwall energy data from InfluxDB. Use for energy reports, solar production, grid usage, battery status, and self-sufficiency calculations. Triggers on "powerwall", "energy report", "solar production", "grid usage", "battery status", "how much solar", "energy yesterday", "power consumption".
---

# Powerwall Energy Reporting

## Invocation
- `/powerwall` or `/powerwall status` - Real-time status (default)
- `/powerwall yesterday` - Yesterday's energy summary
- `/powerwall today` - Today so far
- `/powerwall this week` - Week summary (Monday-Sunday)
- `/powerwall this month` - Month summary
- `/powerwall january` - Specific month
- `/powerwall 2026-01-15` - Specific date
- `/powerwall 2026-01-01 to 2026-01-15` - Date range

## Infrastructure
- **InfluxDB 1.8**: `192.168.1.254:8086`, database `powerwall`, measurement `http`
- **PyPowerwall Proxy**: `192.168.1.254:8675`
- **Fields (W)**: `site_instant_power`, `load_instant_power`, `solar_instant_power`, `battery_instant_power`
- **Battery SOC**: `percentage`

For additional endpoints, query examples, and schema details, see [references/api.md](references/api.md).

## Real-Time Status (Default)

Query latest values:

```bash
curl -sG 'http://192.168.1.254:8086/query' \
  --data-urlencode "db=powerwall" \
  --data-urlencode "q=SELECT LAST(load_instant_power), LAST(solar_instant_power), LAST(site_instant_power), LAST(battery_instant_power), LAST(percentage) FROM http"
```

**Parse `results[0].series[0].values[0]`:**
- Index 1: load_instant_power (W) - home consumption
- Index 2: solar_instant_power (W) - solar production
- Index 3: site_instant_power (W) - grid (positive=import, negative=export)
- Index 4: battery_instant_power (W) - battery (positive=charging, negative=discharging)
- Index 5: percentage - battery SOC %

**Output format:**
```
## Powerwall Status

| Metric | Value |
|--------|-------|
| Solar Production | X.XX kW |
| Home Consumption | X.XX kW |
| Grid Import/Export | X.XX kW |
| Battery | X.XX kW (charging/discharging) |
| Battery SOC | XX.X% |
```

Convert W to kW (÷1000), round to 2 decimals. Show import/export and charging/discharging based on sign.

## Historical Energy Reports

Calculate energy by integrating power over time.

### 1. Determine Time Range
Use RFC3339 timestamps in America/New_York timezone.

- `yesterday`: Previous day midnight-to-midnight
- `today`: Midnight to now
- `this week`: Monday 00:00 to now
- `this month`: 1st 00:00 to now
- Month name: Full month in current year
- Date: Full day
- Range: Inclusive

### 2. Query InfluxDB

```bash
curl -sG 'http://192.168.1.254:8086/query' \
  --data-urlencode "db=powerwall" \
  --data-urlencode "q=SELECT INTEGRAL(load_instant_power, 1h) AS home_kwh, INTEGRAL(solar_instant_power, 1h) AS solar_kwh, INTEGRAL(site_instant_power, 1h) AS grid_kwh FROM http WHERE time >= '<START>' AND time < '<END>'"
```

The `1h` parameter returns kWh directly.

### 3. Parse & Calculate

From `results[0].series[0].values[0]`:
- Index 1: home_kwh
- Index 2: solar_kwh
- Index 3: grid_kwh (positive=import, negative=export)

```
grid_import = max(grid_kwh, 0)
grid_export = abs(min(grid_kwh, 0))
self_sufficiency = clamp((1 - grid_import/home_kwh) * 100, 0, 100)
```

### 4. Output

```
## Powerwall Report: <Period>

| Metric | Value |
|--------|-------|
| Solar Production | XX.XX kWh |
| Home Consumption | XX.XX kWh |
| Grid Import | XX.XX kWh |
| Grid Export | XX.XX kWh |
| Net Grid | XX.XX kWh |
| Self-Sufficiency | XX.X% |
```

## Error Handling
- Empty results: "No data available for the requested period"
- Connection failure: Check InfluxDB at 192.168.1.254:8086
