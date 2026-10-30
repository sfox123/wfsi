# WSFI — Earth Engine jobs

Spec for the indicators that must be computed from gridded data in Google Earth Engine (GEE).
Indicator codes follow `Water_Risk_Indicator_Database.xlsx`. Asset IDs marked **(check)** should be confirmed in the GEE catalog before use.

## Summary

| Job | Indicator(s) | Main inputs | Output | Effort |
|---|---|---|---|---|
| EE-1 | **A3a, A3b** Green-water availability & trend | ERA5-Land monthly soil moisture, cropland mask | Mean soil moisture + Sen's slope | Low |
| EE-2 | **A4** Groundwater storage trend | GRACE/GRACE-FO mascons, GLDAS | Groundwater trend, cm/yr | Medium |
| EE-3 | **A6** Hydroclimate whiplash | SPEI (or CHIRPS + ERA5 PET) | Wet↔dry transitions per decade | Medium |
| EE-4 | **A1, A2, A5, E4 (stress part)** Aqueduct → admin units | Aqueduct 4.0 sub-basins (upload), population grid | Demand/pop-weighted country & district values | Low |
| EE-5 | **B1** Population in high-stress basins | Population grid × Aqueduct future categories | % population, by scenario & year | Low |
| EE-6 | **B2** GDP in high-stress basins | Gridded GDP (upload) × Aqueduct | % GDP, by scenario & year | Low (needs upload) |
| EE-7 | **A8** Coastal / sea-level exposure | DEM, population grid, AR6 sea-level projections (upload) | % population exposed, 2050/2100 | Medium |
| EE-8 *(optional)* | **A5 sub-national** variability | CHIRPS | Inter-annual & seasonal CV per district | Low |

**Not GEE jobs** (handled in Python instead): B3, B4 (ISIMIP), C2 forecast skill (Copernicus C3S hindcasts via CDS API), A7 (published glacier datasets).

---

## Common rules (apply to every job)

**Units of analysis**
- **National:** all countries (ISO3). Boundaries: geoBoundaries ADM0 (catalog or uploaded asset); FAO GAUL acceptable as fallback.
- **Sri Lanka districts:** 25 districts, keyed by ISO 3166-2 code (`LK-11` … `LK-92`). Boundaries: geoBoundaries ADM2 for LKA.

**Aggregation:** state the weighting used in the output (`area`, `population` or `cropland`). Defaults are given per job.

**Output format:** one CSV per job run, long format, exactly these columns:

| column | example | notes |
|---|---|---|
| `unit_id` | `LKA` / `LK-71` | ISO3 or ISO 3166-2 district code |
| `unit_level` | `ADM0` / `ADM2` | |
| `indicator_code` | `A3a` | from the table above |
| `year` | `2024` | single year, or end year of a period |
| `period` | `1981-2024` | blank if single year |
| `scenario` | `observed` / `bau` / `optimistic` / `pessimistic` / `SSP2-4.5` / `SSP5-8.5` | |
| `value` | `0.2862` | raw value, native units, not normalised |
| `unit` | `m3/m3` | |
| `weighting` | `cropland` | `area`, `population`, `cropland`, `demand` |
| `source_assets` | `ECMWF/ERA5_LAND/MONTHLY_AGGR` | semicolon-separated |
| `script_version` | `ee-1_v1.0` | |
| `run_date` | `2026-11-05` | |

Export to Google Drive or a Cloud Storage bucket; it will be loaded into the WSFI database from there. Please also commit the GEE script (`.js` or Python) under `ee/` in this repo, so every number can be reproduced.

**Missing values:** leave `value` empty for units with no valid pixels (e.g. small islands outside GRACE resolution). Do not write 0.

---

## EE-1 · Green-water availability & trend (A3a, A3b)

- **Input:** `ECMWF/ERA5_LAND/MONTHLY_AGGR`, bands `volumetric_soil_water_layer_1` and `_layer_2`. Depth-weighted mean of layers 1–2 (0–7 cm and 7–28 cm, so weights 7/28 and 21/28).
- **Mask:** cropland and grassland only, since the indicator is about rainfed agriculture and pasture. Use ESA WorldCover (`ESA/WorldCover/v200`, classes 30 grassland and 40 cropland) **(check)**.
- **A3a:** annual mean soil moisture per unit, 2015–2024, one row per year. Unit `m3/m3`.
- **A3b:** Sen's slope of annual means for 1981–2024, per decade. One row, `year` = 2024, `period` = `1981-2024`. Unit `m3/m3 per decade`.
- **Weighting:** cropland area.
- **Note:** this is historical only. A future version would need ISIMIP/CMIP6 soil moisture and is out of scope for now.

## EE-2 · Groundwater storage trend (A4)

