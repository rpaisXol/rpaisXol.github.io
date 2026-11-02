---
title: SELF JOIN
created: 2026-10-19
updated: 2026-10-19
tags:
note_type: concept-guide
slug: sqld-concept-n42
---
# SELF JOIN

**Self Join(셀프 조인)**은 **하나의 테이블을 자기 자신과 조인하는 것**이다.
주로 **같은 테이블 안에 서로 연관된 데이터를 조회**할 때 사용한다.

# **1. test 스키마(데이터베이스)에 샘플 테이블 생성**

- emp_id : 직원번호(PK)
- emp_name : 직원명
- manager_id : 자신의 관리자의 직원번호(FK 역할) manager_id에는 **같은 테이블의 emp_id**가 저장된다.

employee 테이블 안에서 manager_id → emp_id를 참조한다.
```
INSERT INTO employee VALUES
(1, '김부장', NULL),
(2, '이과장', 1),
(3, '박대리', 2),
(4, '최사원', 2),
(5, '정사원', 3),
(6, '한인턴', 4);
```

# 2. SELF LEFT JOIN

```
SELECT e.emp_name AS 직원,
       m.emp_name AS 관리자
 -- 같은 테이블을 두 번 사용하므로 별칭(alias)을 붙인다.
FROM employee e
LEFT JOIN employee m
ON e.manager_id = m.emp_id;
```

![[13) SELF JOIN-1793595144531.webp]]

# 3. SELF INNER JOIN

```
SELECT e.emp_name AS 직원,
       m.emp_name AS 관리자
FROM employee e
INNER JOIN employee m
ON e.manager_id = m.emp_id;
```

![[13) SELF JOIN-1793595169923.webp]]

```
select * 
from student s1 cross join student s2
where s1.student_name <> s2.student_name;
```