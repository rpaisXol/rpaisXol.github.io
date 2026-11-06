---
title: 22. CTAS(Create Table As Select)
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
**CTAS(Create Table As Select)**는 **조회 결과를 이용하여 새로운 테이블을 생성**하는 기능이다.

```sql
-- sql 문법
CREATE TABLE 새테이블 
AS 
SELECT ... 
FROM 원본테이블;
```

컬럼명도 select의 결과물인 별칭으로 만들어 지고, 데이터 타입 select결과물로 유추, 데이터도 select 필터링 결과만 복사

![[22) CTAS(Create Table As Select)-1793938370878.webp]]

전체 테이블 복사 - KEY설정은 복사 되지 않는다. 복사후 개별 키 설정이 필요
```sql
CREATE TABLE category_copy 
AS 
SELECT * 
FROM category;
```

특정 컬럼만 복사
```sql
CREATE TABLE film_simple 
AS 
SELECT film_id, title, rental_rate 
FROM film;
```

필터링 복사
```sql
CREATE TABLE expensive_film 
AS 
SELECT film_id, title, rental_rate 
FROM film 
WHERE rental_rate >= 4.99;
```

집계결과를 복사
```sql
CREATE TABLE category_film_count
AS
SELECT
    c.category_id,
    c.name AS category_name,
    COUNT(*) AS film_count
FROM category c
JOIN film_category fc
    ON c.category_id = fc.category_id
GROUP BY
    c.category_id,
    c.name;
```

구조만 복사하고 데이터는 제외
```sql
CREATE TABLE film_empty 
AS 
SELECT * FROM film 
WHERE 1 = 0;
```