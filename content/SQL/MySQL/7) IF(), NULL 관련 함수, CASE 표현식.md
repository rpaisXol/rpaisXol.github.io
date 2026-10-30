---
title: 데이터 관계와 조인 결과의 행 수
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# 1. 기타 단일행 함수

IF(), NULL 관련 함수, CASE 표현식은 조건에 따라 다른 값을 반환할 때 사용하는 기능이다.

### 1. IF()

IF(조건식, 참 값, 거짓 값)

```
-- 영화 러닝타임으로 구분
SELECT
    title, -- 컬럼
    length, -- 컬럼
    IF(length >= 120, '장편', '일반') AS movie_type -- 계산된 조회
FROM film
order by movie_type asc, length asc;

-- 대여기간으로 구분
SELECT
    title,
    rental_duration,
    IF(rental_duration >= 5, '길다', '짧다') AS duration_type
FROM film;
```

### 2) NULL관련 함수

![[7) IF(), NULL 관련 함수, CASE 표현식-1793351906735.webp]]

```
IFNULL(컬럼, 대체값)
```

```
-- film 테이블 original_language_id는 모두 NULL이다
SELECT
    title,
    language_id,
    original_language_id,
    IFNULL(original_language_id, 0) AS original_language_id
FROM film;
```

```
NULLIF(값1, 값2)
```

```
SELECT
    title,
    rental_rate,
    NULLIF(rental_rate, 4.99) AS result
FROM film;
```

test 데이터베이스에 null값이 존재하는 테이블 생성 후 null 관련 함수 연습

```
CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30),
    price INT,
    discount INT
);

INSERT INTO product(name, price, discount)
VALUES
('노트북', 1500000, 10),
('마우스', 30000, NULL),
('키보드', NULL, 15),
('모니터', 250000, NULL),
('스피커', NULL, NULL);
```

```
SELECT
    name,
    IFNULL(price, 0) AS price
FROM product;

SELECT
    name,
    NULLIF(discount, 10) AS discount
FROM product;

SELECT
    name,
    COALESCE(price, discount, 0) AS value
FROM product;

SELECT *
FROM product
WHERE price IS NULL;

SELECT *
FROM product
WHERE discount IS NOT NULL;
```

# **2. CASE 표현식**

여러 조건을 처리할 때 사용한다.

```
--- if() 함수는 조건이 많아지면 중첩이 발생하여 가독성이 떨어진다.

select if(name = '노트북', 1, if(name = '마우스', 2, 3)) 
from product; 
```

```
CASE
    WHEN 조건1 THEN 결과1
    WHEN 조건2 THEN 결과2
    ELSE 결과3
END
```

![[7) IF(), NULL 관련 함수, CASE 표현식-1793352136921.webp]]

```
SELECT
    title,
    length,
    CASE
        WHEN length >= 150 THEN '매우 김'
        WHEN length >= 120 THEN '장편'
        WHEN length >= 90 THEN '보통'
        ELSE '단편'
    END AS length_type
FROM film;
```

```
SELECT
    title,
    rental_rate,
    CASE
        WHEN rental_rate = 0.99 THEN '저가'
        WHEN rental_rate = 2.99 THEN '중가'
        WHEN rental_rate = 4.99 THEN '고가'
        ELSE '기타'
    END AS price_type
FROM film;
```

```
SELECT
    title,
    rating,
    CASE rating
        WHEN 'G' THEN '전체관람가'
        WHEN 'PG' THEN '부모지도'
        WHEN 'PG-13' THEN '13세 이상'
        WHEN 'R' THEN '청소년 제한'
        WHEN 'NC-17' THEN '17세 이상'
        ELSE '기타'
    END AS rating_name
FROM film;
```

### 3. where절에서 사용 예

```
-- 상영시간이 120분 이상이면 rental_rate >= 2.99 인 영화 조회
-- 120분 미만이면 rental_rate >= 0.99인 영화 조회
SELECT
    title,
    length,
    rental_rate
FROM film
WHERE IF(length >= 120,
         rental_rate >= 2.99,
         rental_rate >= 0.99);
```

```
-- rating이 G이면 90분 이상 조회, 아니면 120분 이상 조회
SELECT
    title,
    rating,
    length
FROM film
WHERE IF(rating = 'G',
         length >= 90,
         length >= 120);
```

```
-- original_language_id가 NULL이면 >=연산자를 사용할 수 없기때문에 NULL이면 0으로 바꿔 비교
SELECT
    title,
    original_language_id
FROM film
WHERE IFNULL(original_language_id, 0) >= 10;
```

※ IS NULL / IS NOT NULL 연산자

```
SELECT *
FROM film
WHERE original_language_id IS NULL;

SELECT *
FROM film
WHERE original_language_id IS NOT NULL;
```

WHERE절 CASE

```
-- G 등급은 90분 이상, 그 외는 120분 이상 조회
SELECT
    title,
    rating,
    length
FROM film
WHERE
CASE
    WHEN rating = 'G'
        THEN length >= 90
    ELSE
        length >= 120
END;
```

### 4. order by절에서 사용 예

```
SELECT
    title,
    length
FROM film
ORDER BY length ASC;

-- 120분보다 작은 영화와 120분 이상인 영화로 구분하여 제목의 오름차순으로 조회 
SELECT
    title,
    length
FROM film
ORDER BY IF(length < 120, 0, 1) ASC, title ASC;
```

- 오름차순 정렬하면 NULL값은 제일 먼저 온다. 
- NULL이면 999로 바꿔 마지막에 정렬이 되게

```
SELECT
    title,
    original_language_id
FROM film
ORDER BY
    IFNULL(original_language_id, 999);


-- test db 에서
select * from product
order by discount asc;

select * from product
order by ifnull(discount, 100) asc;
```

- 컬럼값으로 오름/내림이 아닌 특정 순서로 정렬
- 등급이 ASC이면 이넘타입(배열처럼 순서가 있는 타입)이라 G -> PG -> PG-13 -> R -> NC-17 순으로 정렬되어 조회된다.
- PG-13 -> NC-17 순으로 하고 나머지 순서없이 조회

```
SELECT
    title,
    rating
FROM film
ORDER BY
CASE
    WHEN rating = 'PG-13' THEN 1
    WHEN rating = 'NC-17' THEN 2
    ELSE 3
END;
```

- 장편 먼저, 같은 장편이면 제목순으로 정렬

```
SELECT
    title,
    length
FROM film
ORDER BY
CASE
    WHEN length >= 150 THEN 1
    WHEN length >= 100 THEN 2
    ELSE 3
END,
title;
```