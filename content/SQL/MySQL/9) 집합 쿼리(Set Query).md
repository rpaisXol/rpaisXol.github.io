---
title: 집합 쿼리(Set Query)
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
**집합 쿼리(Set Query)**는 두 개 이상의 SELECT 결과를 하나의 결과로 합치는 쿼리이다.

각 SELECT문의 **컬럼 개수와 데이터 타입이 서로 호환**되어야 한다.(컬럼의 이름이 같지 않아도 데이터 타입만 호환되면 연산이 된다. 결과셋의 컬럼 이름은 첫번째 테이블의 이름으로 조회된다)

![[9) 집합 쿼리(Set Query)-1793353163955.webp]]

# 1. UNION

중복을 제거하여 합친다. 

``` 
-- 배우의 이름과 고객의 이름을 하나로 조회
SELECT first_name
FROM actor
UNION
SELECT first_name
FROM customer

-- 중복확인을 위해 UNION 후 정렬
SELECT first_name
FROM actor
UNION
SELECT first_name
FROM customer
order by first_name;
```

# **2. UNION ALL**

중복까지 모두 출력한다. 중복확인을 위해 UNION ALL후 정렬

```
SELECT first_name
FROM actor
UNION ALL
SELECT first_name
FROM customer
order by first_name;
```

# 3. **INTERSECT**

두 결과에 모두 존재하는 데이터만 조회한다. 배우와 고객 모두에 존재하는 이름만 출력된다.

```
SELECT first_name
FROM actor
INTERSECT
SELECT first_name
FROM customer;
```

# **4. EXCEPT**

첫 번째 결과에는 있지만 두 번째 결과에는 없는 데이터만 조회한다. 배우 이름 중 고객 이름에는 없는 데이터만 출력된다.

```
SELECT first_name
FROM actor
EXCEPT
SELECT first_name
FROM customer;

-- 컬럼명이 달라도 컬럼 개수와 타입만 맞으면 된다.
​SELECT first_name
FROM actor
UNION
SELECT city
FROM city;

-- 컬럼 개수가 다르면 오류
-- Error Code: 1222. The used SELECT statements have a different number of columns
SELECT first_name, last_name
FROM actor
UNION
SELECT first_name
FROM customer;

-- 데이터 타입이 다르면 MySQL은 가능한 경우 자동 형변환을 수행한다.
SELECT actor_id
FROM actor
UNION
SELECT first_name
FROM customer;
```