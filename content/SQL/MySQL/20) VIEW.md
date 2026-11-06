---
title: 20. VIEW
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---
# VIEW

- SELECT 문의 결과를 하나의 가상 테이블처럼 저장한 객체이다.
- 실제 데이터를 저장하는 것이 아니라 SELECT 문만 저장하며, 조회할 때마다 원본 테이블에서 데이터를 가져온다.

​**1. VIEW가 필요한 이유**
예를 들어 고객 정보와 주소를 자주 조회한다고 가정하면 매번 JOIN을 작성해야 한다.
```sql
SELECT
    c.first_name,
    c.last_name,
    a.address
FROM customer c
JOIN address a
ON c.address_id = a.address_id
```

이 쿼리를 뷰로 만들어 놓으면 다음 처럼 간단하게 사용할 수 있다.
```sql
CREATE VIEW customer_view AS
    SELECT
        c.first_name,
        c.last_name,
        a.address
    FROM customer c
    JOIN address a
    ON c.address_id = a.address_id
```

**VIEW vs CTE**

![[20) VIEW-1793937585420.webp]]

**2. VIEW 장점**
1. SQL이 간단해진다.
- 복잡한 JOIN을 매번 작성할 필요가 없다.

2. 재사용성이 높다.
- 자주 사용하는 SELECT 문을 여러 프로그램이나 사용자가 함께 사용할 수 있다.

3. 가독성이 좋아진다.
- 복잡한 SQL을 숨기고 의미 있는 이름으로 사용할 수 있다.

4. 보안에 유리하다.
- 필요한 컬럼만 보여줄 수 있다.

5. 유지보수가 쉽다.
- 동일한 SQL을 여러 곳에서 작성하는 대신, 뷰만 수정하면 이를 사용하는 모든 프로그램에 변경 사항이 반영된다.

**3. Sakila에 있는 VIEW**
![[20) VIEW-1793937709156.webp]]

![[20) VIEW-1793937721518.webp]]