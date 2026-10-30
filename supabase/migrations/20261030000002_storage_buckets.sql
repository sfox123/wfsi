-- Storage buckets
--   raw-sources : files exactly as downloaded / uploaded (private)
--   ee-exports  : CSV exports from the Earth Engine jobs (private)
--   releases    : frozen, versioned public data releases (public read)
insert into storage.buckets (id, name, public, file_size_limit)
values
  ('raw-sources', 'raw-sources', false, 524288000),
  ('ee-exports',  'ee-exports',  false, 104857600),
  ('releases',    'releases',    true,  524288000)
on conflict (id) do nothing;
