---
title: 19. Recursive CTE(WITH 테이블)를 사용한 계층형 데이터
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug: sqld-concept-n14
---
# **1. 계층형 조회**

- Recursive CTE는 자기 자신을 계속 참조하면서 계층형 데이터나 반복적인 데이터를 조회하는 기능이다.

- 주로 조직도, 게시판 댓글, 카테고리, 폴더 구조, BOM(부품 구조), 날짜 생성 등에 사용한다.

- Oracle RDBMS는 CONNECT BY라는 계층형(Hierarchical) 조회 문법을 지원한다. 반면 MySQL 8.0은 CONNECT BY를 지원하지 않고 **Recursive CTE(재귀 CTE : WITH문)**를 사용하여 같은 기능을 구현한다.

# 2. 계층형 데이터 조회 실습

**1) 계층형 데이터 만들기 - DDL**

```sql
CREATE TABLE emp (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(30) NOT NULL,
    manager_id INT NULL,
    FOREIGN KEY (manager_id) REFERENCES emp(emp_id)
);
​
```

**2) 조직도**

```text
CEO
├── 영업본부장
│   ├── 영업팀장
│   └── 해외영업팀장
│
├── 개발본부장
│   ├── 백엔드팀장
│   │      └── 신입사원A
│   │
│   └── 프론트팀장
│          └── 신입사원B
│
└── 관리본부장
     └── 인사팀장
```

**3) 조직도를 참조하여 데이터를 계층적으로 입력**

```sql
INSERT INTO emp VALUES
(1, 'CEO', NULL),

(2, '영업본부장', 1),
(3, '개발본부장', 1),
(4, '관리본부장', 1),

(5, '영업팀장', 2),
(6, '해외영업팀장', 2),

(7, '백엔드팀장', 3),
(8, '프론트팀장', 3),

(9, '인사팀장', 4),

(10, '신입사원A', 7),
(11, '신입사원B', 8);
```

# **3. Recursive CTE 기본 문법**

- 위 조직도 세로 순서대로 정렬한다는 것은 전체데이터 상대로는 불가능하다. 한행 한행씩 개별적으로 찾아서 이어 붙이는 방식을 사용해야한다 -> 첫행 조회 후 다음행을 찾기위해서 조인하고, 다음 행 찾기 위해서 조인,....마지막 행이 조회 될때 까지 -> 재귀조회가 된다.

- WITH RECURSIVE는 **자기 자신을 참조하는 CTE**를 만든다.

- **Anchor Query**(시작 데이터)와 **Recursive Query**(반복 조회)를 UNION ALL로 연결한다.

- 재귀는 **새로운 행이 더 이상 생성되지 않으면 자동 종료**된다.

- 계층 구조뿐 아니라 **숫자 생성, 날짜 생성, 누락 데이터 보완** 등 다양한 반복 처리에도 활용할 수 있다.

```sql
WITH RECURSIVE CTE이름 AS
(
    -- 시작 데이터 (Anchor)

    UNION ALL

    -- 재귀 조회 (Recursive)
)

SELECT *
FROM CTE이름;
```

**1) CEO부터 모든 직원 조회**

```sql
WITH RECURSIVE emp_tree AS
(
    -- 시작점
    SELECT
        emp_id,
        emp_name,
        manager_id,
        1 AS level -- 시작 행(ROOT)의 레벨값은 1
    FROM emp
    WHERE manager_id IS NULL -- 시작 행(ROOT)의 조건

    UNION ALL

    -- 하위 직원 계속 찾기, 끝날때 까지 재귀(자기 자신을 이용해서 같은 작업을 반복) 호출
    SELECT
        e.emp_id,
        e.emp_name,
        e.manager_id,
        t.level + 1
    FROM emp e INNER JOIN emp_tree t
         ON e.manager_id = t.emp_id
)

SELECT *
FROM emp_tree;
```

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793755886363.webp]]

**2) 조직도 형태로 조회**

```sql
WITH RECURSIVE emp_tree AS
(
    SELECT
        emp_id,
        emp_name,
        manager_id,
        1 level
    FROM emp
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.emp_id,
        e.emp_name,
        e.manager_id,
        t.level + 1
    FROM emp e
    JOIN emp_tree t
      ON e.manager_id=t.emp_id
)

SELECT
    CONCAT(REPEAT('    ', level-1), emp_name) AS organization
FROM emp_tree;
```

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793755902651.webp]]

**3) 전체 계층 경로(Path)를 같이 조회**

```sql
WITH RECURSIVE emp_tree AS
(
    SELECT
        emp_id,
        emp_name,
        manager_id,
        emp_name AS path
    FROM emp
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.emp_id,
        e.emp_name,
        e.manager_id,
        CONCAT(t.path,' > ',e.emp_name)
    FROM emp e
    JOIN emp_tree t
      ON e.manager_id=t.emp_id
)

SELECT *
FROM emp_tree;
```

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793755927812.webp]]

**4) 특정 직원의 모든 부하직원 조회**

```sql
WITH RECURSIVE emp_tree AS
(
    SELECT *
    FROM emp
    WHERE emp_name='개발본부장'

    UNION ALL

    SELECT e.*
    FROM emp e
    JOIN emp_tree t
      ON e.manager_id=t.emp_id
)

SELECT *
FROM emp_tree;
```

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793755953679.webp]]

**5) 1~10까지 숫자 생성**

```sql
WITH RECURSIVE numbers AS
(
    SELECT 1 AS num

    UNION ALL

    SELECT num+1
    FROM numbers
    WHERE num<10
)

SELECT *
FROM numbers;
```

**6) 날짜 생성**

```sql
WITH RECURSIVE dates AS
(
    SELECT DATE('2026-07-01') dt

    UNION ALL

    SELECT DATE_ADD(dt, INTERVAL 1 DAY)
    FROM dates
    WHERE dt<'2026-07-10'
)

SELECT *
FROM dates;
```

**문제) 토/일 공휴일 제외한 26년 10월 달력 조회, 요일포함(월화수목금)**

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793756039016.webp]]

```sql
with recursive m10 as (
	select date('2026-10-01') d
    union all
    select date_add(d, interval 1 day)
    from m10
    where d < '2026-10-31'
), 
holiday as (
	select date('2026-10-05') d, '개천절 대체공휴일' title
    union all
    select date('2026-10-09') d, '한글날' title
),
work_m10 as (
	select d, 
		case weekday(d) 
			when 0 then '월'
            when 1 then '화'
            when 2 then '수'
            when 3 then '목'
            when 4 then '금'
		end 요일
	from m10
	where weekday(d) < 5

	except

	select d, 
			case weekday(d) 
				when 0 then '월'
				when 1 then '화'
				when 2 then '수'
				when 3 then '목'
				when 4 then '금'
			end 요일
	from holiday
)

select *,
		concat(count(*) over(),'일') 공휴일제외
from work_m10;
```

![[19) Recursive CTE(WITH 테이블)를 사용한 계층형 데이터-1793756057244.webp]]