- **Inputs:**
  - `NASA/GRACE/MASS_GRIDS_V04/MASCON` (`lwe_thickness`, total water storage anomaly, cm).
  - `NASA/GLDAS/V021/NOAH/G025/T3H`: soil moisture layers, snow water equivalent and canopy water, aggregated to monthly.
- **Method:**
  1. Groundwater anomaly = GRACE total water storage anomaly − (GLDAS soil moisture + snow + canopy anomalies). Express the GLDAS terms as anomalies against the same baseline period as GRACE.
  2. Leave the gap between GRACE and GRACE-FO (mid-2017 to mid-2018) as missing; do not interpolate.
  3. For each year Y from 2015 to 2024, take the linear trend from 2002 to Y. Unit `cm/yr`.
- **Weighting:** area.
- **Note:** GRACE resolution is about 300 km effective, so district values for Sri Lanka will look nearly uniform. Produce them anyway, but flag this in the output.

## EE-3 · Hydroclimate whiplash (A6)

- **Inputs:** SPEI in the GEE catalog (`CSIC/SPEI/...`, latest version **(check)**), 3-month timescale. If it isn't available, compute SPEI from CHIRPS (`UCSB-CHG/CHIRPS/PENTAD`) precipitation and ERA5-Land evaporation.
- **Method:** count rapid transitions per pixel following Swain et al. (2025), https://doi.org/10.1038/s43017-024-00624-z. A transition is SPEI-3 ≤ −1 followed by ≥ +1 within N months, or the reverse. Please write N into the script header; propose 3 months.
- **Output:** transitions per decade over 1991–2024. One row, `year` = 2024.
- **Weighting:** area.

## EE-4 · Aqueduct 4.0 to countries and districts (A1, A2, A5, E4)

- **Inputs:**
  - Aqueduct 4.0 future annual sub-basins (already downloaded), uploaded as a table asset with the `ws`, `wd`, `iv` and `sv` columns for 2030/2050/2080 under the optimistic, BAU and pessimistic scenarios, plus baseline.
  - A population grid (GHSL `JRC/GHSL/P2023A/GHS_POP` or WorldPop) **(check)**.
- **Method:**
  - Rasterise or intersect the sub-basins with the admin units.
  - Aggregate ws (→ A1), wd (→ A2) and iv/sv (→ A5a/A5b) weighted by water demand where available, otherwise by population.
  - Write a separate row for each scenario × year.
- **E4 input:** the district-level ws for Sri Lanka from this job feeds the investment concentration index. The investment data itself comes from outside GEE.

## EE-5 · Population in high-stress basins (B1)

- **Inputs:** a population grid, and Aqueduct sub-basin stress categories (category ≥ 3 = high or extremely high).
- **Method:** % of population living in sub-basins with category ≥ 3, for each scenario × year (2030/2050/2080) and for baseline.
- **Assumption to state in the output:** current population (2020) unless SSP population grids are uploaded. If they are, use the SSP that matches the scenario: SSP1 optimistic, SSP3 BAU, SSP5 pessimistic.

## EE-6 · GDP in high-stress basins (B2)

- **Inputs:** gridded GDP, uploaded as an asset. Kummu et al. (2018) covers the historical baseline; Wang & Sun (2022) SSP gridded GDP covers the future.
- **Method:** same as EE-5 with GDP in place of population.
- **Blocker:** these datasets are not in the GEE catalog and must be uploaded first.

## EE-7 · Coastal / sea-level exposure (A8)

- **Inputs:**
  - DEM: Copernicus GLO-30 or NASADEM **(check)**.
  - A population grid.
  - IPCC AR6 sea-level projections from the NASA projection tool, uploaded as points or a grid for 2050 and 2100 under SSP2-4.5 and SSP5-8.5.
- **Method:** % of population on land whose elevation is ≤ projected local sea-level rise plus a fixed allowance, and hydrologically connected to the sea. Please state the allowance; propose 1 m for storm surge and tide.
- **Note:** landlocked countries get `value` = 0. The indicator measures sea-level exposure; there is no global salinity dataset, so it cannot measure salinity directly.

## EE-8 (optional) · District-scale variability (A5 sub-national)

- **Input:** CHIRPS precipitation.
- **Method:** for 1991–2024, compute the inter-annual coefficient of variation of annual totals (A5a) and the seasonal coefficient of variation of the monthly climatology (A5b), per district.
- **Why:** Aqueduct sub-basins are coarse for Sri Lanka, so this gives a historical cross-check at district level.

---

## Questions for the EE colleague

1. Which population grid do you prefer (GHSL or WorldPop)? We should use one everywhere.
2. Can you upload the Aqueduct sub-basin table and the GDP grids as shared assets?
3. Will the exports go to Drive or a Cloud Storage bucket, and who owns that location?
4. What is a realistic timeline per job? Suggested order: EE-4 → EE-5 → EE-1 → EE-2 → EE-3 → EE-7 → EE-6 → EE-8.
