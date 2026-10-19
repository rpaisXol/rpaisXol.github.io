# Oracle 19c 참고 SQL

SQLite 자동 검사 대상이 아닙니다. 공식 문법을 참고하여 작성했으며 Oracle 서버 실행 검증은 하지 않았습니다. 빈 학습 스키마에서 00_setup.sql을 최초 한 번 실행한 뒤 파일별 설명을 따르세요. 같은 이름의 기존 표가 있으면 초기화는 실패하며 기존 표를 삭제하지 않습니다.

- 그룹 소계: 실제 NULL 부서와 합계 NULL을 GROUPING으로 구분
- 계층형: PRIOR는 부모 행, LEVEL은 깊이
- PIVOT·UNPIVOT: 집계 대상 열과 기본 NULL 제외
- 정규식: 시작과 끝 경계, 반복 수
- Top N: 정렬 전후 ROWNUM 차이
- 권한·MERGE: 권한문은 주석 예시, MERGE는 학습용 수정 후 ROLLBACK
