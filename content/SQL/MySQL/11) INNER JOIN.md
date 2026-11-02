---
title: INNER JOIN
created: 2026-10-19
updated: 2026-10-19
tags:
no:
slug:
---
# **1. INNER JOIN**

- INNER JOIN은 **두 테이블에서 서로 일치하는 데이터만 조회**하는 조인이다. **조인 조건(ON)이 만족하는 행만 결과에 포함**된다.

```
A (학생/캐릭터)                        B (기술)
PK(번호)                              PK(번호, 기술)
                                     FK(번호) → A.번호

번호   이름                           번호   기술
──────────────────                   ─────────────────────
1     루피                            1     고무고무 총
2     조로                            2     일도류
3     나미                            3     사이클론 템포
4     쵸파                            1     기어2
```

**- 조인 조건(A.번호 = B.번호)을 만족하는 행만 연결한다.**
**- 서로 다른 두테이블을 조인할 때는 공통으로 존재하는 컬럼이 필요하다.**
**- 학생의 "번호"컬럼을 사용해서 두 테이블을 연결한다.**
**- 조인에는 여러 종류의 조인이 있는데,** **INNER JOIN은 두 테이블에 있는 모든 행이 연결되는 것이 아니라, 조인 조건에 부합되는 행들만 연결한다.**

```
            JOIN 과정

A                           B
───────                     ────────────────

1 루피   ───────────────▶    1 고무고무 총   ✓
      │
      └───────────────▶      1 기어2        ✓

2 조로   ───────────────▶    2 일도류       ✓

3 나미   ───────────────▶    3 사이클론 템포 ✓


4 쵸파                         (번호가 다르므로 연결 안됨)
번호   이름   기술
────────────────────────
1     루피   고무고무 총
1     루피   기어2
2     조로   일도류
3     나미   사이클론 템포
```

**- PK(Primary Key)** 는 부모 테이블의 각 행을 유일하게 식별한다.
**- FK(Foreign Key)** 는 부모의 PK를 참조한다.
**- INNER JOIN** 은 PK = FK가 같은 행끼리 연결한다.

- 부모 1개에 자식이 여러 개면(**1:N 관계**) 부모 행이 **자식의 개수만큼 반복되어 결과에 나타난다.**
- 관계형 데이터베이스(RDB)는 **테이블 간의 관계(Relationship)** 를 이용해 데이터를 관리한다. 이 관계를 연결하는 것이 **외래키(Foreign Key)** 이고, 연결된 데이터를 함께 조회하는 것이 **INNER JOIN**이다.
- 외래키는 테이블을 연결하는 "관계"를 정의하고, INNER JOIN은 그 관계를 이용해 필요한 데이터를 함께 조회하는 기능**이다.

​
**INNER JOIN 문법**

```
SELECT 조회할컬럼
FROM 첫번째테이블
INNER JOIN 두번째테이블
ON 첫번째테이블.기본키 = 두번째테이블.외래키;
```

# **2. 2개의 테이블을 INNER JOIN**

- Sakila 데이터베이스에서 country와 city 테이블은 **country_id** 로 연결되어 있다.
- ▲가 가리키는 쪽이 부모 테이블, 반대쪽이 참조하는(외래키) 자식 테이블

```
country
---------------------
country_id (PK)
country
last_update
        ▲
        │
        │ country_id
        │
city
---------------------
city_id (PK)
city
country_id (FK)
last_update

- country.country_id : 기본키(PK)
- city.country_id : 외래키(FK)
- 한 나라(country)에 여러 도시(city)가 존재하는 1:N 관계이다.
```

```
SELECT
    c.city,
    co.country
FROM city AS c -- city 테이블을 읽는다.
INNER JOIN country AS co
    ON c.country_id = co.country_id; -- city.country_id와 country.country_id가 같은 행을 찾는다.

-- 일치하는 데이터만 결합한다.
-- 일치하는 데이터만 결합한다.
```

# **3. 3개의 테이블을 INNER JOIN**

![[11) INNER JOIN-1793594062218.webp]]

```
country
--------
country_id (PK)
      ▲
      │ 1:N
      │  
city
-----
city_id (PK)
country_id (FK)
      ▲
      │ 1:N
      │
address
--------
address_id (PK)
city_id (FK)

- 한 나라에는 여러 도시가 있다.
- 한 도시에는 여러 주소가 있다.
```

```
SELECT
    co.country,
    c.city,
    a.address
FROM country AS co
INNER JOIN city AS c
    ON co.country_id = c.country_id
INNER JOIN address AS a
    ON c.city_id = a.city_id;
```

# **4.** **중간(연결)테이블**로 연결된 3개의 테이블을 INNER JOIN

**category**와 **film**은 직접 연결되어 있지 않다. 중간에 **film_category** 테이블을 통해 연결된다.

```
category
---------
category_id
name

      ▲
      │
      │

film_category
-------------
film_id
category_id

      │
      │
      ▼

film
----
film_id
title
release_year
length
rating
...
```

**※ country - city - address** vs **category - film_category - film**
"country - city - address"sms **계층(Parent → Child)** 구조이다. 각 테이블은 독립적인 의미를 가진다.

```
country 
   ▲
   │
city (country_id 외래키를 사용) 
   ▲
   │
address (city_id 외래키를 사용)
```

"category - film_category - film"의 film_category는 두 테이블의 연계을 설정하는 **관계를 저장하는 연결 테이블**이다.

```
film
   ▲
   │
film_category (film_id /category_id 연결을 위한 두개의 데이터 저장이 목적)
   │
   ▼
category
```

film_category는 영화(film)와 장르(category)의 다대다(N:M) 관계를 구현하기 위한 연결(중간) 테이블이다. **Association Table(연관 테이블) 또는 Join Table, Junction Table 등의 이름으로 불린다.**

관계형 데이터베이스에서 테이블간의 **N:M 관계를 1:N + 1:N으로 분해하기 위해 사용하는 테이블**을 의미한다.

```
-- 1) 영화 제목과 카테고리 조회

SELECT
    f.title,
    c.name AS category
FROM film AS f  -- ① film 테이블부터 시작한다.
INNER JOIN film_category AS fc
    ON f.film_id = fc.film_id  -- ② 영화의 film_id와 film_category의 film_id를 연결한다.
INNER JOIN category AS c
    ON fc.category_id = c.category_id;  -- ③ film_category의 category_id와 category의 category_id를 연결한다.
```

```
-- 2) Action 장르 영화 조회

SELECT
    f.title,
    c.name
FROM film AS f
INNER JOIN film_category AS fc
    ON f.film_id = fc.film_id
INNER JOIN category AS c
    ON fc.category_id = c.category_id
WHERE c.name = 'Action';
```

```
-- 3) 영화 제목이 A로 시작하는 영화

SELECT
    f.title,
    c.name
FROM film AS f
INNER JOIN film_category AS fc
    ON f.film_id = fc.film_id
INNER JOIN category AS c
    ON fc.category_id = c.category_id
WHERE f.title LIKE 'A%'
ORDER BY f.title;
```

```
-- 4) PG 등급 영화만 조회

SELECT
    f.title,
    f.rating,
    c.name
FROM film AS f
INNER JOIN film_category AS fc
    ON f.film_id = fc.film_id
INNER JOIN category AS c
    ON fc.category_id = c.category_id
WHERE f.rating = 'PG';
```