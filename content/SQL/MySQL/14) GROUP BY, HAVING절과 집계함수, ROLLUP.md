---
title: GROUP BY, HAVING절과 집계함수, ROLLUP
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# 1. GROUP BY

GROUP BY는 이전(from, where) 결과셋을 지정된 컬럼의 값이 같은 행(Row)들을 하나의 그룹(Group)으로 묶어 계산셋을 만든 후 묶인 계산셋 그룹마다 평균, 합계, 개수 등의 집계함수(Aggregate Function)를 적용하여 조회하는 기능이다.

```sql
-- 테이블 생성
CREATE TABLE person(
	id int primary key,
	name varchar(50),
	gender char(1)
);
```

```sql
INSERT INTO person (id, name, gender) VALUES
(1, '김민수', 'M'),
(2, '이영희', 'F'),
(3, '박지훈', 'M'),
(4, '최수진', 'F'),
(5, '정우성', 'M'),
(6, '한지민', 'F'),
(7, '오세훈', 'M'),
(8, '윤아름', 'F'),
(9, '강동원', 'M'),
(10, '송지은', 'F');
```

```sql
select gender, count(*) -- 3 계산셋을 상대로 집계계산된  값을 조회 
from person -- 1 하나의 결과셋
group by gender; -- 2 F/M계산셋 2개가 생성됨
```

1) FROM 결과셋

![[14) GROUP BY, HAVING절과 집계함수, ROLLUP-1793595391708.webp]]

2) GROUP BY 계산셋 - 2개(F/M)

- 사킬라 스키마 film 테이블
![[14) GROUP BY, HAVING절과 집계함수, ROLLUP-1793595420824.webp]]

등급(rating)별 영화 개수를 조회하고 싶다면 rating 컬럼값이 같은 행들을 그룹으로 묶어 중간 계산셋 그룹을 만들고, 그룹마다 count()를 수행하면 된다.

```
PG 그룹
------------
A
B
count : 2

R 그룹
------------
C
D
count : 2

G 그룹
------------
E
count : 1
```

- from film 테이블 결과셋 -> rating 기준으로 그룹 계산셋 -> 각 그룹마다 COUNT 계산 -> 결과 출력
- 이때 select절에는 그룹(계산셋)에 대한 집계함수만 사용가능하다. 
- group by절에 사용된 컬럼명은 계산셋의 대표 컬럼값을 반환하는 집계함수라고 생각하면 된다. select절에 일반컬럼이 오면 error

```sql
SELECT rating, COUNT(*)
FROM film
GROUP BY rating;
```

# 2. GROUP BY 에서 많이 사용되는 집계 함수

GROUP BY절에 사용된 컬럼명, COUNT, SUM, AVG, MAX, MIN

```sql
SELECT rating,
       COUNT(*) AS 영화수
FROM film
GROUP BY rating;

SELECT rating,
       AVG(rental_rate) AS 평균대여료
FROM film
GROUP BY rating;

SELECT rating,
       SUM(length) AS 총상영시간
FROM film
GROUP BY rating;

SELECT rating,
       MAX(length) AS 최대길이
FROM film
GROUP BY rating;

SELECT rating,
       MIN(length) AS 최소길이
FROM film
GROUP BY rating;

SELECT rating,
       COUNT(*) AS 영화수,
       AVG(length) AS 평균길이,
       MAX(length) AS 최대길이,
       MIN(length) AS 최소길이
FROM film
GROUP BY rating;
```

**※ GROUP BY절 생략**

```sql
SELECT count(*) 
FROM film; -- 전체를 하나의 계산셋으로 생성후 집계하겠다 group by null 생략된 형태
```

# **3. GROUP BY 여러 컬럼**

from(조인) 절이 먼저 실행 되므로 JOIN 후 GROUP BY 실행

```sql
SELECT c.name,
       f.rating,
       COUNT(*)
FROM category c
JOIN film_category fc
ON c.category_id = fc.category_id
JOIN film f
ON fc.film_id = f.film_id
GROUP BY c.name, f.rating;
```

```
Action + PG
Action + R
Action + G
Comedy + PG
Comedy + R
...
```

- **R, G 영화만 그룹화**
from -> where -> group by 순

