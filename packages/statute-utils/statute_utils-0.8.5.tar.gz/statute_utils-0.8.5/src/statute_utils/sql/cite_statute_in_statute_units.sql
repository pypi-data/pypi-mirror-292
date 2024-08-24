-- target: statute
-- is: mentioned
-- by: statute units in the future
select
	sr.statute_id target,
  su.id,
	su.item,
	su.caption,
	su.content,
	su.material_path,
	su.statute_id,
	st.text serial,
	su.date
from
	statute_references sr
	join statute_units su on su.id = sr.affector_statute_unit_id
	join statute_titles st on st.statute_id = su.statute_id and st.cat = 'serial'
ORDER BY
	target desc, su.date desc
