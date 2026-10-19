-- Oracle 19c 참고. 서버 실행 미검증. 초기 표 불필요.
SELECT CASE WHEN REGEXP_LIKE('A123','^[A-Z][0-9]+$')
 THEN 'MATCH' ELSE 'NO' END AS result FROM dual;
-- 결과 MATCH: 영문 대문자 하나 + 숫자 하나 이상, 전체 문자열 일치.
SELECT REGEXP_SUBSTR('A12 B3','[0-9]+',1,2) AS n FROM dual;
-- 결과 문자열 3: 두 번째 숫자 구간.
