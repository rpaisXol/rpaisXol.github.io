---
title: SELECT - 숫자, 문자, 날짜 타입의 단일행 함수
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
- 전체 함수는 [https://dev.mysql.com/doc/refman/8.4/en/functions.html](https://dev.mysql.com/doc/refman/8.4/en/functions.html) 문서를 참고.
- 단일행 함수(Single Row Function)는 **한 행의 데이터를 입력받아 한 행의 결과를 반환하는 함수**이다.
- 예를 들어 고객이 599명이면 함수도 599번 실행되어 599개의 결과를 반환한다.

**1. 문자 단일행 함수**

![[6) 숫자, 문자, 날짜 타입의 단일행 함수-1793167828039.webp]]

```
SELECT
    first_name,
    UPPER(first_name) AS upper_name
FROM customer;

SELECT
    first_name,
    LOWER(first_name) AS lower_name
FROM customer;

SELECT
    first_name,
    LENGTH(first_name) AS length
FROM customer;

SELECT
    email,
    REPLACE(email, '.org', '.com') AS new_email
FROM customer;

SELECT
    first_name,
    LEFT(first_name, 3) AS first3
FROM customer;

SELECT
    last_name,
    RIGHT(last_name, 3) AS last3
FROM customer;

SELECT
    first_name,
    SUBSTRING(first_name, 2, 3) AS sub_name
FROM customer;

-- 고객 이름과 성을 합치고 이름 길이를 함께 출력
SELECT
    CONCAT(first_name, ' ', last_name) AS full_name,
    LENGTH(first_name) AS name_length
FROM customer;
```

**2. 숫자 단일행 함수**

![[6) SELECT - 숫자, 문자, 날짜 타입의 단일행 함수-1793168067775.webp]]

```
SELECT
    customer_id,
    MOD(customer_id, 10) AS remainder 
FROM customer;

SELECT
    customer_id,
    FLOOR(RAND() * 100) + 1 AS coupon_number
FROM customer
LIMIT 10;

SELECT
    payment_id,
    amount,
    ROUND(amount, 1) AS round_amount
FROM payment;

SELECT
    payment_id,
    amount,
    TRUNCATE(amount, 1) AS truncate_amount
FROM payment;

SELECT
    payment_id,
    amount,
    CEIL(amount) AS ceil_amount
FROM payment;

-- 10% 할인된 금액 구하기. 반올림 소수점 2까지
SELECT
    payment_id,
    amount,
    ROUND(amount * 0.9, 2) AS discount_price
FROM payment
LIMIT 10;

SELECT
    payment_id,
    amount,
    amount * 0.1 AS discount,
    round(amount-(amount * 0.1), 2) AS discount_price
FROM payment
LIMIT 10;
```

**3. 날짜 단일행 함수**

![[6) SELECT - 숫자, 문자, 날짜 타입의 단일행 함수-1793168092531.webp]]

**DATE_ADD()함수 INTERVAL 옵션 단위**

![[6) SELECT - 숫자, 문자, 날짜 타입의 단일행 함수-1793168100723.webp]]

```
SELECT
    NOW(),
    CURDATE(),
    CURTIME(),
    YEAR(NOW()),
    MONTH(NOW()),
    DAY(NOW());


SELECT
    first_name,
    YEAR(create_date) AS join_year
FROM customer;

-- 날짜타입 +, - 연산이 가능하지만, DATE_ADD()함수 사용을 권장
SELECT
    first_name,
    create_date,
    DATE_ADD(create_date, INTERVAL 30 DAY) AS after30
FROM customer;

-- 가입 후 며칠이 지났는지
SELECT
    first_name,
    DATEDIFF(CURDATE(), create_date) AS days_after_join
FROM customer;

SELECT
    first_name,
    YEAR(create_date) AS join_year,
    YEAR(curdate()) - YEAR(create_date) "가입 후 몇년",
    datediff(curdate(), create_date) "가입 후 몇일"
FROM customer;

-- 날짜 형식 변경
SELECT
    first_name,
    DATE_FORMAT(create_date, '%Y년 %m월 %d일') AS join_date
FROM customer;

-- 현재 날짜/시간 관련 함수
SELECT
    NOW() AS current_datetime,
    CURDATE() AS current_date,
    CURTIME() AS current_time;
```

**4. where절에서 단일행 함수 - 함수의 반환값을 조건값으로 비교**

```
SELECT 컬럼
FROM 테이블
WHERE 함수(컬럼) = 값;
```

```
-- 이름이 'A'로 시작하는 고객
SELECT *
FROM customer
WHERE LEFT(first_name, 1) = 'A';

-- 이름 길이가 5
SELECT *
FROM customer
WHERE LENGTH(first_name) = 5;

-- 대소문자 구분 없이 조회 : 대문자로 변경한 후 대문자로 조회 or 소문자로 변경 후 소문자로 조회
SELECT *
FROM customer
WHERE UPPER(first_name) = 'MARY';

-- .org로 끝나는
SELECT *
FROM customer
WHERE RIGHT(email, 4) = '.org';
```

```
SELECT *
FROM payment
WHERE MOD(payment_id, 2) = 0;

-- 반올림 후 결제금액이 5달러
SELECT *
FROM payment
WHERE ROUND(amount) = 5;
-- 2005년에 가입
SELECT *
FROM customer
WHERE YEAR(create_date) = 2005;

-- 2월에 가입
SELECT *
FROM customer
WHERE MONTH(create_date) = 2;

-- 올해 가입한
SELECT * 
FROM customer
WHERE YEAR(create_date) = YEAR(NOW())
SELECT
    first_name,
    LENGTH(first_name) AS name_length
FROM customer
WHERE LENGTH(first_name) >= 6;
```
- where 절에 자주사용되는 컬럼은 인덱스(키)를 지정하는게 보통인데, 아래의 경우 create_date 컬럼이 인덱스라면, 인덱스 컬럼에 함수를 사용한 YEAR(create_date)의 결과는 인덱스를 사용하지 못한다. 

- 따라서 인덱스가 있는 컬럼은 가능하면 함수 대신 범위 조건으로 검색하는 것이 성능에 유리하다. 다만 인덱스가 없는 컬럼이라면 함수 사용 여부에 따른 성능 차이는 거의 없다.

```
-- 
SELECT *
FROM customer
WHERE YEAR(create_date) = 2005;

-- 다음처럼 create_date 컬럼의 인덱스를 사용하는 범위 조건으로 작성하는 것이 성능상 더 유리하다.
SELECT *
FROM customer
WHERE create_date >= '2005-01-01'
  AND create_date < '2006-01-01';
```

