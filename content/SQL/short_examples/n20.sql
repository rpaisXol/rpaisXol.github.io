WITH a(id) AS (VALUES (1),(2)),
     b(id) AS (VALUES (1),(1))
SELECT a.id,b.id FROM a JOIN b ON a.id=b.id;
