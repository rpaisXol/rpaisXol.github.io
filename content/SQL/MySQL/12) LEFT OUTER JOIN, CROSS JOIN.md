---
title: 12. LEFT OUTER JOIN, CROSS JOIN
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# 1. LEFT OUTER JOIN

```sql
INSERT INTO country(country)
VALUES ('New Land');
```

```sql
-- New Land는 조회되지 않는다. 
-- INNER JOIN은 양쪽 테이블에 모두 존재하는 데이터만 조회하기 때문이다.
SELECT c.country, ci.city 
FROM country c INNER JOIN city ci 
ON c.country_id = ci.country_id;
```

```
country               city
------------------------------
Afghanistan   → 있음
Algeria       → 있음
...
New Land  → 없음
```

```sql
-- LEFT OUTER JOIN을 사용하면 도시가 없는 city 컬럼은 NULL로 조회된다.
SELECT c.country, ci.city
FROM country c
LEFT OUTER JOIN city ci
ON c.country_id = ci.country_id;
```

"OUTER"는 생략 후 "LEFT JOIN" 사용 가능
LEFT JOIN은 왼쪽 테이블(country)의 모든 데이터를 먼저 조회한다.
그 후 오른쪽 테이블(city)에서 일치하는 데이터를 찾는다.
도시가 있으면 → 함께 출력
도시가 없으면 → NULL로 출력

```sql
-- 도시가 없는 나라 출력
select co.country, ci.country_id
from country co left join city ci
on ci.country_id = co.country_id
where ci.country_id is null;
```

#### 언제 LEFT JOIN을 사용해야 하는가?
- "기준이 되는 테이블의 데이터는 모두 보고 싶을 때" 사용한다.
- 회원 목록(주문하지 않은 회원도 포함)
- 학생 목록(결석한 학생도 포함)
- 부서 목록(사원이 없는 부서도 포함)
- 카테고리 목록(영화가 없는 장르도 포함)

# **2. 중간 테이블이 있는 3개의 테이블을 조인**

```sql
-- 1) category 테이블에 새로운 장르 추가
INSERT INTO category(name) 
VALUES ('KContents');
```

```sql
-- 2) INNER JOIN 조회
SELECT c.name AS category, f.title
FROM category c
INNER JOIN film_category fc
    ON c.category_id = fc.category_id
INNER JOIN film f
    ON fc.film_id = f.film_id;
```

```sql
-- 3) LEFT OUTER JOIN 조회
SELECT c.name AS category, f.title
FROM category c
LEFT OUTER JOIN film_category fc
    ON c.category_id = fc.category_id
LEFT OUTER JOIN film f
    ON fc.film_id = f.film_id;
```

```sql
-- 4) IFNULL(), IF(), CASE등을 사용하여 다른 값으로 변경
SELECT c.name AS category,
       IFNULL(f.title, '등록된 영화 없음') AS title
FROM category c
LEFT OUTER JOIN film_category fc
    ON c.category_id = fc.category_id
LEFT OUTER JOIN film f
    ON fc.film_id = f.film_id;
```

# 3. CROSS JOIN

학생과 과목 테이블에서 성적표를 출력하는 경우의 수?

```sql
-- student 테이블 생성
CREATE TABLE student (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(30)
);

-- subject 테이블 생성
CREATE TABLE subject (
    subject_id INT PRIMARY KEY,
    subject_name VARCHAR(30)
);
```

```sql
-- 데이터 삽입
INSERT INTO student VALUES
(1, '홍길동'),
(2, '김철수'),
(3, '이영희');

-- 데이터 삽입
INSERT INTO subject VALUES
(101, 'SQL'),
(102, 'Python'),
(103, 'Power BI');
```

```sql
-- CROSS JOIN 사용
SELECT s.student_name,
       sub.subject_name
FROM student s
CROSS JOIN subject sub;
```

![[12) LEFT OUTER JOIN, CROSS JOIN-1793594935631.webp]]

**CROSS JOIN은 두 테이블의 모든 데이터를 서로 조합하는 조인이다.**
**학생이 3명이고 과목이 3개라면** 3 × 3 = 9개의 조합이 생성된다.

```
- 상품 옵션 생성
색상 × 사이즈 × 소재
예) 검정/M/면, 검정/L/면, 흰색/M/면 ...

- 출석부·근태 데이터 초기 생성
직원 × 근무일
학생 × 수업일

- 시험 또는 수강신청 대상 생성
학생 × 과목
응시자 × 시험장

- 예약 가능 시간 생성
회의실 × 날짜 × 시간대

- 매장별 상품 배정
매장 × 상품
이후 판매 여부나 재고만 업데이트

- 권한 관리
사용자 × 시스템 기능
모든 권한 목록을 생성한 후 권한 여부를 설정

- 캘린더(달력) 생성
연도 × 월
날짜 × 시간
시간 × 분

-테스트 데이터 생성
사용자 × 이벤트
고객 × 쿠폰
지역 × 상품

- 통계 분석용 기준 데이터 생성
지역 × 월
부서 × 연도
매장 × 상품군

- AI·데이터 분석
모델 × 하이퍼파라미터
실험 조건 × 데이터셋
추천 시스템의 후보 조합 생성
```