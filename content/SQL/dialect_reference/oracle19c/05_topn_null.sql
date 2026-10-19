-- Oracle 19c 참고. 00_setup.sql 후 실행. 서버 실행 미검증.
SELECT id,salary FROM emp WHERE salary IS NOT NULL
ORDER BY salary DESC,id FETCH FIRST 2 ROWS ONLY;
-- E(5,5000), D(4,2000).
SELECT id,salary FROM
 (SELECT id,salary FROM emp WHERE salary IS NOT NULL ORDER BY salary DESC,id)
WHERE ROWNUM<=2;
-- 안쪽에서 정렬한 뒤 바깥 ROWNUM으로 선택.
SELECT NVL(NULL,0),COALESCE(NULL,0,5) FROM dual;
-- 0,0. Oracle 빈 문자열은 NULL 취급에 주의.
