-- Statute titles can be used to detect future references. This is a precursor to generating the statute_references table.

with fts_expr as (
	select -- Each statute contains different names, combine them into an fts expression
		group_concat(' "' || text || '" ', 'OR') q
	from
		statute_titles
	where
		(
			cat = 'serial'
			or cat = 'short'
			or cat = 'alias'
		)
		and statute_id = s.id
		and length(text) > 10
		and length(text) < 100
),
-- Look for statutory units mentioning target statute via fts
matched_row_ids(id) as (
	select
		rowid
	from
		statute_units_fts(
			(
				select
					q
				from
					fts_expr
			)
		)
),
-- List statute units that affect the target statute
affecting_units(ids) as (
	select
		su.id
	from
		statute_units su
		join statutes s1 on s1.id = su.statute_id
	where
		su.rowid in (
			select
				id
			from
				matched_row_ids
		)
		and su.statute_id != s.id
		and su.material_path != "1."
		and s1.date > s.date
) -- List each target statute (except for acts)
select
	s.id,
	(
		select
			group_concat(ids,",")
		from
			affecting_units
	) unit_ids
from
	statutes s
where
	s.cat != "act" and unit_ids is not null
