# SQL 예제 실행

각 chXX/exYY/example.sql은 초기 데이터까지 포함한 독립 예제입니다. SQLite 3.39 이상에서 동작합니다.

루트 폴더에서:

```powershell
python run_sql.py examples/ch10/ex01/example.sql
python run_sql.py --check-all
```

각 예제 폴더에서는 python ../../../run_sql.py example.sql로 실행할 수 있습니다. 실행기는 메모리 DB만 사용합니다. expected.json은 자동 검사용 기대 결과입니다.
