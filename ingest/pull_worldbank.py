"""Pull World Bank indicators (WDI + WGI) into long-format CSV.

  B6  Agriculture value added (% of GDP)          NV.AGR.TOTL.ZS
  D6  Governance: mean of WGI GE, RQ, RL, CC     GOV_WGI_{GE,RQ,RL,CC}_EST (needs >= 3 of 4)
  X4  Total population                            SP.POP.TOTL
  X5  Total GDP (current US$)                     NY.GDP.MKTP.CD
  X6  Renewable internal freshwater per capita    ER.H2O.INTR.PC

Usage: python ingest/pull_worldbank.py out.csv
"""
import sys, time
import pandas as pd, requests

API = "https://api.worldbank.org/v2/country/all/indicator/{code}"
YEARS = "2010:2025"
DIRECT = {"B6": "NV.AGR.TOTL.ZS", "X4": "SP.POP.TOTL", "X5": "NY.GDP.MKTP.CD", "X6": "ER.H2O.INTR.PC"}
WGI = ["GOV_WGI_GE_EST", "GOV_WGI_RQ_EST", "GOV_WGI_RL_EST", "GOV_WGI_CC_EST"]


def fetch(code: str) -> pd.DataFrame:
    rows, page = [], 1
    while True:
        for attempt in range(3):
            r = requests.get(API.format(code=code),
                             params={"format": "json", "date": YEARS, "per_page": 20000, "page": page}, timeout=60)
            if r.ok:
                break
            time.sleep(3 * (attempt + 1))
        r.raise_for_status()
        body = r.json()
        if len(body) < 2 or body[1] is None:
            msg = body[0].get("message") if isinstance(body[0], dict) else body
            print(f"  {code}: no data ({msg})")
            return pd.DataFrame(columns=["unit_id", "year", "value"])
        meta, data = body
        rows += [{"unit_id": d["countryiso3code"], "year": int(d["date"]), "value": d["value"]}
                 for d in data if d.get("countryiso3code")]
        if page >= int(meta["pages"]):
            break
        page += 1
    df = pd.DataFrame(rows)
    print(f"  {code}: {df.value.notna().sum()} values, last updated {meta.get('lastupdated')}")
    return df


def main(out: str):
    import os; os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    frames = []
    for ind, code in DIRECT.items():
        df = fetch(code).dropna(subset=["value"])
        df["indicator_code"] = ind
        df["note"] = f"WB {code}"
        frames.append(df)

    w = None
    for code in WGI:
        df = fetch(code).dropna(subset=["value"]).rename(columns={"value": code})
        w = df if w is None else w.merge(df, on=["unit_id", "year"], how="outer")
    w["n"] = w[WGI].notna().sum(axis=1)
    w = w[w.n >= 3]
    d6 = pd.DataFrame({"unit_id": w.unit_id, "year": w.year, "value": w[WGI].mean(axis=1),
                       "indicator_code": "D6", "note": "mean of WGI " + w.n.astype(str) + "/4 dimensions"})
    frames.append(d6)

    out_df = pd.concat(frames, ignore_index=True)
    out_df["scenario"] = "observed"
    out_df["flag"] = "reported"
    out_df.loc[out_df.indicator_code == "D6", "flag"] = "modelled"
    out_df.to_csv(out, index=False)
    print(f"wrote {len(out_df)} rows -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
