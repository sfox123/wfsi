-- WSFI core schema: reference tables, provenance, observations, weights.

-- ---------------------------------------------------------------- reference
create table public.pillar (
  code          text primary key check (code in ('A','B','C','D','E','X')),
  name          text not null,
  role          text not null check (role in ('risk','readiness','equity','supporting')),
  sort_order    smallint not null
);
comment on table public.pillar is 'WSFI pillars. A,B = risk (numerator); C,D = readiness (denominator); E = equity modifier; X = supporting data.';

create table public.indicator (
  code              text primary key,                 -- e.g. A3a
  framework_id      text not null,                    -- e.g. A3 (code in the indicator framework)
  pillar            text not null references public.pillar(code),
  name              text not null,
  unit              text not null,
  higher_is         text not null check (higher_is in ('worse','better','context')),
  raw_direction     text,                             -- human-readable note
  resolution        text,
  cadence           text,
  source            text,
  data_type         text check (data_type in ('Direct','Calculate','Proxy','Survey / scoring')),
  in_index          boolean not null default true     -- false for supporting (X) data
);
comment on column public.indicator.higher_is is 'Meaning of a higher RAW value: worse (more risk / less equity), better (more readiness / equity), context (supporting data).';

create table public.spatial_unit (
  unit_id     text primary key,                       -- ISO3 (ADM0) or ISO 3166-2 (ADM2)
  level       text not null check (level in ('ADM0','ADM1','ADM2')),
  name        text not null,
  parent_id   text references public.spatial_unit(unit_id),
  region      text,
  is_island   boolean,
  attributes  jsonb not null default '{}'::jsonb
);
create index on public.spatial_unit (parent_id);

-- ---------------------------------------------------------------- provenance
create table public.source_run (
  id              bigint generated always as identity primary key,
  source          text not null,                      -- e.g. 'World Bank WDI', 'EE-1 ERA5-Land'
  indicator_codes text[] not null default '{}',
  retrieved_at    timestamptz not null default now(),
  source_version  text,                               -- dataset version / release
  storage_path    text,                               -- object path in Supabase Storage (raw file)
  file_sha256     text,
  script_version  text,
  row_count       integer,
  is_synthetic    boolean not null default false,
  notes           text
);
comment on table public.source_run is 'One row per data pull or upload. Every observation points to the run that produced it.';

-- ---------------------------------------------------------------- observations
create table public.observation (
  id              bigint generated always as identity primary key,
  run_id          bigint not null references public.source_run(id) on delete cascade,
  unit_id         text not null references public.spatial_unit(unit_id),
  indicator_code  text not null references public.indicator(code),
  year            smallint not null check (year between 1950 and 2150),
  period          text,                               -- e.g. '1981-2024' for trends
  scenario        text not null default 'observed'
                  check (scenario in ('observed','baseline_1979-2019','optimistic','bau','pessimistic','SSP2-4.5','SSP5-8.5')),
  value           double precision,
  flag            text not null default 'reported'
                  check (flag in ('reported','modelled','expert_score','missing','not_applicable')),
  weighting       text,                               -- area / population / cropland / demand
  note            text,
  unique (run_id, unit_id, indicator_code, year, scenario),
  check (value is not null or flag in ('missing','not_applicable'))
);
create index on public.observation (indicator_code, year, scenario);
create index on public.observation (unit_id);

-- Latest value per unit x indicator x year x scenario (newest run wins).
-- Synthetic runs are only used where no real run exists.
create view public.observation_current
with (security_invoker = true) as
select distinct on (o.unit_id, o.indicator_code, o.year, o.scenario)
       o.unit_id, u.level as unit_level, u.name as unit_name,
       o.indicator_code, i.pillar, i.framework_id,
       o.year, o.period, o.scenario, o.value, i.unit, o.flag, o.note,
       r.is_synthetic, r.source, r.id as run_id, r.retrieved_at
from public.observation o
join public.source_run r   on r.id = o.run_id
join public.indicator i    on i.code = o.indicator_code
join public.spatial_unit u on u.unit_id = o.unit_id
order by o.unit_id, o.indicator_code, o.year, o.scenario,
         r.is_synthetic asc, r.retrieved_at desc, r.id desc;

-- ---------------------------------------------------------------- weights
create table public.weight_set (
  id           bigint generated always as identity primary key,
  name         text not null unique,
  description  text,
  method       text,                                  -- equal / expert elicitation / AHP / PCA ...
  is_default   boolean not null default false,
  created_at   timestamptz not null default now()
);
create unique index weight_set_one_default on public.weight_set (is_default) where is_default;

create table public.weight (
  weight_set_id  bigint not null references public.weight_set(id) on delete cascade,
  level          text not null check (level in ('pillar','indicator')),
  code           text not null,                       -- pillar code or indicator code
  weight         double precision not null check (weight >= 0),
  primary key (weight_set_id, level, code)
);

-- ---------------------------------------------------------------- access
-- Public read for all tables; writes only via service role (pipelines).
alter table public.pillar       enable row level security;
alter table public.indicator    enable row level security;
alter table public.spatial_unit enable row level security;
alter table public.source_run   enable row level security;
alter table public.observation  enable row level security;
alter table public.weight_set   enable row level security;
alter table public.weight       enable row level security;

create policy "public read" on public.pillar       for select using (true);
create policy "public read" on public.indicator    for select using (true);
create policy "public read" on public.spatial_unit for select using (true);
create policy "public read" on public.source_run   for select using (true);
create policy "public read" on public.observation  for select using (true);
create policy "public read" on public.weight_set   for select using (true);
create policy "public read" on public.weight       for select using (true);
