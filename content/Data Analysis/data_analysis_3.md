---
tags:
  - 데이터분석
  - 데이터전처리
  - 파이썬
  - 판다스
title: 3. 데이터 파악하기, 다루게 쉽게 수정하기
created: 2026-09-08
status: Version 1.0
---
> [!abstract] 알아두기
> * 데이터가 주어졌을 때 가장 먼저 하는 일은 데이터의 전반적인 구조를 파악하는 것
> * 어떤 변수들이 있는지, 몇 행으로 구성되는지 구조를 살피면서 데이터 특징이 어떠한지 파악

---
## 1. 데이터 파악하기

데이터를 파악할 때 명령어

| 함수          | 기능               |
| ----------- | ---------------- |
| head()      | 앞부분 출력           |
| tail()      | 뒷부분 출력           |
| shape       | 행, 열 개수 출력       |
| info()      | 변수 속성 출력         |
| describe()  | 요약 통계량 출력        |

```python
import pandas as pd
exam = pd.read_csv('exam.csv')
```

|     | id  | nclass | math | english | science |
| --- | --- | ------ | ---- | ------- | ------- |
| 0   | 1   | 1      | 50   | 98      | 50      |
| 1   | 2   | 1      | 60   | 97      | 60      |
| 2   | 3   | 1      | 45   | 86      | 78      |
| 3   | 4   | 1      | 30   | 98      | 58      |
| 4   | 5   | 2      | 25   | 80      | 65      |
| 5   | 6   | 2      | 50   | 89      | 98      |
| 6   | 7   | 2      | 80   | 90      | 45      |
| 7   | 8   | 2      | 90   | 78      | 25      |
| 8   | 9   | 3      | 20   | 98      | 15      |
| 9   | 10  | 3      | 50   | 98      | 45      |
| 10  | 11  | 3      | 65   | 65      | 65      |
| 11  | 12  | 3      | 45   | 85      | 32      |
| 12  | 13  | 4      | 46   | 98      | 65      |
| 13  | 14  | 4      | 48   | 87      | 12      |
| 14  | 15  | 4      | 75   | 56      | 78      |
| 15  | 16  | 4      | 58   | 98      | 65      |
| 16  | 17  | 5      | 65   | 68      | 98      |
| 17  | 18  | 5      | 80   | 78      | 90      |
| 18  | 19  | 5      | 89   | 68      | 87      |
| 19  | 20  | 5      | 78   | 83      | 58      |
#### head - 데이터 앞부분 파악하기

- head()는 데이터의 앞에서부터 다섯 번째 행까지 출력하는 기능
- 데이터의 앞부분을 일부 출력하면 데이터의 형태 쉽게 확인

```python
exam.head()  # 앞에서부터 5행까지 출력
```

|     | id  | nclass | math | english | science |
| --- | --- | ------ | ---- | ------- | ------- |
| 0   | 1   | 1      | 50   | 98      | 50      |
| 1   | 2   | 1      | 60   | 97      | 60      |
| 2   | 3   | 1      | 45   | 86      | 78      |
| 3   | 4   | 1      | 30   | 98      | 58      |
| 4   | 5   | 2      | 25   | 80      | 65      |

```python
exam.head(10)  # 앞에서부터 10행까지 출력
```

|     | id  | nclass | math | english | science |
| --- | --- | ------ | ---- | ------- | ------- |
| 0   | 1   | 1      | 50   | 98      | 50      |
| 1   | 2   | 1      | 60   | 97      | 60      |
| 2   | 3   | 1      | 45   | 86      | 78      |
| 3   | 4   | 1      | 30   | 98      | 58      |
| 4   | 5   | 2      | 25   | 80      | 65      |
| 5   | 6   | 2      | 50   | 89      | 98      |
| 6   | 7   | 2      | 80   | 90      | 45      |
| 7   | 8   | 2      | 90   | 78      | 25      |
| 8   | 9   | 3      | 20   | 98      | 15      |
| 9   | 10  | 3      | 50   | 98      | 45      |

#### tail() - 데이터 뒷부분 확인하기

- 데이터의 뒷부분을 출력하는 기능

```python
exam.tail()  # 뒤에서부터 5행까지 출력
```

|     | id  | nclass | math | english | science |
| --- | --- | ------ | ---- | ------- | ------- |
| 15  | 16  | 4      | 58   | 98      | 65      |
| 16  | 17  | 5      | 65   | 68      | 98      |
| 17  | 18  | 5      | 80   | 78      | 90      |
| 18  | 19  | 5      | 89   | 68      | 87      |
| 19  | 20  | 5      | 78   | 83      | 58      |

