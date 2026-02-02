# PyPowerwall API Reference

## Documentation Links

- **PyPowerwall GitHub**: https://github.com/jasonacox/pypowerwall
- **Proxy API Docs**: https://github.com/jasonacox/pypowerwall/blob/main/proxy/API.md
- **Powerwall-Dashboard**: https://github.com/jasonacox/Powerwall-Dashboard
- **InfluxDB 1.8 Query Language**: https://docs.influxdata.com/influxdb/v1.8/query_language/

## PyPowerwall Proxy Endpoints

Base URL: `http://192.168.1.254:8675`

### Power Data (Flat JSON)
| Endpoint | Description |
|----------|-------------|
| `/pw/power` | Site, solar, battery, load power (W) - flat JSON |
| `/csv` | CSV format: home, grid, solar, battery, soc |
| `/soe` | Battery state of energy `{"percentage": X}` |
| `/freq` | Grid status `{"grid_status": 1}` |

### Aggregated Data (Nested JSON)
| Endpoint | Description |
|----------|-------------|
| `/aggregates` | Full metrics for site, battery, solar, load |
| `/api/meters/aggregates` | Raw gateway API payload |

### System Info
| Endpoint | Description |
|----------|-------------|
| `/stats` | Proxy statistics and health |
| `/vitals` | Device vitals |
| `/strings` | Solar string data |
| `/pod` | Battery pod info (time_remaining, backup_reserve) |
| `/temps/pw` | Powerwall temperatures |
| `/alerts/pw` | System alerts |

## InfluxDB Schema

Database: `powerwall`
Measurement: `http`

### Key Fields (from /aggregates flattening)
| Field | Type | Description |
|-------|------|-------------|
| `site_instant_power` | float | Grid power (W). Positive=importing, negative=exporting |
| `load_instant_power` | float | Home consumption (W) |
| `solar_instant_power` | float | Solar production (W) |
| `battery_instant_power` | float | Battery (W). Positive=charging, negative=discharging |
| `percentage` | float | Battery state of charge (0-100%) |
| `backup_reserve_percent` | float | Configured backup reserve |
| `time_remaining_hours` | float | Estimated backup time remaining |

### Energy Fields (often zero in Cloud mode)
| Field | Description |
|-------|-------------|
| `site_energy_imported` | Cumulative grid import (kWh) |
| `site_energy_exported` | Cumulative grid export (kWh) |
| `solar_energy_exported` | Cumulative solar production (kWh) |
| `load_energy_imported` | Cumulative home consumption (kWh) |

**Note:** In Cloud/FleetAPI mode, cumulative energy fields are often zero. Use `INTEGRAL()` on instant power fields instead.

## Useful InfluxDB Queries

### Latest readings
```sql
SELECT LAST(load_instant_power), LAST(solar_instant_power),
       LAST(site_instant_power), LAST(percentage)
FROM http
```

### Energy for time period (using INTEGRAL)
```sql
SELECT INTEGRAL(load_instant_power, 1h) AS home_kwh,
       INTEGRAL(solar_instant_power, 1h) AS solar_kwh,
       INTEGRAL(site_instant_power, 1h) AS grid_kwh
FROM http
WHERE time >= '2026-01-01T00:00:00-05:00'
  AND time < '2026-01-02T00:00:00-05:00'
```

### Average power over period
```sql
SELECT MEAN(load_instant_power), MEAN(solar_instant_power)
FROM http
WHERE time >= now() - 1h
```

### Peak power
```sql
SELECT MAX(load_instant_power) AS peak_load,
       MAX(solar_instant_power) AS peak_solar
FROM http
WHERE time >= '2026-01-01T00:00:00-05:00'
  AND time < '2026-01-02T00:00:00-05:00'
```

## Response Examples

### /pw/power
```json
{"site": 3461, "solar": 0, "battery": 0, "load": 3461}
```

### /soe
```json
{"percentage": 23.34}
```

### /aggregates (nested structure)
```json
{
  "site": {
    "instant_power": 3461,
    "energy_exported": 0,
    "energy_imported": 0,
    ...
  },
  "battery": {...},
  "load": {...},
  "solar": {...}
}
```

## Telegraf Configuration

Config location: `/mnt/user/appdata/powerwall/telegraf.conf`

Key settings:
- Collection interval: 5s
- HTTP timeout: 10s (increased from 4s to handle slow /pod endpoint)
- Output: InfluxDB at 192.168.1.254:8086
