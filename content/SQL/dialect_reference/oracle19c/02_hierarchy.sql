-- Oracle 19c 참고. 00_setup.sql 후 실행. 서버 실행 미검증.
SELECT id,name,LEVEL AS depth FROM emp
START WITH manager_id IS NULL
CONNECT BY NOCYCLE PRIOR id=manager_id
ORDER SIBLINGS BY id;
-- 루트 A,E. B,C,F는 A 아래, D는 C 아래. 깊이는 1,2,3.
