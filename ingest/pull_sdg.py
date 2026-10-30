"""Pull UN SDG Global Database series into long-format CSV.

  D3  Water-use efficiency (SDG 6.4.1)              ER_H2O_WUEYST
  D4  IWRM implementation (SDG 6.5.1)               ER_H2O_IWRMD
  D5  Transboundary cooperation (SDG 6.5.2)         EG_TBA_H2CO
  D8  Safely treated domestic wastewater (6.3.1)    EN_WWT_WWDS
  E5  Participation in water resources planning     ER_WAT_PART (0-3, SDG 6.b.1)
  X1  Water stress (SDG 6.4.2)                      ER_H2O_STRESS
  X2  People directly affected by disasters / 100k  VC_DSR_DAFF (SDG 13.1.1)

Areas come as UN M49 codes; converted to ISO3 with pycountry.
Usage: python ingest/pull_sdg.py out.csv
"""
import sys, time
import pandas as pd, pycountry, requests

API = "https://unstats.un.org/sdgapi/v1/sdg/Series/Data"
SERIES = {"D3": "ER_H2O_WUEYST", "D4": "ER_H2O_IWRMD", "D5": "EG_TBA_H2CO", "D8": "EN_WWT_WWDS",
          "E5": "ER_WAT_PART", "X1": "ER_H2O_STRESS", "X2": "VC_DSR_DAFF"}
TOTALS = {"_T", "TOTAL", "ALL", "ALLAREA", "ALLSECT", "_Z", "G", "BOTHSEX"}


def m49_to_iso3(code):
    try:
        c = pycountry.countries.get(numeric=f"{int(code):03d}")
        return c.alpha_3 if c else None
    except (ValueError, TypeError):
        return None


def to_float(v):
    try:
        f = float(str(v).replace(">", "").replace("<", "").strip())
        return None if f != f else f   # drop NaN
    except ValueError:
        return None


def fetch(series):
    rows, page = [], 1
    while True:
        for attempt in range(3):
            r = requests.get(API, params={"seriesCode": series, "pageSize": 5000, "page": page}, timeout=120)
            if r.ok:
                break
            time.sleep(5 * (attempt + 1))
        r.raise_for_status()
        body = r.json()
        rows += body.get("data", [])
        if page >= body.get("totalPages", 1):
            break
        page += 1
    return rows


def main(out):
    import os; os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    frames = []
    for ind, series in SERIES.items():
        recs = fetch(series)
        out_rows = []
        for d in recs:
            iso3 = m49_to_iso3(d.get("geoAreaCode"))
            val = to_float(d.get("value"))
            if not iso3 or val is None:
                continue
            dims = d.get("dimensions") or {}
            # rank: global-reporting, total-breakdown rows first
            non_total = sum(1 for k, v in dims.items() if v not in TOTALS)
            out_rows.append({"unit_id": iso3, "year": int(float(d["timePeriodStart"])), "value": val,
                             "rank": non_total, "note": f"SDG {series}; source: {(d.get('source') or '')[:80]}"})
        df = pd.DataFrame(out_rows)
        if df.empty:
            print(f"  {series}: no country values")
            continue
        df = df.sort_values("rank").drop_duplicates(["unit_id", "year"]).drop(columns="rank")
        df["indicator_code"] = ind
        print(f"  {series}: {len(df)} country-year values, {df.unit_id.nunique()} countries, "
              f"years {df.year.min()}-{df.year.max()}")
        frames.append(df)

    out_df = pd.concat(frames, ignore_index=True)
    out_df["scenario"] = "observed"
    out_df["flag"] = "reported"
    out_df.to_csv(out, index=False)
    print(f"wrote {len(out_df)} rows -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
