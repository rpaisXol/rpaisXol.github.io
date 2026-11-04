---
title: 15. 집계함수 GROUP_CONCAT(), COUNT(DISTINCT), STDDEV(), VARIANCE()
created: 2026-10-19
updated: 2026-10-19
tags:
note_type:
slug:
---

# 1. 문자열 집계함수 GROUP_CONCAT()

```sql
CREATE TABLE student ( 
	id INT PRIMARY KEY, 
	name VARCHAR(20) NOT NULL, 
	gender CHAR(1) NOT NULL, 
	age INT NOT NULL 
);
```

```sql
INSERT INTO student (id, name, gender, age) VALUES
(1, '김민수', 'M', 20),
(2, '이영희', 'F', 22),
(3, '박지훈', 'M', 21),
(4, '최수진', 'F', 23),
(5, '정우성', 'M', 19),
(6, '한지민', 'F', 20),
(7, '오세훈', 'M', 24),
(8, '윤아름', 'F', 21),
(9, '강동원', 'M', 22),
(10, '송지은', 'F', 19);
```

```sql
SELECT gender, count(*)
	, group_concat(name order by name desc separator ' / ')
FROM student
GROUP BY gender;
```

영화에 출연한 배우 목록: JOIN만 적으면 "INNER JOIN"으로 실행<br>
축약형 JOIN (INNER JOIN), LEFT JOIN (LEFT OUTER JOIN)

```sql
SELECT
    f.title,
    GROUP_CONCAT(
        CONCAT(a.first_name, ' ', a.last_name)
        ORDER BY a.last_name
        SEPARATOR ', '
    ) AS actors
FROM film f
INNER JOIN film_actor fa
    ON f.film_id = fa.film_id
INNER JOIN actor a
    ON fa.actor_id = a.actor_id
GROUP BY f.film_id, f.title
ORDER BY f.title;
```
