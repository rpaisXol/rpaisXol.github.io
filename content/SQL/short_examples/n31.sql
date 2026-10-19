WITH e(id,mgr) AS (VALUES (1,NULL),(2,1))
SELECT x.id,m.id FROM e x LEFT JOIN e m ON x.mgr=m.id
ORDER BY x.id;
