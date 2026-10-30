---
tags:
note_type:
slug:
title: DB&테이블 생성, 데이터 입력,수정,삭제,조회 SQL문
---
**SQL은 용도에 따라 DDL, DML, DCL 등으로 구분한다.***

![[2) DB&테이블 생성, 데이터 입력,수정,삭제,조회 SQL문-1793163201077.webp]]

# 1.  product 테이블 생성 SQL 쿼리

- AUTO_INCREMENT**는 새로운 행이 추가될 때 숫자를 **자동으로 1씩 증가시켜 저장하는 속성**이다.
- 주로 **기본키(Primary Key)**에 사용하여 각 행에 고유한 번호를 자동으로 부여한다.
- SQL쿼리에서 줄바꿈,탭은 공백한칸과 동일하다. 명령의 종결은 ";"이다.
- 쿼리를 작성할때 줄바꿈과 탭을 사용하여 가독성을 높여준다.

DDL : CREATE, DROP, ALTER

```
CREATE DATABASE test;

CREATE TABLE product ( 
	id INT AUTO_INCREMENT PRIMARY KEY, 
	name VARCHAR(30), 
	price INT 
);
```

# **2. 조회, 입력, 수정, 삭제 SQL 쿼리**

​DML : INSERT, UPDATE, DELETE, SELECT
```
-- 추가 
INSERT INTO product(name, price) 
VALUES ('키보드', 50000); 

INSERT INTO product(name, price) 
VALUES ('마우스', 30000); 

-- 조회 
SELECT * FROM product; 

-- 수정 
UPDATE product 
SET price = 35000 
WHERE id = 2; 

-- 다시 조회 
SELECT * FROM product; 

-- 삭제 
DELETE FROM product WHERE id = 1; 

-- 최종 조회 
SELECT * FROM product; 

-- TRUNCATE문으로도 데이터를 삭제할 수 있다 
TRUNCATE product;
```

※ DELETE vs TRUNCATE

| DELETE                 | TRUNCATE           |
| ---------------------- | ------------------ |
| 모든 행 삭제 가능             | 모든 행 삭제            |
| AUTO_INCREMENT 유지      | AUTO_INCREMENT 초기화 |
| WHERE 사용으로 원하는 행 삭제 가능 | WHERE 사용 불가        |
| ROLLBACK 가능            | ROLLBACK 불가        |
* 대량의 데이터를 삭제할 때 DELETE문을 사용하면 트랜잭션 로그 기록으로 인해 데이터베이스 성능에 많은 문제가 발생할 수 있다. 롤백을 않는다는 가정하에 전체 데이터를 빠르게 삭제하려면 TRUNCATE 사용.

# **3. NULL vs NOT NULL**

- NULL은 0도 아니고 빈 문자열("")도 아니다. 값이 아직 없거나(미입력), 알 수 없는 상태를 의미한다.
- 테이블에서 컬럼값이 필수 입력값이라면 NOT NULL을 사용. 기본키의 자동으로 NOT NULL이 된다.

```
CREATE TABLE product2 ( id INT AUTO_INCREMENT PRIMARY KEY, 
	-- 기본키는 자동으로 NOT NULL 
	name VARCHAR(30), -- NOT NULL 옵션이 없으면 NULL값 허용 
	price INT NOT NULL -- price는 NULL 값을 허용하지 않는다 
);
```

**product1**
```
INSERT INTO product(name) 
VALUES('모니터'); 
INSERT INTO product(name, price) 
VALUES('카메라', NULL); 
-- 둘 다 정상적으로 price값은 NULL로 저장된다.
```

**product2**
```
INSERT INTO product2(name) 
VALUES('모니터'); -- ERROR : Field 'price' doesn't have a default value

INSERT INTO product2(name, price)
VALUES('마우스', NULL); -- ERROR : Column 'price' cannot be null
```