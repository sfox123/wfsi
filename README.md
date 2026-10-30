# WSFI — Water Security Futures Index

Data pipeline and index engine for the Water Security Futures Index. The index relates projected water risk to anticipatory and adaptive readiness, with an equity modifier.

## Layout

| Path | Contents |
|---|---|
| `docs/earth-engine-jobs.md` | Spec for the indicators computed in Google Earth Engine |
| `ee/` | Earth Engine scripts (one per job) |
| `ingest/` | Python jobs that pull API sources into the database *(planned)* |
| `supabase/` | Database schema, migrations and index functions *(planned)* |

## Data flow

Sources (APIs, Earth Engine exports, checked file uploads) → Supabase Postgres (long-format observations, with provenance for each pull) → index functions with versioned weight sets → REST API.