```sql
SELECT rating,
       COUNT(*)
FROM film
WHERE rating IN ('R', 'G')
GROUP BY rating;
```

# 4. HAVING

- 그룹을 만든 후 그룹(계산셋)에서 집계함수 결과값을 필터링한다.
- WHERE는 **그룹을 만들기 전에 행을 필터링한다.**
- HAVING은 **그룹을 만든 후 그룹의 집계함수결과를 필터링한다.**

```sql
-- 200개 이상만
SELECT rating,
       COUNT(*) AS cnt
FROM film
GROUP BY rating
HAVING COUNT(*) >= 200;

-- 평균 길이 120만
SELECT rating,
       AVG(length) AS avg_length
FROM film
WHERE rating <> 'R'
GROUP BY rating
HAVING AVG(length) >= 120;

-- DESC 정렬
SELECT rating, AVG(length) AS avg_length 
FROM film GROUP BY rating 
ORDER BY avg_length DESC;
```

# 5. 전체적인 순서

```sql
① FROM
      ↓
② WHERE
      ↓
③ GROUP BY - 행을 그룹으로 묶음
      ↓
④ 집계함수(그룹컬럼명, COUNT, AVG...) - 그룹별 계산 수행
      ↓
⑤ HAVING
      ↓
⑥ SELECT
      ↓
⑦ ORDER BY

※ 예외적으로 MySQL에서는 GROUP BY에 별칭 사용이 가능하지만, 표준 SQL에서는 별칭을 사용할 수 없다. 컬럼명을 사용하는 것이 권장된다.
```
```sql
-- 영화가 200편 이상인 등급
SELECT rating,
       COUNT(*) AS cnt
FROM film
GROUP BY rating
HAVING COUNT(*) >= 200;

-- 카테고리별 영화 수
SELECT c.name,
       COUNT(*) AS 영화수
FROM category c
JOIN film_category fc
ON c.category_id = fc.category_id
JOIN film f
ON fc.film_id = f.film_id
GROUP BY c.name
ORDER BY 영화수 DESC;

-- 카테고리별 평균 영화 길이
SELECT c.name,
       AVG(f.length) AS 평균길이
FROM category c
JOIN film_category fc
ON c.category_id = fc.category_id
JOIN film f
ON fc.film_id = f.film_id
GROUP BY c.name
ORDER BY 평균길이 DESC;

-- 영화가 60편 이상인 카테고리
SELECT c.name,
       COUNT(*) AS 영화수
FROM category c
JOIN film_category fc
ON c.category_id = fc.category_id
JOIN film f
ON fc.film_id = f.film_id
GROUP BY c.name
HAVING COUNT(*) >= 60
ORDER BY 영화수 DESC;
```

# 6. **GROUP BY확장 기능 - ROLL UP(MySQL은 현재 ROLLUP만 지원)**

ROLLUP은 GROUP BY 결과에 소계(Subtotal)와 총계(Grand Total)를 자동으로 추가하는 기능이다.

```sql
-- 고객id별 구매 카운트와 전체 구매 카운트를 같이 조회
select customer_id, count(*) from sales group by customer_id
union all
select "전체", count(*) from sales;

-- group by 확장 rollup 사용시
select customer_id, count(*)
from sales
group by rollup(customer_id);
```

```sql
-- 일반 GROUP BY
SELECT
    deptno,
    job,
    SUM(salary) AS total_salary
FROM employee
GROUP BY deptno, job;
```

![[14) GROUP BY, HAVING절과 집계함수, ROLLUP-1793596181417.webp]]

```sql
-- ROLLUP
SELECT
    deptno,
    job,
    SUM(salary) AS total_salary
FROM employee
GROUP BY ROLLUP(deptno, job);
```

![[14) GROUP BY, HAVING절과 집계함수, ROLLUP-1793596202191.webp]]

```sql
-- 결과가 보기 좋게 수정
SELECT
    IFNULL(CAST(deptno AS CHAR), '전체') AS 부서,
    IFNULL(job, '소계/총계') AS 직책,
    SUM(salary) AS 급여합계
FROM employee
GROUP BY ROLLUP(deptno, job);
```

![[14) GROUP BY, HAVING절과 집계함수, ROLLUP-1793596224053.webp]]