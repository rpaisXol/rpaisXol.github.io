---
title: 18. 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
**※ 집계함수 vs 원도우함수**
**집계함수의 결과셋은 최종 SELECT의 결과셋**
**원도우함수의 결과셋은 서브쿼리의 결과셋과 동일하다. -> 메인쿼리와 합쳐저야(집합, 조인,...) 한다.**

# **1. 윈도우 함수에서 함께 사용하는 옵션**
윈도우 함수는 대부분 OVER() 절과 함께 사용하며, 다음 요소를 조합하여 계산 범위를 지정한다.

1. **PARTITION BY** : 데이터를 그룹으로 나눈다.

2. **ORDER BY** : 그룹 내 정렬 기준을 지정한다.

3. **ROWS / RANGE**
- 계산할 행의 범위를 지정한다. ORDER BY가 없으면 행의 순서가 없기 때문에 ROWS나 RANGE를 사용할 수 없다.
- ORDER BY가 없으면 계산할 범위는 "**RANGE 처음~ 끝**"과 동일하고, ORDER BY가 있고 ROWS / RANGE절이 없으면 **"RANGE 처음 ~ 현재행**"이 된다.
- ROWS와 RANGE는 ORDER BY를 기준으로 동작하며, PARTITION BY가 있다면 각 그룹 내부에서만 범위를 계산한다.

```sql
OVER (
    PARTITION BY ...
    ORDER BY ...
    ROWS BETWEEN ...
)
```

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793754949689.webp]]

※ 행을 기준으로 하면 현재 행의 값만을 계산에 사용하지만, 값 범위 기준을 사용하면 다른 행의 같은 값까지 다 포함하여 계산한다. 값 범위 기준의 계산은 특별한 경우가 아니면 잘 사용되지 않는다.

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793754957347.webp]]

현재행이 2행이고 처음부터 현재까지 행기준이면 

```sql
SUM(score) 
OVER (
	ORDER BY score 
	ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755047678.webp]]

- score의 **SUM은 80 + 90 = 170** 이고,

현재행이 2행이고 처음부터 현재까지 범위(값) 기준이면

```sql
SUM(score) 
OVER (
	ORDER BY score RANGE 
	BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

score의 **SUM은 80 + 90 + 90 = 260** 이 된다.

# 2. 윈도우 범위

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755122853.webp]]

예)

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755130570.webp]]

학생의 점수가 다음과 같다면

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755141274.webp]]

**현재 행이 3행이라면 C(90점)**
- UNBOUNDED PRECEDING ~ CURRENT ROW : **A + B + C (80, 85, 90)**
- 2 PRECEDING ~ CURRENT ROW : **A + B + C (80, 85, 90)**
- 1 PRECEDING ~ CURRENT ROW : **B + C (85, 90)**
- 1 PRECEDING ~ 1 FOLLOWING : **B + C + D (85, 90, 95)**
- CURRENT ROW ~ UNBOUNDED FOLLOWING : **C + D + E (90, 95, 100)**

이처럼 ROWS는 "현재 행을 기준으로 앞뒤 몇 개의 행을 계산할 것인가"를 지정하는 기능

좀 더 이해하기

```sql
-- 함수() over() : 전체를 하나로, 정렬x, RANGE처음 ~ 끝
-- 정렬이 없으면 "RANGE처음 ~ 끝" 고정이라 윈도우절을 명시적으로 범위설정을 할 수 없다.
-- 함수() over(partition by) : n개의 파티션, 정렬x, RANGE처음 ~ 끝
-- 함수() over(order by) : 1개의 파티션, 정렬o, RANGE처음 ~ 현재
-- 정렬이 있다면 "RANGE처음 ~ 현재"가 기본값이지만 윈도우절을 명시적으로 범위설정을 변경할 수 있다.
-- 함수() over(partition by order by) : n개의 파티션, 정렬o, RANGE처음 ~ 현재
SELECT
    title,
    length,
    sum(length) OVER(ORDER BY length DESC) 값범위누적, -- range between unbounded preceding and current row 기본값으로 됨
    sum(length) OVER(ORDER BY length DESC 
				rows between unbounded preceding and current row) 행범위누적,
	sum(length) OVER(ORDER BY length DESC 
				rows between unbounded preceding and unbounded following) 전체합
FROM film;
```

**1) 상영시간의 누적합**
상영시간이 짧은 영화부터 현재 영화까지의 **상영시간 합계**를 구한다.

```sql
SELECT
    title,
    length,
    SUM(length) OVER(
        ORDER BY length
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_length
FROM film;
```

**2) 최근 3개 영화의 평균 상영시간 : 이전 2행 + 현재 (최근 3건 평균)**
- 현재 영화와 바로 앞의 2편을 포함한 **3편의 평균 상영시간**을 구한다.
- 동작 방식이 슬라이딩 윈도우 알고리즘과 유사

```sql
SELECT
    title,
    length,
    AVG(length) OVER(
        ORDER BY length
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS avg_length
FROM film;
```

**3) 최근 3개 영화의 평균 상영시간 : 이전 1행 + 현재 + 다음 1행**
현재 영화를 중심으로 앞뒤 1편씩 포함한 3편의 평균 상영시간을 구한다.

```sql
SELECT
    title,
    length,
    AVG(length) OVER(
        ORDER BY length
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS neighbor_avg
FROM film;
```

**4) 현재부터 마지막까지 (남은 데이터 누계)**
현재 영화부터 마지막 영화까지의 상영시간 합계

```sql
SELECT
    title,
    length,
    SUM(length) OVER(
        ORDER BY length
        ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
    ) AS remaining_length
FROM film;
```

**3. PARTITION BY + ORDER BY + ROWS를 모두 사용하는 예)**

직원(staff)별 일자별 매출을 구한 뒤, 최근 7일간(일주일)의 누적 매출을 계산, 7일간(일주일)의 누적 매출이 많았던 데이터 조회

```sql
SELECT
    p.staff_id,
    DATE(p.payment_date) AS pay_date,
    SUM(p.amount) AS daily_amount
FROM payment p
GROUP BY
    p.staff_id,
    DATE(p.payment_date);
```

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755348926.webp]]

```sql
SELECT
    staff_id,
    pay_date,
    daily_amount,

    SUM(daily_amount) OVER (
	    -- 직원별로 데이터를 나누고 각 직원 그룹 안에서만 계산
        PARTITION BY staff_id 
        -- 날짜순으로 정렬
        ORDER BY pay_date 
        -- 직전 6행~현재행, 총 7행 7일을 계산 대상
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW 
    ) AS rolling_7days
FROM (
    SELECT
        staff_id,
        DATE(payment_date) AS pay_date,
        SUM(amount) AS daily_amount
    FROM payment
    GROUP BY
        staff_id,
        DATE(payment_date)
) t
ORDER BY staff_id, pay_date;
```

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755386418.webp]]

![[18) 윈도우범위(ROWS, RANGE)를 사용하는 윈도우 함수-1793755391692.webp]]

