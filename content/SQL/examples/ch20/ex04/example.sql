-- SQLite 3.39 이상 학습용 독립 예제
PRAGMA foreign_keys = ON;
CREATE TABLE dept (
  dept_id INTEGER PRIMARY KEY,
  dept_name TEXT NOT NULL
);
INSERT INTO dept VALUES (10,'Sales'),(20,'Dev'),(30,'HR'),(40,'Empty');
CREATE TABLE emp (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  dept_id INTEGER REFERENCES dept(dept_id),
  salary INTEGER CHECK(salary >= 0),
  comm INTEGER,
  manager_id INTEGER REFERENCES emp(id)
);
INSERT INTO emp VALUES
 (1,'A',10,1000,NULL,NULL),
 (2,'B',10,1500,100,1),
 (3,'C',20,1500,NULL,1),
 (4,'D',20,2000,200,3),
 (5,'E',NULL,5000,NULL,NULL),
 (6,'F',30,NULL,0,1);
CREATE TABLE bonus(emp_id INTEGER REFERENCES emp(id), amount INTEGER);
INSERT INTO bonus VALUES (2,50),(2,70),(4,100);
CREATE TABLE ta(v INTEGER);
CREATE TABLE tb(v INTEGER);
INSERT INTO ta VALUES (1),(2),(2),(NULL);
INSERT INTO tb VALUES (2),(3),(NULL);

-- 학습 문제 시작
CREATE TABLE required(course INTEGER PRIMARY KEY);
CREATE TABLE took(student INTEGER,course INTEGER);
INSERT INTO required VALUES(10),(20);
INSERT INTO took VALUES(1,10),(1,20),(2,10);
SELECT DISTINCT t.student FROM took t WHERE NOT EXISTS
 (SELECT 1 FROM required r WHERE NOT EXISTS
  (SELECT 1 FROM took x WHERE x.student=t.student AND x.course=r.course))
ORDER BY t.student;
