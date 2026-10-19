-- Oracle 19c 참고. 00_setup.sql 후 실행. 서버 실행 미검증.
-- ROLLUP 한 열: 부서별 4그룹 + 전체합계 1그룹.
SELECT dept_id,GROUPING(dept_id) AS is_total,SUM(salary) AS total
FROM emp GROUP BY ROLLUP(dept_id)
ORDER BY GROUPING(dept_id),dept_id NULLS LAST;
-- 실제 NULL 부서 E는 is_total=0이고 5000.
-- 전체 합계는 is_total=1이고 11000.
SELECT dept_id,manager_id,SUM(salary)
FROM emp GROUP BY CUBE(dept_id,manager_id);
-- 원문에서 순서는 보장하지 않음. 조합은 (부서,관리자),(부서),(관리자),().
SELECT dept_id,manager_id,SUM(salary)
FROM emp GROUP BY GROUPING SETS((dept_id),(manager_id),());
