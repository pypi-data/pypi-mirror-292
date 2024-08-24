-- target: statute
-- is: mentioned
-- by: unique statute in the future
-- mentions: number of times such future statute refers to target
select
  base_ref.statute_id target,
	su1.statute_id id,
	(
		select
			v.text
		from
			statute_titles v
		where
			v.cat = 'serial'
			and v.statute_id = su1.statute_id
	) serial_title,
	(
		select
			v.text
		from
			statute_titles v
		where
			v.cat = 'official'
			and v.statute_id = su1.statute_id
	) official_title,
	(
		select
			v.text
		from
			statute_titles v
		where
			v.cat = 'short'
			and v.statute_id = su1.statute_id
	) short_title,
	su1.date,
	count(su1.statute_id) mentions
from
	statute_references base_ref
	join statute_units su1 on su1.id = base_ref.affector_statute_unit_id
	join statute_titles st on st.statute_id = su1.statute_id
group by
	su1.statute_id
order by
	su1.date desc, su1.statute_id
