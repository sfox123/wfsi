"""Load a long-format WSFI CSV into Supabase as one source_run.

Accepted columns (extra columns are ignored):
  unit_id | iso3        spatial unit (ISO3 or ISO 3166-2 district code)
  indicator_code        e.g. A3a
  year                  int
  scenario              default 'observed'
  value                 number or empty
  flag                  default 'reported' (empty value -> 'missing')
  period, weighting, note   optional

This is the format of data/dummy/wsfi_dummy_national_long.csv and of the
Earth Engine exports described in docs/earth-engine-jobs.md.

Usage:
  export SUPABASE_DB_URL='postgresql://postgres.<ref>:<password>@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'
  python ingest/load_long_csv.py FILE.csv --source "EE-1 ERA5-Land" [--synthetic] [--script-version ee-1_v1.0] [--dry-run]
"""
import argparse, hashlib, io, os, sys
import pandas as pd

COLS = ["unit_id", "indicator_code", "year", "period", "scenario", "value", "flag", "weighting", "note"]


def prepare(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "unit_id" not in df.columns and "iso3" in df.columns:
        df = df.rename(columns={"iso3": "unit_id"})
    missing = {"unit_id", "indicator_code", "year"} - set(df.columns)
    if missing:
        sys.exit(f"missing required columns: {sorted(missing)}")
    for c in COLS:
        if c not in df.columns:
            df[c] = None
    df["scenario"] = df["scenario"].fillna("observed")
    df["flag"] = df["flag"].fillna("reported")
    df.loc[df["value"].isna() & ~df["flag"].isin(["missing", "not_applicable"]), "flag"] = "missing"
    df["year"] = df["year"].astype(int)
    dupes = df.duplicated(["unit_id", "indicator_code", "year", "scenario"]).sum()
    if dupes:
        sys.exit(f"{dupes} duplicate unit/indicator/year/scenario rows")
    return df[COLS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--source", required=True)
    ap.add_argument("--source-version")
    ap.add_argument("--script-version")
    ap.add_argument("--storage-path", help="path of the raw file in Supabase Storage, if uploaded")
    ap.add_argument("--synthetic", action="store_true", help="mark the run as dummy data")
    ap.add_argument("--notes")
    ap.add_argument("--drop-unknown-units", action="store_true",
                    help="skip rows for units not in spatial_unit instead of failing")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    df = prepare(a.csv)
    sha = hashlib.sha256(open(a.csv, "rb").read()).hexdigest()
    codes = sorted(df.indicator_code.unique())
    print(f"{len(df)} rows, {df.unit_id.nunique()} units, indicators: {', '.join(codes)}")
    if a.dry_run:
        return

    import psycopg
    url = os.environ.get("SUPABASE_DB_URL") or sys.exit("set SUPABASE_DB_URL")
    with psycopg.connect(url) as conn, conn.cursor() as cur:
        # fail early with a clear message if codes are unknown
        cur.execute("select code from indicator"); known_i = {r[0] for r in cur.fetchall()}
        cur.execute("select unit_id from spatial_unit"); known_u = {r[0] for r in cur.fetchall()}
        bad_i = set(codes) - known_i; bad_u = set(df.unit_id) - known_u
        if bad_u and a.drop_unknown_units:
            print(f"dropping {df.unit_id.isin(bad_u).sum()} rows for {len(bad_u)} unknown units: {sorted(bad_u)[:15]}")
            df = df[~df.unit_id.isin(bad_u)]
            bad_u = set()
        if bad_i or bad_u:
            sys.exit(f"unknown indicator codes {sorted(bad_i)} / unit ids {sorted(bad_u)[:10]}")

        cur.execute(
            """insert into source_run (source, indicator_codes, source_version, storage_path,
                                       file_sha256, script_version, row_count, is_synthetic, notes)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id""",
            (a.source, codes, a.source_version, a.storage_path, sha, a.script_version,
             len(df), a.synthetic, a.notes))
        run_id = cur.fetchone()[0]

        buf = io.StringIO()
        df.assign(run_id=run_id)[["run_id"] + COLS].to_csv(buf, index=False, header=False)
        buf.seek(0)
        with cur.copy("copy observation (run_id, unit_id, indicator_code, year, period, scenario, "
                      "value, flag, weighting, note) from stdin with (format csv)") as cp:
            cp.write(buf.read())
        conn.commit()
    print(f"loaded as source_run {run_id}")


if __name__ == "__main__":
    main()