```python
exam.tail(10)  # 뒤에서부터 10행까지 출력
```

|     | id  | nclass | math | english | science |
| --- | --- | ------ | ---- | ------- | ------- |
| 10  | 11  | 3      | 65   | 65      | 65      |
| 11  | 12  | 3      | 45   | 85      | 32      |
| 12  | 13  | 4      | 46   | 98      | 65      |
| 13  | 14  | 4      | 48   | 87      | 12      |
| 14  | 15  | 4      | 75   | 56      | 78      |
| 15  | 16  | 4      | 58   | 98      | 65      |
| 16  | 17  | 5      | 65   | 68      | 98      |
| 17  | 18  | 5      | 80   | 78      | 90      |
| 18  | 19  | 5      | 89   | 68      | 87      |
| 19  | 20  | 5      | 78   | 83      | 58      |

#### shape - 데이터가 몇 행, 몇 열로 구성되는지 알아보기

- 데이터 프레임의 크기를 알아볼 때 사용
- 데이터 프레임에 점을 찍고 shape를 추가하면 데이터 프레임의 행, 열 개수를 출력
- shape는 함수가 아니라 데이터 프레임이 가지고 있는 속성인 어트리뷰트이다.
- 명령어 뒤엔 괄호를 입력하지 않는다.

```python
exam.shape # (20, 5), 20행 5열
```

```text
(20, 5)
```

```python
# 판다스 패키지 호출하기
import pandas as pd

# 데이터 프레임 만들기
df = pd.DataFrame({'name'    : ['김지훈', '이유진', '박동현', '김민지'],
                   'english' : [90, 80, 60, 70],
                   'math'    : [50, 60, 100, 20]})

df
```

|     | name | english | math |
| --- | ---- | ------: | ---: |
| 0   | 김지훈  |      90 |   50 |
| 1   | 이유진  |      80 |   60 |
| 2   | 박동현  |      60 |  100 |
| 3   | 김민지  |      70 |   20 |

#### info - 속성 파악하기

```python
exam.info()
```

```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 20 entries, 0 to 19
Data columns (total 5 columns):
 #   Column   Non-Null Count  Dtype
---  ------   --------------  -----
 0   id       20 non-null     int64
 1   nclass   20 non-null     int64
 2   math     20 non-null     int64
 3   english  20 non-null     int64
 4   science  20 non-null     int64
dtypes: int64(5)
memory usage: 928.0 bytes
```

- 여기서 데이터 프레임에 대한 여러가지 속성 값들을 한 눈에 파악이 가능
- Non-null Count는 결측치를 제외하고 구한 값의 개수를 나타냄

#### describe() - 요약 통계랑 구하기

- 평균처럼 변수의 값을 요약한 요약 통계량을 구하는 함수
- 문자로 된 변수의 요약 통계량을 함께 출력하려면 describe()에 include='all'를 입력

```python
exam.describe()
```

|       | id       | nclass    | math      | english   | science   |
| ----- | -------- | --------- | --------- | --------- | --------- |
| count | 20.00000 | 20.000000 | 20.000000 | 20.000000 | 20.000000 |
| mean  | 10.50000 | 3.000000  | 57.450000 | 84.900000 | 59.450000 |
| std   | 5.91608  | 1.450953  | 20.299015 | 12.875517 | 25.292968 |
| min   | 1.00000  | 1.000000  | 20.000000 | 56.000000 | 12.000000 |
| 25%   | 5.75000  | 2.000000  | 45.750000 | 78.000000 | 45.000000 |
| 50%   | 10.50000 | 3.000000  | 54.000000 | 86.500000 | 62.500000 |
| 75%   | 15.25000 | 4.000000  | 75.750000 | 98.000000 | 78.000000 |
| max   | 20.00000 | 5.000000  | 90.000000 | 98.000000 | 98.000000 |

| 출력값   | 통계량                      | 설명                         |
| ----- | ------------------------ | -------------------------- |
| count | 빈도(frequency)            | 값의 개수                      |
| mean  | 평균(mean)                 | 모든 값을 더해 값의 개수로 나눔         |
| std   | 표준편차(standard deviation) | 변수의 값들이 평균에서 떨어진 정도를 나타낸 값 |
| min   | 최소값(minimum)             | 가장 작은 값                    |
| 25%   | 1사분위수(1st quantile)      | 하위 25% 지점에 위치한 값           |
| 50%   | 중앙값(median)              | 하위 50% 지점에 위치한 값           |
| 75%   | 3사분위수(3rd quentile)      | 하위 75% 지점에 위치한 값           |
| max   | 최대값(maximum)             | 가장 큰 값                     |
#### **mpg 데이터 파악하기**

