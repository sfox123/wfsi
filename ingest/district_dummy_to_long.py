"""Convert data/dummy/wsfi_dummy_lka_districts.csv (wide) to the long format
accepted by load_long_csv.py."""
import sys
import pandas as pd

# column -> (indicator_code, year, scenario)
MAP = {
    "A1_ws_2050_optimistic": ("A1", 2050, "optimistic"),
    "A1_ws_2050_bau": ("A1", 2050, "bau"),
    "A1_ws_2050_pessimistic": ("A1", 2050, "pessimistic"),
    "A3a_soil_moisture_2024": ("A3a", 2024, "observed"),
    "A4_gw_trend_cm_yr_2024": ("A4", 2024, "observed"),
    "A5a_interannual_cv_2050_bau": ("A5a", 2050, "bau"),
    "A6_whiplash_per_decade": ("A6", 2024, "observed"),
    "A8_pop_slr_exposed_pct_2050_SSP2-4.5": ("A8", 2050, "SSP2-4.5"),
    "B1_pop_high_stress_pct_2050_bau": ("B1", 2050, "bau"),
    "C7_4g_coverage_pct_2024": ("C7", 2024, "observed"),
    "E1_water_access_gap_pp_2022": ("E1", 2022, "observed"),
    "E2_sanitation_access_gap_pp_2022": ("E2", 2022, "observed"),
}

src, dst = sys.argv[1], sys.argv[2]
w = pd.read_csv(src)
rows = []
for d in w.to_dict("records"):
    for col, (code, year, scen) in MAP.items():
        rows.append(dict(unit_id=d["adm2_code"], indicator_code=code, year=year, scenario=scen,
                         value=d[col], flag="modelled"))
pd.DataFrame(rows).to_csv(dst, index=False)
print(f"{len(rows)} rows -> {dst}")
