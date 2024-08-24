-- Each statute can be used as a component of a codification

with affected_codifications(codification) AS (
  SELECT
    json_object(
      'title',
      (
        SELECT
          title
        FROM
          codifications
        WHERE
          id = cs.codification_id
      ),
      'base_serial_title',
      (
        SELECT
          text
        FROM
          statute_titles
        WHERE
          statute_id = s.id
          AND cat = 'serial'
      ),
      'id',
      cs.codification_id,
      'date',
      (
        SELECT
          date
        FROM
          codifications
        WHERE
          id = cs.codification_id
      )
    ) codification
  FROM
    codification_statutes cs
  WHERE
    cs.statute_id = s.id
  GROUP BY
    cs.codification_id
  ORDER BY
    codification ->> '$.date' desc
),
collected_codifications(codifications) as (
  SELECT
    json_group_array(json(codification))
  FROM
    affected_codifications
)
SELECT
  s.id,
  (
    SELECT
      codifications
    FROM
      collected_codifications
  ) affected_codifications,
  (
    SELECT
      json_array_length(codifications)
    FROM
      collected_codifications
  ) affected_codifications_count
from statutes s
where affected_codifications_count > 0