- 실제 데이터를 불러와 데이터 특징 파악하기
- mpg는 미국 환경 보호국에서 공개한 데이터, 1999~2008년 미국에 출시된 자동차 234종 정보

```python
# mpg 데이터 불러오기
mpg = pd.read_csv('mpg.csv')
```

```python
mpg.head()  # mpg 앞부분 확인
```

|     | manufacturer | model | displ | year | cyl | trans      | drv | cty | hwy | fl  | category |
| --- | ------------ | ----- | ----- | ---- | --- | ---------- | --- | --- | --- | --- | -------- |
| 0   | audi         | a4    | 1.8   | 1999 | 4   | auto(l5)   | f   | 18  | 29  | p   | compact  |
| 1   | audi         | a4    | 1.8   | 1999 | 4   | manual(m5) | f   | 21  | 29  | p   | compact  |
| 2   | audi         | a4    | 2.0   | 2008 | 4   | manual(m6) | f   | 20  | 31  | p   | compact  |
| 3   | audi         | a4    | 2.0   | 2008 | 4   | auto(av)   | f   | 21  | 30  | p   | compact  |
| 4   | audi         | a4    | 2.8   | 1999 | 6   | auto(l5)   | f   | 16  | 26  | p   | compact  |

```python
mpg.tail()  # mpg 뒷부분 확인
```

|     | manufacturer | model  | displ | year | cyl | trans      | drv | cty | hwy | fl  | category |
| --- | ------------ | ------ | ----- | ---- | --- | ---------- | --- | --- | --- | --- | -------- |
| 229 | volkswagen   | passat | 2.0   | 2008 | 4   | auto(s6)   | f   | 19  | 28  | p   | midsize  |
| 230 | volkswagen   | passat | 2.0   | 2008 | 4   | manual(m6) | f   | 21  | 29  | p   | midsize  |
| 231 | volkswagen   | passat | 2.8   | 1999 | 6   | auto(l5)   | f   | 16  | 26  | p   | midsize  |
| 232 | volkswagen   | passat | 2.8   | 1999 | 6   | manual(m5) | f   | 18  | 26  | p   | midsize  |
| 233 | volkswagen   | passat | 3.6   | 2008 | 6   | auto(s6)   | f   | 17  | 26  | p   | midsize  |

```python
mpg.shape  # 행, 열 출력
```

```text
(234, 11)
```

```python
mpg.info()  # 데이터 속성 확인
```

```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 234 entries, 0 to 233
Data columns (total 11 columns):
 #   Column        Non-Null Count  Dtype  
---  ------        --------------  -----  
 0   manufacturer  234 non-null    object 
 1   model         234 non-null    object 
 2   displ         234 non-null    float64
 3   year          234 non-null    int64  
 4   cyl           234 non-null    int64  
 5   trans         234 non-null    object 
 6   drv           234 non-null    object 
 7   cty           234 non-null    int64  
 8   hwy           234 non-null    int64  
 9   fl            234 non-null    object 
 10  category      234 non-null    object 
dtypes: float64(1), int64(4), object(6)
memory usage: 20.2+ KB
```

```python
mpg.describe()  # 요약 통계량 출력
```

|       | displ      | year        | cyl        | cty        | hwy        |
| ----- | ---------- | ----------- | ---------- | ---------- | ---------- |
| count | 234.000000 | 234.000000  | 234.000000 | 234.000000 | 234.000000 |
| mean  | 3.471795   | 2003.500000 | 5.888889   | 16.858974  | 23.440171  |
| std   | 1.291959   | 4.509646    | 1.611534   | 4.255946   | 5.954643   |
| min   | 1.600000   | 1999.000000 | 4.000000   | 9.000000   | 12.000000  |
| 25%   | 2.400000   | 1999.000000 | 4.000000   | 14.000000  | 18.000000  |
| 50%   | 3.300000   | 2003.500000 | 6.000000   | 17.000000  | 24.000000  |
| 75%   | 4.600000   | 2008.000000 | 8.000000   | 19.000000  | 27.000000  |
| max   | 7.000000   | 2008.000000 | 8.000000   | 35.000000  | 44.000000  |

```python
mpg.describe(include = 'all')  # 문자 변수 요약 통계량 함께 출력
```

