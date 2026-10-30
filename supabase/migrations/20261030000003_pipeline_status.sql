-- Collection route per indicator, pipeline_status view and pipeline_snapshot() for the status page.
-- (Applied to the live project as migration "pipeline_status"; see the Supabase migration history for the exact SQL.)
alter table public.indicator
  add column route text check (route in ('api','earth_engine','python_batch','upload','expert')),
  add column route_detail text;

create view public.pipeline_status
with (security_invoker = true) as
select i.code, i.framework_id, i.pillar, i.name, i.unit, i.source, i.route, i.route_detail, i.in_index,
       count(o.id) filter (where not r.is_synthetic and o.value is not null)    as real_values,
       count(o.id) filter (where r.is_synthetic and o.value is not null)        as dummy_values,
       count(distinct o.unit_id) filter (where not r.is_synthetic)              as real_units,
       count(distinct o.unit_id) filter (where r.is_synthetic)                  as dummy_units,
       max(r.retrieved_at) filter (where not r.is_synthetic)                    as last_real_pull,
       max(o.year) filter (where not r.is_synthetic and o.scenario = 'observed') as latest_real_year,
       case when count(o.id) filter (where not r.is_synthetic and o.value is not null) > 0 then 'collected'
            when count(o.id) filter (where r.is_synthetic) > 0 then 'dummy'
            else 'none' end as status
from public.indicator i
left join public.observation o on o.indicator_code = i.code
left join public.source_run r  on r.id = o.run_id
group by i.code;

create or replace function public.pipeline_snapshot()
returns json language sql stable security invoker set search_path = public as $$
  select json_build_object(
    'as_of', now(),
    'units', (select json_build_object('adm0', count(*) filter (where level='ADM0'),
                                       'adm2', count(*) filter (where level='ADM2')) from spatial_unit),
    'indicators', (select json_agg(p order by p.pillar, p.code) from pipeline_status p),
    'runs', (select json_agg(r) from (select id, source, indicator_codes, retrieved_at, row_count, is_synthetic, script_version
                                      from source_run order by id desc limit 25) r)
  );
$$;
