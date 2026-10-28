---
title: SELECT - 컬럼의 데이터 타입과 형변환
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# **1. 데이터 타입**

MySQL8.4의 전체 데이터 타입은 [https://dev.mysql.com/doc/refman/8.4/en/data-types.html](https://dev.mysql.com/doc/refman/8.4/en/data-types.html) 문서를 참조

![[5) 컬럼의 데이터 타입과 형변환-1793167579992.webp]]


# **2. 형변환(형변환 함수 사용)** 

**문자 -> 숫자**

```
-- CAST() 함수 사용
SELECT CAST('100' AS float) AS result; -- 컬럼 없이  값이나 계산식을 SELECT로 조회시 FROM절 생략

-- 문자열끼리 더하기 자동 형변환(MySQL에선 +연산이 숫자 연산에만 사용된다)
SELECT '100' + '200' AS result;
SELECT '100' + 50;
SELECT '100원' + 50;
SELECT 'xyz' + 50; -- 문자는 0으로 변환
```

**숫자 -> 문자**

```
SELECT CAST(123 AS CHAR);

SELECT CONCAT(CAST(100 AS CHAR), '원');

SELECT concat(cast(customer_id as char), '번') 번호, first_name
FROM customer;
-- 자동형변환 이용
SELECT concat(customer_id, '번') 번호, first_name
FROM customer;
```

**문자 -> 날짜**

```
SELECT CAST('2026-07-13' AS DATE); 

SELECT CAST('2026-07-13 09:30:00' AS DATETIME);
```

**날짜 -> 문자**

```
SELECT CAST(NOW() AS CHAR);
```

**문자 -> 날짜**

```
SELECT STR_TO_DATE('20260713', '%Y%m%d'); 

SELECT STR_TO_DATE('2026-07-13', '%Y-%m-%d');
```

**실수 <-> 정수**

```
SELECT CAST(123.987 AS SIGNED);

SELECT CAST(100 AS DECIMAL(10,2));

SELECT
	CAST(10/3 AS unsigned),
	CAST(10/3 AS decimal(10,2)),
    CAST(10/3 AS float), -- 6번째 정밀도
    CAST(10/3 AS double); -- 9번째
```
