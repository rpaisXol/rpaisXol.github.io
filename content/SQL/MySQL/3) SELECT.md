---
title: SELECT
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# **공식문서에서 제공하는 SELECT문 사용 방법**

[https://dev.mysql.com/doc/refman/8.4/en/select.html](https://dev.mysql.com/doc/refman/8.4/en/select.html)

```
SELECT
    [ALL | DISTINCT | DISTINCTROW ]
    [HIGH_PRIORITY]
    [STRAIGHT_JOIN]
    [SQL_SMALL_RESULT] [SQL_BIG_RESULT] [SQL_BUFFER_RESULT]
    [SQL_NO_CACHE] [SQL_CALC_FOUND_ROWS]
    select_expr [, select_expr] ...
    [into_option]
    [FROM table_references
      [PARTITION partition_list]]
    [WHERE where_condition]
    [GROUP BY [ {col_name | expr | position}, ... [WITH ROLLUP]
              | ROLLUP ({col_name | expr | position}, ...)] ]
    [HAVING where_condition]
    [WINDOW window_name AS (window_spec)
        [, window_name AS (window_spec)] ...]
    [ORDER BY {col_name | expr | position}
      [ASC | DESC], ... [WITH ROLLUP]]
    [LIMIT {[offset,] row_count | row_count OFFSET offset}]
    [into_option]
    [FOR {UPDATE | SHARE}
        [OF tbl_name [, tbl_name] ...]
        [NOWAIT | SKIP LOCKED]
      | LOCK IN SHARE MODE]
    [into_option]

into_option: {
    INTO OUTFILE 'file_name'
        [CHARACTER SET charset_name]
        export_options
  | INTO DUMPFILE 'file_name'
  | INTO var_name [, var_name] ...
}

export_options:
    [{FIELDS | COLUMNS}
        [TERMINATED BY 'string']
        [[OPTIONALLY] ENCLOSED BY 'char']
        [ESCAPED BY 'char']
    ]
    [LINES
        [STARTING BY 'string']
        [TERMINATED BY 'string']
    ]
```

간단하게 하면
```
SELECT 열
FROM DB.테이블 -- DB이름은 생략 가능
WHERE 조건
ORDER BY 열
```

- select문은 select절, from절, where절, order by절로 구성된다.
- 실행순서는 from절 -> where절 -> select절 -> order by절 -> LIMIT 절 순서이다.
- (전체데이터셋 - 행데이터셋 - 열데이터셋 - 정렬순 - Ton N)

```
-- SELECT 문(SQL 전체) --

SELECT name, price      -- SELECT절
FROM product            -- FROM절
WHERE price >= 10000    -- WHERE절
ORDER BY price DESC    -- ORDER BY절
LIMIT 10;
```
## 1. 테이블의 열정보 확인

show columns from customer;
### 1-1. SELECT 절

- 하나의 열 조회
```
select first_name
from customer
limit 10;
```

- 2개이상의 열 조회, 순서는 상관 없다.
```
select first_name, last_name
from customer
limit 10;

-- 조회 순서는 원본 순서와 상관 없다
select last_name, last_name
from customer
limit 10;
```

- 전체 열 조회
```
select *
from customer
limit 10;
```

- **DISTINCT** 연산자 : SELECT한 결과에서 중복된 행을 제거하고 고유한 값만 조회하는 연산자이다. select절이 실행 후 다음에 실행된다.

```
SELECT DISTINCT 컬럼명
FROM 테이블명;

SELECT DISTINCT 컬럼명, 컬럼명
FROM 테이블명;
```

예)
```
SELECT DISTINCT store_id
FROM customer;

SELECT distinct store_id, active
FROM customer;
-- from -> where -> select -> distinct -> order by -> limit

-- 주의 : DISTINCT는 각 컬럼을 따로 중복 제거하는 것이 아니라, SELECT한 컬럼들의 조합 전체를 기준으로 중복을 제거한다.
SELECT DISTINCT first_name
FROM customer
ORDER BY first_name;
```

### 1-2. **WHERE 절 : 특정행에 연산 비교/논리 연산 후 "참" 인 행만 필터링**

```
SELECT 열 
FROM 테이블
WHERE 열값 비교/논리 연산
```

**1) 비교 연산**(숫자, 문자, 날짜등에 사용 가능하지만 대부분은 숫자데이터 컬럼값 비교에 많이 사용된다)

```
<, <=, =, >, >=, <>, !=, !<, !>
```

```
select film_id, title, length
from film
where length <= 50;

select film_id, title, length
from film
where length = 50;

select film_id, title, length
from film
where length <> 50
limit 10;

-- 같은 연산
select film_id, title, length
from film
where length != 50
limit 10;
```

```
-- 문자값도 가능
select film_id, title, length
from film
where length <> 50
limit 10;

-- 같은 연산
select film_id, title, length
from film
where length != 50
limit 10;
```

```
select first_name, create_date
from customer
where create_date < '2006-02-14 22:04:37';
```

**2) 논리 연산**

![[3) SELECT-1793166962089.webp]]