|        | manufacturer | model       | displ      | year        | cyl        | trans    | drv | cty        | hwy        | fl  | category |
| ------ | ------------ | ----------- | ---------- | ----------- | ---------- | -------- | --- | ---------- | ---------- | --- | -------- |
| count  | 234          | 234         | 234.000000 | 234.000000  | 234.000000 | 234      | 234 | 234.000000 | 234.000000 | 234 | 234      |
| unique | 15           | 38          | NaN        | NaN         | NaN        | 10       | 3   | NaN        | NaN        | 5   | 7        |
| top    | dodge        | caravan 2wd | NaN        | NaN         | NaN        | auto(l4) | f   | NaN        | NaN        | r   | suv      |
| freq   | 37           | 11          | NaN        | NaN         | NaN        | 83       | 106 | NaN        | NaN        | 168 | 62       |
| mean   | NaN          | NaN         | 3.471795   | 2003.500000 | 5.888889   | NaN      | NaN | 16.858974  | 23.440171  | NaN | NaN      |
| std    | NaN          | NaN         | 1.291959   | 4.509646    | 1.611534   | NaN      | NaN | 4.255946   | 5.954643   | NaN | NaN      |
| min    | NaN          | NaN         | 1.600000   | 1999.000000 | 4.000000   | NaN      | NaN | 9.000000   | 12.000000  | NaN | NaN      |
| 25%    | NaN          | NaN         | 2.400000   | 1999.000000 | 4.000000   | NaN      | NaN | 14.000000  | 18.000000  | NaN | NaN      |
| 50%    | NaN          | NaN         | 3.300000   | 2003.500000 | 6.000000   | NaN      | NaN | 17.000000  | 24.000000  | NaN | NaN      |
| 75%    | NaN          | NaN         | 4.600000   | 2008.000000 | 8.000000   | NaN      | NaN | 19.000000  | 27.000000  | NaN | NaN      |
| max    | NaN          | NaN         | 7.000000   | 2008.000000 | 8.000000   | NaN      | NaN | 35.000000  | 44.000000  | NaN | NaN      |

## 2. 변수명 바꾸기

- 데이터의 전반적인 특징을 파악 -> 분석 전에 변수명을 바꾸는 작업을 진행
- 변수명을 이해하기 쉽게 바꾸면 데이터를 더 수월하게 다루기 쉬움

### 변수명 바꾸기

#### 1. 데이터 프레임 바꾸기

```python
df_raw = pd.DataFrame({'var1' : [1, 2, 1],
                       'var2' : [2, 3, 2]})
df_raw
```

|     | var1 | var2 |
| --- | ---- | ---- |
| 0   | 1    | 2    |
| 1   | 2    | 3    |
| 2   | 1    | 2    |
#### 2. 데이터 프레임 복사본 만들기

```python
df_new = df_raw.copy()  # 복사본 만들기
df_new                  # 출력
```

|     | var1 | var2 |
| --- | ---- | ---- |
| 0   | 1    | 2    |
| 1   | 2    | 3    |
| 2   | 1    | 2    |
#### 3. 변수명 바꾸기

```python
df_new = df_new.rename(columns = {'var2' : 'v2'})  # var2를 v2로 수정
df_new
df_raw
```

|     | var1 | v2  |
| --- | ---- | --- |
| 0   | 1    | 2   |
| 1   | 2    | 3   |
| 2   | 1    | 2   |

|     | var1 | var2 |
| --- | ---- | ---- |
| 0   | 1    | 2    |
| 1   | 2    | 3    |
| 2   | 1    | 2    |

## 3. 파생변수 만들기

- 데이터에 들어 있는 변수도 포함해서, 변수를 조합하거나 함수를 이용해 새 변수를 만들어 분석할 수 있다.
- 이처럼 기존의 변수를 변형해 만든 변수를 파생변수라고 한다.

### 변수 조합해 파생변수 만들기

```python
df = pd.DataFrame({'var1' : [4, 3, 8],
                   'var2' : [2, 6, 1]})
df
```

|     | var1 | var2 |
| --- | ---- | ---- |
| 0   | 4    | 2    |
| 1   | 3    | 6    |
| 2   | 8    | 1    |

```python
df['var_sum'] = df['var1'] + df['var2']  # var_sum 파생변수 만들기
df
```

|     | var1 | var2 | var_sum |
| --- | ---- | ---- | ------- |
| 0   | 4    | 2    | 6       |
| 1   | 3    | 6    | 9       |
| 2   | 8    | 1    | 9       |

