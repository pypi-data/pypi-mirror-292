-- target: statute
-- is: a component of
-- by: codifications
select
	cs.statute_id target,
	c.id,
	c.title,
	(
		select
			text
		from
			statute_titles
		where
			cat = 'serial'
			and statute_id = s.id
	) serial,
	(
		select
			text
		from
			statute_titles
		where
			cat = 'official'
			and statute_id = s.id
	) official,
  c.date
from
	codification_statutes cs
	join codifications c on c.id = cs.codification_id
	join statutes s on s.cat = c.cat
	and s.num = c.num
group by cs.statute_id, cs.codification_id