```
SELECT *
FROM customer
WHERE active = 1
AND store_id = 1;

SELECT *
FROM customer
WHERE store_id = 1
OR store_id = 2;

SELECT *
FROM customer
WHERE NOT active = 1;

SELECT *
FROM customer
WHERE active <> 1;

SELECT *
FROM customer
WHERE first_name IN ('MARY', 'PATRICIA', 'LINDA');

-- IN 연산자 결과와 동일
SELECT *
FROM customer
WHERE first_name = 'MARY'
OR first_name = 'PATRICIA' 
OR first_name = 'LINDA'

SELECT *
FROM customer
WHERE first_name NOT IN ('MARY', 'PATRICIA');

SELECT *
FROM customer
WHERE customer_id BETWEEN 10 AND 20; -- 10(포함)~20(포함)

-- BETWEEN 연산자 결과와 동일
SELECT *
FROM customer
WHERE customer_id >= 10 AND customer_id <= 20; 

SELECT *
FROM customer
WHERE customer_id NOT BETWEEN 10 AND 20;

SELECT *
FROM customer
WHERE first_name LIKE 'A%'; -- 대문자 A로 시작하는

SELECT *
FROM customer
WHERE first_name LIKE '%A'; -- 대문자 A로 끝나는

SELECT *
FROM customer
WHERE first_name LIKE '%AR%'; -- 대문자 AR을 포함, 주의) MySQL 소문자까지 조회 된다.

SELECT *
FROM customer
WHERE first_name LIKE '_AR_';

SELECT *
FROM customer
WHERE first_name NOT LIKE 'A%'; -- 대문자 A로 시작하지 않는

SELECT *
FROM customer
WHERE email IS NULL; -- NULL값은 NULL 전용 연산자사용. email에 NULL값이 없으면 빈 결과셋 반환

SELECT *
FROM customer
WHERE email IS NOT NULL;

SELECT *
FROM customer
WHERE (first_name = 'MARY' OR store_id = 1) AND active = 1 ;
-- ()가 없으면 AND가 먼저 실행 OR는 마지막에 실행

SELECT *
FROM customer
WHERE NOT first_name LIKE 'A%';

SELECT *
FROM customer
WHERE active = 1
AND store_id IN (1, 2)
AND first_name LIKE 'M%'
AND customer_id BETWEEN 100 AND 300;
```
**※ 연산자 우선순위**
- SQL에서는 다음 순서로 조건을 계산한다.
- () (괄호) -> NOT -> AND -> OR
- AND와 OR를 함께 사용할 때는 괄호 ()를 사용하는 것이 가장 좋은 습관이다.

```
SELECT *
FROM customer
WHERE active = 1
OR (store_id = 1 AND first_name = 'MARY');
```

## 1-3 ORDER BY절 / LIMIT절

**1. ORDER BY절**
```
SELECT 열
FROM 테이블
WHERE 열 조건
ORDER BY 열 ASC 또는 DESC
```

```
SELECT *
FROM customer
ORDER BY customer_id;

SELECT *
FROM customer
ORDER BY customer_id ASC;

SELECT *
FROM customer
ORDER BY customer_id DESC;

-- 문자 값으로 정렬가능
SELECT *
FROM customer
ORDER BY first_name;

-- 날짜 값으로 정렬가능
SELECT *
FROM customer
ORDER BY create_date;

SELECT *
FROM customer
ORDER BY last_name, first_name;

SELECT *
FROM customer
ORDER BY store_id ASC, customer_id DESC;

-- 최근 등록된 고객 순으로
SELECT *
FROM customer
ORDER BY create_date DESC;
```

**2. LIMIT : 상위 N개의 데이터만 조회, OFFSET 특정 구간의 상위 N개 조회**

```
SELECT *
FROM customer
LIMIT 5;

SELECT *
FROM customer
LIMIT 10;

-- LIMIT절은 항상 ORDER BY절과 함꼐 사용하는 것이 좋다
SELECT *
FROM customer
ORDER BY create_date DESC 
LIMIT 10; -- 제일 마지막에 실행

SELECT *
FROM customer
ORDER BY customer_id
LIMIT 10, 5; -- 0~9행 10개 건너뛰고 5개 출력

-- 같은 표현(OFFSET 키워드 사용)
SELECT *
FROM customer
ORDER BY customer_id
LIMIT 5 OFFSET 10;

SELECT *
FROM customer
WHERE active = 1
ORDER BY customer_id
LIMIT 10;

SELECT *
FROM customer
WHERE first_name LIKE 'A%'
ORDER BY first_name
LIMIT 3;
```

※ 페이징(Pagination) 예제
* OFFSET 사이즈를 1씩 키우면 "슬아이딩 원도우 알고리즘"
* OFFSET 사이즈를 사이즈 크기만큼 키우면 " 페이징 알고리즘"

1페이지

```
SELECT *
FROM customer
ORDER BY customer_id
LIMIT 10 OFFSET 0; 
-- 페이지 사이즈가 10이라면 OFFSET 숫자 패턴은 "(현재페이지 
-- 1) * 페이지사이즈"
```

2페이지

```
SELECT *
FROM customer
ORDER BY customer_id
LIMIT 10 OFFSET 10;
```

3페이지

```
SELECT *
FROM customer
ORDER BY customer_id
LIMIT 10 OFFSET 20;
```

