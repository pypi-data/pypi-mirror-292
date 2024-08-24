select
  s.id target,
  c.id,
  json_group_array(
    json_object(
      'id',
      cs.statute_id,
      'date',
      cs.date,
      'subtitle',
      (
        select
          text
        from
          statute_titles
        where
          statute_id = cs.statute_id
          and cat = 'serial'
      ),
      'title',
      (
        ifnull(
          (
            select
              text
            from
              statute_titles
            where
              statute_id = cs.statute_id
              and cat = 'short'
          ),
          (
            select
              text
            from
              statute_titles
            where
              statute_id = cs.statute_id
              and cat = 'official'
          )
        )
      )
    ) order by cs.date desc
  ) components
from
  codification_statutes cs
  join codifications c on c.id = cs.codification_id
  join statutes s on s.cat = c.cat
  and s.num = c.num
group by
  c.id
