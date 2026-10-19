-- Oracle 19c 참고. 00_setup.sql 후 실행. 서버 실행 미검증.
SELECT sales,dev FROM
 (SELECT dept_id,salary FROM emp)
PIVOT(SUM(salary) FOR dept_id IN(10 AS sales,20 AS dev));
-- 한 행: SALES=2500, DEV=3500.
SELECT dept_name,amount FROM
 (SELECT 2500 AS sales,3500 AS dev FROM dual)
UNPIVOT(amount FOR dept_name IN(sales AS 'Sales',dev AS 'Dev'))
ORDER BY dept_name;
-- Dev 3500 / Sales 2500. 기본 UNPIVOT은 NULL을 제외.
