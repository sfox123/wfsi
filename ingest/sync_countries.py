"""Register every country (ADM0) from the World Bank country list in spatial_unit.
Existing rows are left as they are; aggregates (regions, income groups) are skipped."""
import os, sys
import psycopg, requests

r = requests.get("https://api.worldbank.org/v2/country", params={"format": "json", "per_page": 400}, timeout=60)
r.raise_for_status()
rows = [(c["id"], c["name"], c["region"]["value"].strip())
        for c in r.json()[1] if c["region"]["value"].strip() != "Aggregates"]

url = os.environ.get("SUPABASE_DB_URL") or sys.exit("set SUPABASE_DB_URL")
with psycopg.connect(url) as conn, conn.cursor() as cur:
    cur.executemany(
        "insert into spatial_unit (unit_id, level, name, region) values (%s, 'ADM0', %s, %s) "
        "on conflict (unit_id) do nothing", rows)
    conn.commit()
    cur.execute("select count(*) from spatial_unit where level = 'ADM0'")
    print(f"{len(rows)} countries in World Bank list; {cur.fetchone()[0]} ADM0 units in database")
