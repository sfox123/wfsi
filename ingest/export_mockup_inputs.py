"""Export the inputs for the formula mockup page (public.mockup_inputs()) to a JSON file."""
import json, os, sys
import psycopg

out = sys.argv[1]
url = os.environ.get("SUPABASE_DB_URL") or sys.exit("set SUPABASE_DB_URL")
with psycopg.connect(url) as conn, conn.cursor() as cur:
    cur.execute("select public.mockup_inputs()")
    data = cur.fetchone()[0]
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with open(out, "w") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
print(f"{len(data['countries'])} countries -> {out}")
