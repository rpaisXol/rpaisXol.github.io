-- Oracle 19c 문법 형태 참고. 자동 실행하지 마세요.
-- 기존 사용자를 가정한 권한 명령입니다. 이 자료는 계정 생성이나 권한 변경을 실행하지 않습니다.
-- GRANT SELECT ON emp TO learner;
-- REVOKE SELECT ON emp FROM learner;
-- MERGE 원리: 소스와 대상 키를 연결하고 MATCHED/NOT MATCHED 분기를 구분.
-- 실제 학습 스키마의 EMP에서만 검토할 변경 예제입니다.
MERGE INTO emp e
USING (SELECT 2 AS id,1600 AS salary FROM dual) s
ON (e.id=s.id)
WHEN MATCHED THEN UPDATE SET e.salary=s.salary;
-- B의 salary를1600으로 변경. 실행 전 트랜잭션과 대상 확인.
ROLLBACK;
