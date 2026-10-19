WITH a(id) AS (VALUES (1),(2)),
     b(id) AS (VALUES (1))
SELECT a.id,b.id FROM a LEFT JOIN b ON a.id=b.id
ORDER BY a.id;
