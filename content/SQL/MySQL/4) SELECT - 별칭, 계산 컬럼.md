---
title: SELECT - 별칭, 계산 컬럼
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
## **1. 별칭**

AS는 **컬럼이나 테이블에 별칭(Alias, 별명)을 지정하는 키워드**이다.

​컬럼명 별칭

```
SELECT
    first_name AS 이름,
    last_name AS 성
FROM customer;
```

AS는 생략 가능

```
SELECT
    first_name 이름
FROM customer;
```

테이블 별칭
컬럼 별칭은 조회 결과(출력 결과)에 필요해서, 테이블 별칭 편의상, 가독성을 위해

```
SELECT
    c.customer_id,
    c.first_name
FROM customer AS c; -- AS생략가능 FROM customer c
```

## **2. 계산 컬럼**

SELECT절에서는 **기존 컬럼뿐 아니라 계산된 값을 새로운 컬럼(계산 컬럼, Derived Column)** 으로 조회할 수 있다.

```
SELECT
    customer_id,
    customer_id + 1000 AS new_id
FROM customer;
```

- 컬럼을 함수의 인수로 사용 후 반환값을 새로운 컬럼으로 조회할 수 있다(함수는 뒤에서 다시 설명)

```
SELECT
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) AS full_name
FROM customer;
```

- 특정 값(계산값, 함수반환값, ...)을 조회에 추가 할 수 있다

```
SELECT
    customer_id,
    first_name, 
    10*10,
    'USA',
    NOW()
FROM customer 
LIMIT 10;
```
* order by 절은 select절 다음에 실행되므로 select절에서 사용한 별칭이나 select절 인덱스가 사용가능하다.
- where절의 경우 실행순서가 select절보다 먼저이므로 select절 별칭 사용 불가.

```
SELECT first_name 이름, last_name 성, customer_id % 2 AS 짝수
FROM customer
ORDER BY first_name; -- select절보다 뒤에 실행되는 절이기 때문에 별칭or위치숫자 사용가능
-- ORDER BY 이름;
-- ORDER BY 1;
```
