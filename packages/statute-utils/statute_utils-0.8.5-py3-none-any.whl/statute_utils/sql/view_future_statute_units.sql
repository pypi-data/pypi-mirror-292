with future_mentions(units) AS (
	select
		json_group_array(
			json_object(
				"affector_locator",
				c.item,
				"affector_caption",
				-- can't use "caption" here for some reason, complains JSON_OBJECT must be TEXT
				c.caption,
				"affector_content",
				-- can't use "content" here for some reason, complains JSON_OBJECT must be TEXT
				c.content,
				"affector_material_path",
				c.material_path,
				"affector_statute_id",
				c.statute_id,
				"affector_statute",
				c.serial,
				"affector_statute_date",
				c.date
			)
			order by
				c.date desc
		)
	from
		cite_statute_in_statute_units c
	where
		target = s.id
),
interim_uniqs as (
	select
		su1.statute_id,
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
		count(su1.statute_id) num
	from
		statute_references sr1
		join statute_units su1 on su1.id = sr1.affector_statute_unit_id
		join statute_titles st on st.statute_id = su1.statute_id
	where
		sr1.statute_id = s.id
	group by
		su1.statute_id
	order by
		su1.date desc
),
uniq_statute_list(result) as (
	select
		json_group_array(
			json_object(
				'statute_id', i.statute_id, 'serial_title',
				i.serial_title, 'official_title',
				i.official_title, 'short_title',
				i.short_title, 'date', i.date, 'count',
				i.num
			)
			order by
				i.date desc
		)
	from
		interim_uniqs i
)
select
	s.id,
	(
		select
			result
		from
			uniq_statute_list
	) unique_statutes_list,
	(
		select
			json_array_length(result)
		from
			uniq_statute_list
	) unique_statutes_list_count,
	(
		select
			units
		from
			future_mentions
	) future_statute_units,
	(
		select
			json_array_length(units)
		from
			future_mentions
	) future_statute_units_count
from
	statutes s
where
	future_statute_units_count > 0
