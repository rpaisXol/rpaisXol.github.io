---
title: 23. NATURL JOIN, USING
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
- JOIN ... ON을 기본으로 사용하고, 조인 컬럼명이 동일하며 조건이 단순할 때만 USING을 사용하는 경우가 있다. 
- NATURAL JOIN은 공통 컬럼이 추가되거나 변경되면 조인 조건이 바뀌어 예상치 못한 결과를 낼 수 있으므로 일반적으로 권장되지 않는다.

​**1. ANSI JOIN**
- 조인 조건을 명시
- 어떤 컬럼으로 조인하는지 한눈에 보임

​컬럼명 별칭

```sql
SELECT
    a.actor_id,
    a.first_name,
    a.last_name,
    fa.film_id
FROM actor a JOIN film_actor fa
ON a.actor_id = fa.actor_id;
```

**2. USING 사용**
- 두 테이블의 **조인 컬럼명이 같을 때** 사용할 수 있다.

```sql
SELECT
    actor_id,
    first_name,
    last_name,
    film_id
FROM actor JOIN film_actor
USING (actor_id);
```

**3. NATURAL JOIN**
- 두 테이블의 **조인 컬럼명이 같을 때** 사용할 수 있다.
- 컬럼명이 같은 모든 컬럼을 자동으로 조인한다.

```sql
SELECT * 
FROM actor 
NATURAL JOIN film_actor;
```

![[23) NATURL JOIN, USING-1793938616359.webp]]