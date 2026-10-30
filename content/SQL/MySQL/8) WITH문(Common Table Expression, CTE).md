---
title: WITH문(Common Table Expression, CTE)
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
- WITH문(Common Table Expression, **CTE**)은 **SELECT의 결과셋에 이름을 붙인 후, 그 결과를 바로 아래 SELECT에서 사용하는 문법**이다.
-  **SELECT 결과셋도 테이블**과 같은 역할을 한다 -> 가상의 테이블

```
WITH 이름 AS (
    SELECT ...
)
SELECT *
FROM 이름;
```

**- WITH를 사용하는 이유**
1) 가독성이 좋아진다.
2) 같은 결과를 여러 번 사용할 수 있다.
3) 복잡한 SQL을 단계별로 작성할 수 있다.

```
--  film테이블에서 title, rental_rate 컬럼만을 가진 가상의 테이블
WITH movie AS (
    SELECT title, rental_rate
    FROM film
)
SELECT *
FROM movie;

-- rental_rate가 4 이상인 영화의 title, rental_rate 컬럼만을 가진 가상의 테이블
WITH expensive_movie AS (
    SELECT title, rental_rate
    FROM film
    WHERE rental_rate >= 4
)
SELECT *
FROM expensive_movie;

-- 영화 길이가 120분 이상
WITH long_movie AS (
    SELECT title, length
    FROM film
    WHERE length >= 120
)
SELECT *
FROM long_movie
ORDER BY length DESC;

-- 배우의 풀네임을 가진 가상의 테이블
WITH actor_name AS (
    SELECT
        actor_id,
        CONCAT(first_name, ' ', last_name) AS full_name
    FROM actor
)
SELECT *
FROM actor_name
ORDER BY full_name;

-- 특정 등급만을 모아둔 가상의 테이블
WITH movie AS (
    SELECT
        title,
        rating
    FROM film
)
SELECT *
FROM movie
WHERE rating = 'PG';
```
