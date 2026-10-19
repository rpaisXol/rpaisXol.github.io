WITH x(v) AS (VALUES (1),(2)),
     y(v) AS (SELECT v*2 FROM x)
SELECT SUM(v) FROM y;