```python
df['var_mean'] = (df['var1'] + df['var2']) / 2  # var_mean 파생변수 만들기
df
```

|     | var1 | var2 | var_sum | var_mean |
| --- | ---- | ---- | ------- | -------- |
| 0   | 4    | 2    | 6       | 3.0      |
| 1   | 3    | 6    | 9       | 4.5      |
| 2   | 8    | 1    | 9       | 4.5      |

### mpg 통합 연비 변수 만들기

```python
mpg['total'] = (mpg['cty'] + mpg['hwy']) / 2  # 통합 연비 변수 만들기
mpg.head()
```

|     | manufacturer | model | displ | year | cyl | trans      | drv | cty | hwy | fl  | category | total |
| --- | ------------ | ----- | ----- | ---- | --- | ---------- | --- | --- | --- | --- | -------- | ----- |
| 0   | audi         | a4    | 1.8   | 1999 | 4   | auto(l5)   | f   | 18  | 29  | p   | compact  | 23.5  |
| 1   | audi         | a4    | 1.8   | 1999 | 4   | manual(m5) | f   | 21  | 29  | p   | compact  | 25.0  |
| 2   | audi         | a4    | 2.0   | 2008 | 4   | manual(m6) | f   | 20  | 31  | p   | compact  | 25.5  |
| 3   | audi         | a4    | 2.0   | 2008 | 4   | auto(av)   | f   | 21  | 30  | p   | compact  | 25.5  |
| 4   | audi         | a4    | 2.8   | 1999 | 6   | auto(l5)   | f   | 16  | 26  | p   | compact  | 21.0  |

```python
sum(mpg['total']) / len(mpg)  # total 합계를 행 수로 나누기
```

```text
20.14957264957265
```

### 조건문을 활용해 파생변수 만들기

#### 1. 기준값 정하기

```python
mpg['total'].describe()  # 요약 통계량 출력
```

```text
count    234.000000
mean      20.149573
std        5.050290
min       10.500000
25%       15.500000
50%       20.500000
75%       23.500000
max       39.500000
Name: total, dtype: float64
```

```python
# 그래프 만들기
mpg['total'].plot.hist()
```

![[data_analysis_3-1795267445618.webp]]

#### 2. 합격 판정 변수 만들기

```python
import numpy as np
# 20 이상이면 pass, 그렇지 않으면 fail 부여
mpg['test'] = np.where(mpg['total'] >= 20, 'pass', 'fail')
mpg.head()
```

|     | manufacturer | model | displ | year | cyl | trans      | drv | cty | hwy | fl  | category | total | test |
| --- | ------------ | ----- | ----- | ---- | --- | ---------- | --- | --- | --- | --- | -------- | ----- | ---- |
| 0   | audi         | a4    | 1.8   | 1999 | 4   | auto(l5)   | f   | 18  | 29  | p   | compact  | 23.5  | pass |
| 1   | audi         | a4    | 1.8   | 1999 | 4   | manual(m5) | f   | 21  | 29  | p   | compact  | 25.0  | pass |
| 2   | audi         | a4    | 2.0   | 2008 | 4   | manual(m6) | f   | 20  | 31  | p   | compact  | 25.5  | pass |
| 3   | audi         | a4    | 2.0   | 2008 | 4   | auto(av)   | f   | 21  | 30  | p   | compact  | 25.5  | pass |
| 4   | audi         | a4    | 2.8   | 1999 | 6   | auto(l5)   | f   | 16  | 26  | p   | compact  | 21.0  | pass |

#### 3. 빈도표로 합격 판정 자동차 수 살펴보기

```python
mpg['test'].value_counts()  # 연비 합격 빈도표 만들기
```

```text
pass    128
fail    106
Name: test, dtype: int64
```

#### **막대 그래프 빈도 표현하기**

```python
count_test = mpg['test'].value_counts()  # 연비 합격 빈도표를 변수에 할당
count_test.plot.bar()  # 연비 합격 빈도 막대 그래프 만들기
```

![[data_analysis_3-1795267602828.webp]]

#### **축 이름 회전하기**

```python
count_test.plot.bar(rot = 0)  # 축 이름 수평으로 만들기
```

![[data_analysis_3-1795267649876.webp]]

### **중첩 조건문 활용하기**

#### **1. 연비 등급 변수 만들기**

```python
# total 기준으로 A, B, C 등급 부여
mpg['grade'] = np.where(mpg['total'] >= 30, 'A',
               np.where(mpg['total'] >= 20, 'B', 'C'))
               
# 데이터 확인
mpg.head()
```

