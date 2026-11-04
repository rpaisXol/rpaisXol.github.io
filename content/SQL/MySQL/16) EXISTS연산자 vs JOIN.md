---
title:
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
※ WHERE절 서브쿼리에 자주 사용되는 연산자, 서브쿼리의 결과 개수는 행의 수(열의 수는 상관 없음. 여러 열이라도 하나의 행을 하나의 결과값으로 처리)

![[16) EXISTS연산자 vs JOIN-1793752708132.webp]]
# **1. = (같다)**

서브쿼리가 하나의 값만 반환할 때 사용
예) 평균 대여료와 같은 영화 조회]

```sql
SELECT title, rental_rate 
FROM film 
WHERE rental_rate = 
( 
	SELECT AVG(rental_rate) 
	FROM film 
);
```

# 2. >, <, >=, <=

서브쿼리가 하나의 값만 반환할 때 사용
예) 평균보다 대여료가 높은 영화

```sql
SELECT title, rental_rate 
FROM film 
WHERE rental_rate > 
( 
	SELECT AVG(rental_rate) 
	FROM film 
);
```

# **3. IN**

서브쿼리가 여러 개의 값을 반환할 때 사용
예) Action 또는 Comedy 장르 조회

```sql
SELECT film_id, category_id 
FROM film_category 
WHERE category_id IN 
( -- 서브쿼리의 결과셋이 2행이상 
	SELECT category_id 
	FROM category 
	WHERE name IN ('Action', 'Comedy') 
); 

SELECT category_id 
FROM category 
WHERE name IN ('Action', 'Comedy');
```

# **4. NOT IN**

서브쿼리 결과에 없는 데이터 조회
예) Action, Comedy를 제외한 장르가 조회

```sql
SELECT film_id, category_id
FROM film_category 
WHERE category_id NOT IN
( -- 서브쿼리의 결과셋이 2행이상
    SELECT category_id
    FROM category
    WHERE name IN ('Action', 'Comedy')
);


SELECT category_id
    FROM category
    WHERE name IN ('Action', 'Comedy');
```

# **5. EXISTS : 메인쿼리와 서브쿼리간에 조인이 발생** **INNER JOIN 과 비슷**

서브쿼리 결과가 하나라도 존재하면 TRUE(메인쿼리와 조인 발생)
예) 영화가 하나 이상 등록된 장르만 조회

```sql
SELECT name
FROM category c
WHERE EXISTS
(
    SELECT *
    FROM film_category fc
    WHERE fc.category_id = c.category_id
);
```

# **6. NOT EXISTS : 메인쿼리와 서브쿼리간에** **LEFT JOIN - INNER JOIN(차집합: EXCEPT)과 비슷**

서브쿼리 결과가 없으면 TRUE
예) 영화가 하나도 없는 장르 조회

```sql
SELECT name
FROM category c
WHERE NOT EXISTS
(
    SELECT *
    FROM film_category fc
    WHERE fc.category_id = c.category_id
);
```

다음과 결과는 동일

```sql
SELECT c.*
FROM category c LEFT JOIN film_category fc
	ON fc.category_id = c.category_id

EXCEPT -- 차집합

SELECT c.*
FROM category c INNER JOIN film_category fc
	ON fc.category_id = c.category_id;
```

# 7. INNER JOIN의 목적

**관련된 데이터를 함께 조회하는 것**
예를 들어 영화와 장르를 함께 출력하려면 JOIN이 필요하다. 
-> 영화 제목과 장르 이름을 모두 출력해야 하므로 **JOIN**을 사용한다.

```sql
SELECT f.title, c.name
FROM film f
INNER JOIN film_category fc
    ON f.film_id = fc.film_id
INNER JOIN category c
    ON fc.category_id = c.category_id;
```

# **8. EXISTS의 목적**

**메인쿼리와 서브쿼리간에 조인 발생. 관련 데이터가 존재하는지만 확인하는 것**
예를 들어 영화가 하나라도 등록된 장르만 조회한다. -> 영화 제목은 필요 없다.

```sql
SELECT c.name
FROM category c
WHERE EXISTS (
    SELECT *
    FROM film_category fc
    WHERE fc.category_id = c.category_id
);
```

# **9. 같은 결과가 나오는 경우**

```sql
SELECT DISTINCT c.name
FROM category c
INNER JOIN film_category fc
ON c.category_id = fc.category_id;
```

```sql
SELECT c.name
FROM category c
WHERE EXISTS (
    SELECT *
    FROM film_category fc
    WHERE fc.category_id = c.category_id
);
```

**그런데 JOIN은 중복이 생긴다. 영화가 3편이면 Action도 3번 나온다. 그래서 DISTINCT를 추가해야 한다.**

```sql
SELECT DISTINCT c.name ...
```

# **10. NOT EXISTS 와 JOIN**

category는 있고 영화는 없다.

```sql
SELECT c.name
FROM category c
WHERE NOT EXISTS (
    SELECT *
    FROM film_category fc
    WHERE fc.category_id = c.category_id
);

SELECT c.name
FROM category c
LEFT JOIN film_category fc
ON c.category_id = fc.category_id
WHERE fc.category_id IS NULL;
```

1. 언제 JOIN을 사용할까?
- 다른 테이블의 컬럼을 출력해야 할 때
- 영화 제목 + 장르 이름 학생 이름 + 출석 날짜 회원 이름 + 주문 금액 → JOIN

1. 언제 EXISTS를 사용할까?
- 존재 여부만 확인할 때
- 영화가 있는 장르인가? 주문한 회원인가? 출석 기록이 있는 학생인가? 리뷰가 있는 상품인가? → EXISTS

1. 언제 NOT EXISTS를 사용할까?
- 관련 데이터가 없는 경우를 찾을 때
- 영화가 없는 장르 주문하지 않은 회원 출석하지 않은 학생 리뷰가 없는 상품 → NOT EXISTS

![[16) EXISTS연산자 vs JOIN-1793753437446.webp]]