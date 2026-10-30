# WSFI — Water Security Futures Index

Data pipeline and index engine for the Water Security Futures Index. The index relates projected water risk to anticipatory and adaptive readiness, with an equity modifier.

## Layout

| Path | Contents |
|---|---|
| `docs/earth-engine-jobs.md` | Spec for the indicators computed in Google Earth Engine |
| `ee/` | Earth Engine scripts (one per job) |
| `docs/api.md` | How developers query the data (Supabase REST API) |
| `ingest/` | Loaders: `load_long_csv.py` loads any long-format CSV (dummy data, Earth Engine exports) as one tracked run |
| `supabase/migrations/` | Database schema and storage buckets; `supabase/seed_reference.sql` holds pillars, indicators, units and default weights |
| `data/dummy/` | Synthetic sample data and its generator (not real values) |

## Supabase

Project `wsfi` (IWMI organisation, ap-southeast-1). Storage buckets: `raw-sources` and `ee-exports` (private), `releases` (public).

Load the dummy data once: add the repository secret `SUPABASE_DB_URL` (Supabase dashboard → Connect → Session pooler URI), then run the **Load dummy data** workflow from the Actions tab.

## Data flow

Sources (APIs, Earth Engine exports, checked file uploads) → Supabase Postgres (long-format observations, with provenance for each pull) → index functions with versioned weight sets → REST API.