|     | manufacturer | model | displ | year | cyl | trans      | drv | cty | hwy | fl  | category | total | test | grade |
| --- | ------------ | ----- | ----- | ---- | --- | ---------- | --- | --- | --- | --- | -------- | ----- | ---- | ----- |
| 0   | audi         | a4    | 1.8   | 1999 | 4   | auto(l5)   | f   | 18  | 29  | p   | compact  | 23.5  | pass | B     |
| 1   | audi         | a4    | 1.8   | 1999 | 4   | manual(m5) | f   | 21  | 29  | p   | compact  | 25.0  | pass | B     |
| 2   | audi         | a4    | 2.0   | 2008 | 4   | manual(m6) | f   | 20  | 31  | p   | compact  | 25.5  | pass | B     |
| 3   | audi         | a4    | 2.0   | 2008 | 4   | auto(av)   | f   | 21  | 30  | p   | compact  | 25.5  | pass | B     |
| 4   | audi         | a4    | 2.8   | 1999 | 6   | auto(l5)   | f   | 16  | 26  | p   | compact  | 21.0  | pass | B     |

#### 2. 빈도표와 막대 그래프로 연비 등급 살펴보기

```python
count_grade = mpg['grade'].value_counts()  # 등급 빈도표 만들기
count_grade
```

```text
B    118
C    106
A     10
Name: grade, dtype: int64
```

```python
count_grade.plot.bar(rot = 0)  # 등급 빈도 막대 그래프 만들기
```

![[data_analysis_3-1795267773518.webp]]

#### 알파벳순으로 막대 정렬하기

```python
# 등급 빈도표 알파벳순 정렬
count_grade = mpg['grade'].value_counts().sort_index()
count_grade
```

```text
A     10
B    118
C    106
Name: grade, dtype: int64
```

```python
# 등급 빈도 막대 그래프 만들기
count_grade.plot.bar(rot = 0)
```

![[data_analysis_3-1795268791728.webp]]

### 메서드 체이닝

- mpg['grade'].value_counts().sort_index()와 같이 점을 이용해 메서드를 계속 이어서 작성하는 방법을 메서드 체이닝이라고 함
- 변수에 여러 메서드를 순서대로 적용할 수 있으므로 출력 결과에 변수에 할당하고 다시 불러오는 작업을 반복하지 않아도 됨

```python
# 출력 결과를 변수에 할당하는 방법
df = mpg['grade']
df = df.value_counts()
df = df.sort_index()
```

```python
# 메서드 체이닝
df = mpg['grade'].value_counts().sort_index()
```

#### 필요한 만큼 범주 만들기

```python
# A, B, C, D 등급 변수 만들기
mpg['grade2'] = np.where(mpg['total'] >= 30, 'A',
                np.where(mpg['total'] >= 25, 'B',
                np.where(mpg['total'] >= 20, 'C', 'D')))
```

### 목록에 해당하는 행으로 변수 만들기

```python
mpg['size'] = np.where((mpg['category'] == 'compact') |
                       (mpg['category'] == 'subcompact') |
                       (mpg['category'] == '2seater'),
                       'small', 'large')
mpg['size'].value_counts()
```

```text
large    147
small     87
Name: size, dtype: int64
```

```python
mpg['size'] = np.where(mpg['category'].isin(['compact', 'subcompact', '2seater']), 'small', 'large')

mpg['size'].value_counts()
```

```text
large    147
small     87
Name: size, dtype: int64
```


#### 한 눈에 정리하기

```python
# 1. 패키지 로드
import pandas as pd
import numpy as np

# 2. 데이터 불러오기
mpg = pd.read_csv('mpg.csv')

# 3. 데이터 파악하기
mpg.head()      # 데이터 앞부분
mpg.tail()      # 데이터 뒷부분
mpg.shape       # 행, 열 수
mpg.info()      # 속성
mpg.describe()  # 요약 통계량

# 4. 변수명 바꾸기
mpg = mpg.rename(columns = {'manufacturer' : 'company'})

# 5. 파생변수 만들기
mpg['total'] = (mpg['cty'] + mpg['hwy'])/2                  # 변수 조합
mpg['test'] = np.where(mpg['total'] >= 20, 'pass', 'fail')  # 조건문 활용

# 6. 빈도 확인하기
count_test = mpg['test'].value_counts()  # 빈도표 만들기
count_test.plot.bar(rot = 0)             # 빈도 막대 그래프 만들기
```