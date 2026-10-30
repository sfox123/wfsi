"""Generate SYNTHETIC (dummy) data for the Water Security Futures Index (WSFI).
Values are simulated from rough country archetypes + noise. They mimic the units,
ranges, cadence, scenario structure and missingness of the real sources listed in
Water_Risk_Indicator_Database.xlsx, but they are NOT real data.
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(20261030)
SEED_NOTE = "numpy seed 20261030"

# ---------------------------------------------------------------- countries
# iso3, name, region, aridity, income, governance, glacier, coastal, island, transboundary_dep, conflict, pop_m
C = [
("LKA","Sri Lanka","South Asia",.35,.35,.45,0,.6,1,0,.2,22),
("IND","India","South Asia",.65,.30,.45,.4,.4,0,.35,.4,1430),
("PAK","Pakistan","South Asia",.85,.25,.30,.7,.3,0,.75,.6,240),
("BGD","Bangladesh","South Asia",.30,.25,.30,.15,.9,0,.9,.35,172),
("NPL","Nepal","South Asia",.30,.20,.35,.9,0,0,.1,.25,30),
("BTN","Bhutan","South Asia",.20,.35,.60,.8,0,0,.1,.05,.8),
("AFG","Afghanistan","South Asia",.85,.10,.10,.6,0,0,.3,.9,42),
("MDV","Maldives","South Asia",.10,.55,.40,0,1,1,0,.05,.5),
("CHN","China","East Asia & Pacific",.55,.60,.50,.45,.4,0,.05,.2,1410),
("MMR","Myanmar","East Asia & Pacific",.30,.20,.15,.3,.6,0,.4,.8,54),
("THA","Thailand","East Asia & Pacific",.40,.55,.45,0,.6,0,.4,.25,72),
("VNM","Viet Nam","East Asia & Pacific",.30,.45,.45,.05,.9,0,.6,.1,99),
("KHM","Cambodia","East Asia & Pacific",.30,.25,.25,0,.4,0,.8,.15,17),
("IDN","Indonesia","East Asia & Pacific",.20,.45,.50,0,.7,1,0,.25,278),
("PHL","Philippines","East Asia & Pacific",.25,.40,.45,0,.8,1,0,.4,117),
("AUS","Australia","East Asia & Pacific",.80,.95,.85,0,.3,1,0,.05,26),
("NZL","New Zealand","East Asia & Pacific",.10,.90,.92,.3,.3,1,0,.02,5.2),
("FJI","Fiji","East Asia & Pacific",.30,.50,.50,0,.8,1,0,.1,.93),
("UZB","Uzbekistan","Europe & Central Asia",.90,.30,.30,.5,0,0,.8,.2,36),
("KAZ","Kazakhstan","Europe & Central Asia",.70,.60,.40,.4,.1,0,.4,.1,20),
("NLD","Netherlands","Europe & Central Asia",.10,.98,.90,0,1,0,.9,.03,17.9),
("ESP","Spain","Europe & Central Asia",.80,.85,.75,.1,.3,0,.1,.05,48),
("DEU","Germany","Europe & Central Asia",.20,.95,.90,.05,.2,0,.4,.03,84),
("IRN","Iran","Middle East & North Africa",.90,.45,.25,.1,.3,0,.1,.4,89),
("IRQ","Iraq","Middle East & North Africa",.90,.35,.15,.05,.2,0,.6,.8,45),
("JOR","Jordan","Middle East & North Africa",.97,.45,.50,0,.05,0,.3,.3,11),
("SAU","Saudi Arabia","Middle East & North Africa",.99,.85,.50,0,.2,0,0,.2,37),
("EGY","Egypt","Middle East & North Africa",.99,.35,.35,0,.6,0,.97,.35,112),
("MAR","Morocco","Middle East & North Africa",.80,.40,.45,0,.4,0,0,.15,37),
("NGA","Nigeria","Sub-Saharan Africa",.55,.30,.25,0,.4,0,.2,.85,224),
("ETH","Ethiopia","Sub-Saharan Africa",.55,.15,.30,0,0,0,0,.7,127),
("KEN","Kenya","Sub-Saharan Africa",.65,.30,.40,0,.2,0,.35,.4,55),
("SOM","Somalia","Sub-Saharan Africa",.85,.05,.05,0,.4,0,.6,.95,18),
("ZAF","South Africa","Sub-Saharan Africa",.70,.55,.55,0,.2,0,.1,.3,60),
("MOZ","Mozambique","Sub-Saharan Africa",.40,.15,.30,0,.6,0,.5,.6,33),
("MDG","Madagascar","Sub-Saharan Africa",.45,.10,.30,0,.4,1,0,.3,30),
("BRA","Brazil","Latin America & Caribbean",.20,.55,.45,0,.3,0,.3,.3,216),
("PER","Peru","Latin America & Caribbean",.60,.50,.40,.85,.3,0,.15,.25,34),
("BOL","Bolivia","Latin America & Caribbean",.50,.35,.30,.7,0,0,.2,.25,12),
("CHL","Chile","Latin America & Caribbean",.75,.70,.70,.75,.3,0,.05,.1,19.6),
("MEX","Mexico","Latin America & Caribbean",.75,.60,.40,0,.3,0,0,.5,128),
("HTI","Haiti","Latin America & Caribbean",.50,.08,.05,0,.6,0,.1,.8,11.7),
("USA","United States","North America",.55,.95,.75,.2,.3,0,.05,.15,335),
("CAN","Canada","North America",.10,.95,.85,.4,.2,0,.05,.05,40),
]
cols = ["iso3","country","region","aridity","income","gov","glacier","coastal","island","tbdep","conflict","pop_m"]
ctry = pd.DataFrame(C, columns=cols)

def n(sd=1.0, size=None): return rng.normal(0, sd, size)
def clip(x, lo, hi): return float(np.clip(x, lo, hi))
def lognorm(mu, sd): return float(np.exp(rng.normal(mu, sd)))

# ---------------------------------------------------------------- metadata
META = [
# code, pillar, indicator, unit, direction_raw, resolution, cadence, source, type
("A1","A","Projected blue-water stress","ratio (withdrawal / available)","higher = more risk","Sub-basin→national","Scenario (2030/2050/2080)","WRI Aqueduct 4.0 future annual (ws)","Direct"),
("A2","A","Projected water depletion","ratio (consumption / renewable supply)","higher = more risk","Sub-basin→national","Scenario (2030/2050/2080)","WRI Aqueduct 4.0 future annual (wd)","Direct"),
("A3a","A","Green-water availability (mean soil moisture, layers 1–2)","m³/m³","higher = LESS risk (invert)","Grid→national","Annual","ERA5-Land monthly","Calculate"),
("A3b","A","Green-water trend (Sen's slope of soil moisture, 1981–2024)","m³/m³ per decade","negative = drying = more risk","Grid→national","Single value","ERA5-Land monthly","Calculate"),
("A4","A","Groundwater storage trend (GRACE TWS minus GLDAS SM+snow, 2002–yr)","cm EWT per year","negative = decline = more risk","Grid→national","Annual (rolling trend)","GRACE/GRACE-FO JPL Mascon + GLDAS","Calculate"),
("A5a","A","Inter-annual variability","coefficient of variation","higher = more risk","Sub-basin→national","Scenario (2030/2050/2080)","WRI Aqueduct 4.0 future annual (iv)","Direct"),
("A5b","A","Seasonal variability","coefficient of variation","higher = more risk","Sub-basin→national","Scenario (2030/2050/2080)","WRI Aqueduct 4.0 future annual (sv)","Direct"),
("A6","A","Hydroclimate whiplash frequency (1991–2024)","transitions per decade","higher = more risk","Grid→national","Single value","SPEIbase + Swain et al. (2025) method","Calculate"),
("A7","A","Glacier/snow meltwater dependence","% of runoff from glacier/snow","higher = more risk","Basin→national","Single value","Immerzeel 2020 / Hugonnet 2021","Calculate"),
("A8","A","Population in low-elevation coastal zone exposed to projected SLR","% of population","higher = more risk","Coastal grid→national","Scenario (2050/2100)","NASA AR6 SLR tool + GHSL","Calculate"),
("B1","B","Population in high-stress basins (Aqueduct cat ≥3)","% of population","higher = more risk","Grid→national","Scenario (2030/2050/2080)","WorldPop × Aqueduct future","Calculate"),
("B2","B","GDP in high-stress basins","% of GDP","higher = more risk","Grid→national","Scenario (2030/2050/2080)","Wang & Sun SSP GDP × Aqueduct","Calculate"),
("B3","B","Irrigation withdrawal change vs 2015 baseline","% change","higher = more risk","Grid→national","Scenario (2030/2050/2080)","ISIMIP3b water use","Calculate"),
("B4","B","Domestic + industrial withdrawal change vs 2015 baseline","% change","higher = more risk","Grid→national","Scenario (2030/2050/2080)","ISIMIP3b water use","Calculate"),
("B5","B","Sectoral competition index (Shannon of shares × stress)","index 0–1","higher = more risk","National","Irregular (AQUASTAT)","AQUASTAT / WDI + Aqueduct","Calculate"),
("B6","B","Agriculture value added","% of GDP","higher = more risk","National","Annual","World Bank WDI NV.AGR.TOTL.ZS","Proxy"),
("B7","B","Water-related conflict events","events per million people per year","higher = more risk","National","Annual","Pacific Institute WCC / ACLED / UCDP","Calculate"),
("B8a","B","Dependency ratio (external renewable water)","%","higher = more risk","National","Single value (long-term avg)","FAO AQUASTAT","Direct"),
("B8b","B","Flood & drought disaster displacements","per 100,000 people per year","higher = more risk","National","Annual","IDMC GIDD","Direct"),
("C1","C","Multi-hazard early-warning system score (Sendai G-1)","score 0–1","higher = more ready","National","Annual (self-reported)","Sendai Framework Monitor, Target G","Direct"),
("C2","C","Seasonal precipitation forecast skill (ROC area, lead 1 month)","ROC area 0.5–1","higher = more ready","Grid→national","Single value","C3S hindcasts vs CHIRPS","Calculate"),
("C3","C","S2S / seasonal forecast uptake (expert score)","ordinal 0–4","higher = more ready","National","Survey round","Expert scoring rubric (no global dataset)","Survey / scoring"),
("C4","C","Active anticipatory-action frameworks","count","higher = more ready","National","Annual","Anticipation Hub overview reports","Direct"),
("C5","C","Pre-arranged finance","US$ per capita","higher = more ready","National","Annual","Anticipation Hub + risk-pool data","Calculate"),
("C6","C","Impact-based forecasting maturity (expert score)","ordinal 0–4","higher = more ready","National","Survey round","Expert scoring rubric (no global dataset)","Survey / scoring"),
("C7","C","Population covered by at least a 4G mobile network","% of population","higher = more ready","National","Annual","ITU DataHub","Proxy"),
("D1","D","Dam storage capacity per capita","m³ per person","higher = more ready","National","Single value","FAO AQUASTAT dams","Direct"),
("D2","D","Source diversification (Shannon index of withdrawal sources)","index 0–1.39","higher = more ready","National","Irregular","FAO AQUASTAT","Calculate"),
("D3","D","Water-use efficiency (SDG 6.4.1)","US$ per m³","higher = more ready","National","Annual (2-yr lag)","UN SDG Global Database","Direct"),
("D4","D","IWRM implementation (SDG 6.5.1)","score 0–100","higher = more ready","National","Triennial survey","UN-Water IWRM portal","Direct"),
("D5","D","Transboundary basin area with operational arrangement (SDG 6.5.2)","%","higher = more ready","National","Triennial survey","UN SDG Global Database","Direct"),
("D6","D","Governance (mean of WGI GE, RQ, RL, CC)","estimate −2.5 to +2.5","higher = more ready","National","Annual","World Bank WGI","Proxy"),
("D7","D","ND-GAIN readiness (economic + social components)","score 0–1","higher = more ready","National","Annual","ND-GAIN","Direct"),
("D8","D","Safely treated domestic wastewater (SDG 6.3.1)","%","higher = more ready","National","Irregular","UN SDG Global Database","Direct"),
("E1","E","Basic drinking-water access gap (richest − poorest quintile)","percentage points","higher = LESS equitable","National (from survey)","Irregular (JMP inequality)","WHO/UNICEF JMP","Calculate"),
("E2","E","Basic sanitation access gap (richest − poorest quintile)","percentage points","higher = LESS equitable","National (from survey)","Irregular (JMP inequality)","WHO/UNICEF JMP","Calculate"),
("E3","E","Internet use gender parity (female / male)","ratio","closer to 1 = more equitable","National","Annual","ITU DataHub","Calculate"),
("E4","E","Concentration index of water investment vs stress","index −1 to +1","negative = investment away from stressed areas","District→national","Single value","Aqueduct + AidData","Calculate"),
("E5","E","Participation level in water governance (SDG 6.b.1)","ordinal 0–3","higher = more equitable","National","GLAAS cycle","SDG 6.b.1 / WHO GLAAS","Proxy"),
("E6","E","Water bill share of income, poorest quintile","% of household income","higher = LESS equitable","National","Irregular","IBNET + World Bank PIP","Calculate"),
("X1","X","Water stress (SDG 6.4.2)","%","supporting","National","Annual","UN SDG Global Database","Direct"),
("X2","X","Disaster deaths & affected (SDG 13.1.1)","per 100,000 people","supporting / validation","National","Annual","UN SDG Global Database","Direct"),
("X4","X","Total population","persons","supporting","National","Annual","World Bank WDI SP.POP.TOTL","Direct"),
("X5","X","Total GDP","current US$","supporting","National","Annual","World Bank WDI NY.GDP.MKTP.CD","Direct"),
("X6","X","Renewable internal freshwater per capita","m³ per person","supporting","National","Annual","World Bank WDI ER.H2O.INTR.PC","Direct"),
]
meta = pd.DataFrame(META, columns=["code","pillar","indicator","unit","raw_direction","resolution","cadence","simulated_source","type"])
db_code = {c: (c[:2] if c[:2] in ("A3","A5","B8") else c) for c in meta.code}
meta.insert(1, "framework_id", meta.code.map(db_code))

rows = []
def add(r, code, year, value, scenario="observed", flag="reported", note=""):
    if value is not None and not (isinstance(value, float) and np.isnan(value)):
        value = round(float(value), 4)
    else:
        value = None
    rows.append(dict(iso3=r.iso3, country=r.country, region=r.region, indicator_code=code,
                     year=year, scenario=scenario, value=value, flag=flag, note=note))

YEARS = list(range(2015, 2025))
SCEN = {"optimistic":(-1,"SSP1-RCP2.6"),"bau":(0,"SSP3-RCP7.0"),"pessimistic":(1,"SSP5-RCP8.5")}
rand_missing = lambda p=0.03: rng.random() < p

for r in ctry.itertuples():
    ar, inc, gov = r.aridity, r.income, r.gov
    pop0 = r.pop_m * 1e6
    # ---- scenario-based indicators (Aqueduct / ISIMIP / SLR)
    ws0 = clip(np.exp(-3.2 + 3.6*ar + n(.35)), .005, 3)
    wd0 = clip(ws0*0.55 + n(.05), 0, 1)
    iv0 = clip(.15 + .7*ar + n(.08), .05, 1.4); sv0 = clip(.3 + .6*(1-ar)*.8 + .4*ar + n(.12), .1, 1.6)
    hs_pop0 = clip(100*(1/(1+np.exp(-(ar-.55)*9))) + n(6), 0, 100)
    hs_gdp0 = clip(hs_pop0*(1+n(.12)), 0, 100)
    add(r,"A1",2019,ws0,"baseline_1979-2019"); add(r,"A2",2019,wd0,"baseline_1979-2019")
    add(r,"A5a",2019,iv0,"baseline_1979-2019"); add(r,"A5b",2019,sv0,"baseline_1979-2019")
    add(r,"B1",2019,hs_pop0,"baseline_1979-2019"); add(r,"B2",2019,hs_gdp0,"baseline_1979-2019")
    for scen,(s,_) in SCEN.items():
        for yr, h in [(2030,.33),(2050,.67),(2080,1.0)]:
            g = h*(0.12 + 0.10*s + 0.15*ar)
            add(r,"A1",yr,ws0*(1+g+n(.03)),scen)
            add(r,"A2",yr,min(1,wd0*(1+g*.9+n(.03))),scen)
            add(r,"A5a",yr,iv0*(1+h*(.05+.05*s)+n(.02)),scen)
            add(r,"A5b",yr,sv0*(1+h*(.04+.04*s)+n(.02)),scen)
            add(r,"B1",yr,clip(hs_pop0*(1+g*1.2)+h*6*ar+n(1.5),0,100),scen)
            add(r,"B2",yr,clip(hs_gdp0*(1+g*1.1)+h*5*ar+n(1.5),0,100),scen)
            add(r,"B3",yr,h*(10+25*ar*(1-inc)+8*s)+n(3),scen)
            add(r,"B4",yr,h*(20+90*(1-inc)+15*s)+n(5),scen)
    for scen, s in [("SSP2-4.5",0),("SSP5-8.5",1)]:
        for yr,h in [(2050,.5),(2100,1)]:
            v = 0 if r.coastal == 0 else clip(r.coastal*(6+40*r.coastal**3)*(.5+h*(.6+.4*s)) + n(1), 0, 100)
            add(r,"A8",yr,v,scen, "reported" if r.coastal else "not_applicable", "" if r.coastal else "landlocked")
    # ---- panel indicators
    sm = clip(.38 - .26*ar + n(.02), .05, .48); sm_tr = -.004*ar - .002 + n(.0025)
    gw = -2.5*ar*(1-inc*.5) + .4 + n(.5)
    for i,yr in enumerate(YEARS):
        add(r,"A3a",yr,sm + sm_tr/10*(yr-2015) + n(.012),flag="modelled")
        add(r,"A4",yr,gw + n(.25),flag="modelled")
    add(r,"A3b",2024,sm_tr,flag="modelled")
    add(r,"A6",2024,clip(1.5 + 3*(1-abs(ar-.5)*1.6) + n(.6), .2, 8),flag="modelled")
    add(r,"A7",2020,clip(r.glacier**2*45 + n(1.5), 0, 60) if r.glacier>0 else 0.0,flag="modelled")

    pop_g = .022*(1-inc) + .002
    gdp0 = pop0 * lognorm(np.log(500 + 60000*inc**2), .15)
    for yr in YEARS:
        t = yr-2015
        pop = pop0*(1+pop_g)**(t-9); gdp = gdp0*(1.035 - .01*inc + n(.015))**(t-9)
        add(r,"X4",yr,round(pop)); add(r,"X5",yr,gdp)
        add(r,"X6",yr,clip(np.exp(10.2-4*ar+n(.05))*(1+pop_g)**(-(t-9)), 5, 1e5))
        add(r,"X1",yr,clip(ws0*100*1.2*(1+.01*t)+n(2), .5, 2000) if yr <= 2021 else None, flag="reported" if yr<=2021 else "missing", note="" if yr<=2021 else "not yet published")
        add(r,"X2",yr,lognorm(np.log(40+400*(1-inc)*(.5+r.coastal)), .9))
        add(r,"B6",yr,clip(2 + 30*(1-inc)**1.6 - .15*t + n(1), .5, 60) if not rand_missing() else None, flag="reported")
        add(r,"B7",yr,lognorm(np.log(.02+3*r.conflict**2), .5) if r.conflict>.05 else 0.0)
        add(r,"B8b",yr,lognorm(np.log(5 + 900*r.coastal*(1-inc)), 1.0) if rng.random()>.08 else 0.0)
        add(r,"C7",yr,clip(15 + 85*inc**.4 + 6*t*(1-inc) + n(3), 0, 100))
        if yr <= 2023: add(r,"D6",yr,clip(-2.2 + 4.2*gov + n(.12), -2.5, 2.5))
        if yr <= 2022:
            add(r,"D7",yr,clip(.15 + .55*inc + .15*gov + .005*t + n(.02), 0, 1))
            add(r,"D3",yr,lognorm(np.log(2 + 150*inc**2.2) + .02*t, .25))
        if 2017 <= yr <= 2023: add(r,"E3",yr,clip(.45 + .55*inc + .05*(t-2)*(1-inc)*.3 + n(.04), .3, 1.08))
    for yr in [2015, 2017, 2020]:
        add(r,"B5",yr,clip(.6*ar*(.4+.6*(1-inc)) + .2 + n(.06), 0, 1) if not rand_missing(.15) else None, flag="modelled")
    add(r,"B8a",2020,0.0 if r.island else clip(100*r.tbdep + n(2), 0, 98))
    # C pillar
    reports = rng.random() > (.45*(1-gov))
    for yr in range(2019, 2025):
        v = clip(.15 + .6*gov + .1*inc + .03*(yr-2019) + n(.05), 0, 1)
        add(r,"C1",yr, v if reports else None, flag="reported" if reports else "missing", note="" if reports else "country did not report to Sendai Monitor")
    add(r,"C2",2024,clip(.62 + .12*(1-ar) + .06*(r.region in ("South Asia","East Asia & Pacific","Latin America & Caribbean")) + n(.03), .5, .9),flag="modelled")
    add(r,"C3",2025,int(np.clip(round(1 + 2.5*gov + n(.6)), 0, 4)),flag="expert_score")
    add(r,"C6",2025,int(np.clip(round(.5 + 3*gov*inc**.3 + n(.6)), 0, 4)),flag="expert_score")
    lmic = inc < .7
    for yr in [2022, 2023, 2024]:
        cnt = int(rng.poisson(1 + 5*r.conflict*(1-inc) + 3*r.coastal*(1-inc)) + (yr-2022)*(rng.random()<.4)) if lmic else 0
        add(r,"C4",yr,cnt, flag="reported")
        add(r,"C5",yr,lognorm(np.log(.05 + cnt*.15), .8) if cnt else 0.0, flag="modelled")
    # D pillar
    add(r,"D1",2020,lognorm(np.log(60 + 2500*inc**1.5), .9))
    add(r,"D2",2020,clip(.3 + .5*inc + .2*ar + n(.12), 0, 1.39) if not rand_missing(.2) else None, flag="modelled", note="")
    for yr in [2017, 2020, 2023]:
        add(r,"D4",yr,clip(15 + 60*gov + 10*inc + 3*((yr-2017)/3) + n(5), 5, 100))
        if r.island: add(r,"D5",yr,None,flag="not_applicable",note="no transboundary waters")
        else: add(r,"D5",yr,clip(100*(.2+.6*gov) + n(15), 0, 100) if not rand_missing(.1) else None)
    for yr in [2020, 2022]:
        add(r,"D8",yr,clip(5 + 85*inc**1.3 + 2*(yr-2020) + n(5), 0, 100) if not rand_missing(.15) else None)
    # E pillar
    for yr in [2016, 2019, 2022]:
        if inc > .85:
            add(r,"E1",yr,None,flag="missing",note="JMP inequality data not produced for this country")
            add(r,"E2",yr,None,flag="missing",note="JMP inequality data not produced for this country")
        else:
            add(r,"E1",yr,clip(55*(1-inc)**1.2 - 1.5*(yr-2016)/3 + n(4), 0, 90),flag="modelled")
            add(r,"E2",yr,clip(75*(1-inc)**1.1 - 2*(yr-2016)/3 + n(5), 0, 95),flag="modelled")
    add(r,"E4",2024,clip(-.4*(1-gov) + .2 + n(.12), -1, 1) if not rand_missing(.15) else None,flag="modelled")
    for yr in [2019, 2021, 2024]:
        add(r,"E5",yr,int(np.clip(round(.5 + 2.2*gov + n(.5)), 0, 3)))
    for yr in [2018, 2021]:
        add(r,"E6",yr,clip(1 + 6*(1-inc)*ar + n(.8), .2, 15) if rng.random() > .35 else None, flag="modelled")

panel = pd.DataFrame(rows)
panel.loc[panel.value.isna() & (panel.flag.isin(["reported","modelled"])), "flag"] = "missing"
panel.loc[(panel.flag=="missing") & (panel.note==""), "note"] = "no value published"
panel = panel.merge(meta[["code","framework_id","pillar","unit"]], left_on="indicator_code", right_on="code").drop(columns="code")
panel["is_synthetic"] = True
panel = panel[["iso3","country","region","pillar","framework_id","indicator_code","year","scenario","value","unit","flag","note","is_synthetic"]]
panel = panel.sort_values(["iso3","pillar","indicator_code","scenario","year"]).reset_index(drop=True)

# wide snapshot: latest observed year per indicator; scenario indicators -> BAU 2050
def latest(df):
    d = df.dropna(subset=["value"])
    return d.sort_values("year").groupby(["iso3","indicator_code"]).tail(1)
obs = latest(panel[panel.scenario=="observed"])
scen = panel[((panel.scenario=="bau") & (panel.year==2050)) | ((panel.scenario=="SSP2-4.5") & (panel.year==2050))]
snap = pd.concat([obs, scen])
wide = snap.pivot_table(index=["iso3","country","region"], columns="indicator_code", values="value", aggfunc="first").reset_index()
order = [c for c in meta.code if c in wide.columns]
wide = wide[["iso3","country","region"] + order]

# ---------------------------------------------------------------- Sri Lanka districts
D = [("LK-11","Colombo","Western",.2,1),("LK-12","Gampaha","Western",.25,1),("LK-13","Kalutara","Western",.15,1),
("LK-21","Kandy","Central",.25,0),("LK-22","Matale","Central",.45,0),("LK-23","Nuwara Eliya","Central",.15,0),
("LK-31","Galle","Southern",.15,1),("LK-32","Matara","Southern",.2,1),("LK-33","Hambantota","Southern",.75,1),
("LK-41","Jaffna","Northern",.8,1),("LK-42","Kilinochchi","Northern",.75,1),("LK-43","Mannar","Northern",.85,1),
("LK-44","Vavuniya","Northern",.7,0),("LK-45","Mullaitivu","Northern",.65,1),("LK-51","Batticaloa","Eastern",.65,1),
("LK-52","Ampara","Eastern",.65,1),("LK-53","Trincomalee","Eastern",.7,1),("LK-61","Kurunegala","North Western",.6,0),
("LK-62","Puttalam","North Western",.75,1),("LK-71","Anuradhapura","North Central",.8,0),("LK-72","Polonnaruwa","North Central",.75,0),
("LK-81","Badulla","Uva",.45,0),("LK-82","Monaragala","Uva",.7,0),("LK-91","Ratnapura","Sabaragamuwa",.1,0),("LK-92","Kegalle","Sabaragamuwa",.15,0)]
urban = {"Colombo":.95,"Gampaha":.7,"Kandy":.5,"Kalutara":.45,"Galle":.45,"Jaffna":.45,"Kurunegala":.35,"Matara":.4}
srows = []
for code,name,prov,dry,coast in D:
    u = urban.get(name,.2)
    ws = clip(np.exp(-2.6 + 2.6*dry + n(.25)), .02, 2.5)
    rec = dict(adm2_code=code, district=name, province=prov, climate_zone="Dry" if dry>=.6 else ("Intermediate" if dry>=.4 else "Wet"))
    for scen,(s,_) in SCEN.items():
        rec[f"A1_ws_2050_{scen}"] = round(ws*(1+.67*(.12+.1*s+.15*dry)),4)
    rec["A3a_soil_moisture_2024"] = round(clip(.4-.22*dry+n(.015),.08,.48),4)
    rec["A4_gw_trend_cm_yr_2024"] = round(-1.6*dry+.5+n(.3),3)
    rec["A5a_interannual_cv_2050_bau"] = round(clip(.2+.6*dry+n(.05),.05,1.2),4)
    rec["A6_whiplash_per_decade"] = round(clip(2+3*dry+n(.5),.2,8),2)
    rec["A8_pop_slr_exposed_pct_2050_SSP2-4.5"] = round(clip((4+10*u)*(1+n(.2)),0,60),2) if coast else 0.0
    rec["B1_pop_high_stress_pct_2050_bau"] = round(clip(100/(1+np.exp(-(dry-.55)*10))+n(5),0,100),2)
    rec["C7_4g_coverage_pct_2024"] = round(clip(70+30*u+n(4)-(8 if prov=="Northern" else 0),40,100),2)
    rec["E1_water_access_gap_pp_2022"] = round(clip(30*(1-u)+n(4),0,70),2)
    rec["E2_sanitation_access_gap_pp_2022"] = round(clip(20*(1-u)+n(4),0,70),2)
    rec["is_synthetic"] = True
    srows.append(rec)
lka = pd.DataFrame(srows)

ctry_out = ctry[["iso3","country","region","island","pop_m"]].rename(columns={"pop_m":"approx_population_millions","island":"is_island"})
ctry_out["is_island"] = ctry_out.is_island.astype(bool)
meta["is_synthetic"] = True
panel.to_pickle("panel.pkl"); wide.to_pickle("wide.pkl"); lka.to_pickle("lka.pkl"); meta.to_pickle("meta.pkl"); ctry_out.to_pickle("ctry.pkl")
print(len(panel), wide.shape, lka.shape)
print(panel.flag.value_counts())
