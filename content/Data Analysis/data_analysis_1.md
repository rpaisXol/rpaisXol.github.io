---
tags:
  - 데이터분석
  - 데이터전처리
  - 파이썬
  - 판다스
title: 데이터 분석에 필요한 기초 용어 및 도구
created: 2026-09-08
status: Version 1.0
---

## 1. 변수

> [!abstract] 알아두기
> * 다양한 값을 지닌 하나의 속성을 변수.
> * 데이터는 변수들의 덩어리라고 할 수 있다. 여러 변수가 모여서 데이터가 된다.
> * 변수는 데이터의 분석 대상이며 데이터 분석은 변수 간의 어떤 관계가 있는지 파악하는 작업

변수
- 다양한 값을 지닌 하나의 속성, 분석의 대상
- 
![[{FA427E95-3C62-4B39-9CD0-D4273B9972C3}.png]]

---

#### **변수 만들기**

```python
a = 1
a 
```
1

```python
b = 2
b 
```
2

```python
c = 3
c 
```
3

```python
d = 3.5
d
```
3.5

#### **변수로 연산하기**

```python
a + b
```
3

```python
a + b + c
```
6

```python
4 / b
```
2.0

```python
5 + b
```
10

#### **여러 값으로 구성된 변수 만들기**

```python
var1 = [1, 2, 3]
var1
```
[1, 2, 3]

```python
var2 = [4, 5, 6]
var2
```
[4, 5, 6]

```python
var1 + var2
```
[1, 2, 3, 4, 5, 6]

```python
a + b
```

#### **문자로 된 변수 만들기**

```python
str1 = 'a'
str1
```
'a'

```python
str2 = 'text'
str2
```
'text'


```python
str3 = 'Hello World'
str3
```
'Hello World'

#### **여러 문자로 된 변수 만들기**

```python
str4 = ['a', 'b', 'c']
str4
```
['a', 'b', 'c']


```python
str5 = ['Hello!', 'World', 'is', 'good!']
str5
```
['Hello!', 'World', 'is', 'good!']


#### **문자 변수 결합하기**

```python
str2 + str3
```
'textHello World'

```python
str2 + ' ' + str3
```
'text Hello World'

## 2. 함수 

> [!abstract] 알아두기
> * 데이터 분석은 함수로 시작해 함수로 끝난다.
> * 함수는 마법 상자 같은 기능을 한다.

![[{8E556243-5466-40CA-8A73-54A90D722FC2} 1.png]]

- 데이터 분석은 함수를 이용해서 변수를 조작하는 일이라고 할 수 있다. 
- 분석 작업은 대부분 함수를 다루는 것으로 시작해 함수를 다루는 것을 끝난다. 
- 데이터 분석을 공부하는 것은 함수의 기능과 조작 방법을 익히는 과정

#### **문자로 된 변수 만들기**

```python
# 변수 만들기
x = [1, 2, 3]
x
```
[1, 2, 3]

```python
# 함수 적용하기
sum(x)
```
6

```python
max(x)
```
3

```python
# 함수 적용하기
min(x)
```
1

#### **함수의 결과물을 새 변수로 만들기**

```python
# 변수 만들기
x_sum = sum(x)
x_sum
```
6

```python
# 함수 적용하기
x_max = max(x)
x_max
```
3

## 3. 패키지

함수가 특정한 기능을 상자에 비유하면, 패키지는 이런 상자가 여러 개 들어있는 꾸러미에 비유

1. 패키지에는 다양한 함수가 들어가 있다.
2. 함수를 사용하려면 패키지 설치가 먼저 선행되야한다.
3. 아나콘다에 주요 패키지 대부분이 들어있음

![[{054F1BE5-6188-4C78-AEDC-8C84E282EF3E}.png]]

```bash
pip install seaborn
```

#### **패키지 로드하기**

```python
import seaborn
```

#### **패키지 함수 사용하기**

```python
var = ['a', 'a', 'b', 'c']
var 
```
['a', 'a', 'b', 'c']

```python
seaborn.countplot(x = var)
```
![[{AA94131A-52C6-4B7C-B198-698D909EBBD2}.png]]

#### **패키지 약어 활용하기**

```python
import seaborn as sns
sns.countplot(x = var)
```
![[{F9E090FE-433C-42BE-AFB6-5F97151CDB9A}.png]]

#### **seaborn의 titanic 데이터로 그래프 만들기**

```python
df = sns.load_dataset('titanic')
df
```
![[{B65860F3-98C5-4B5D-8E15-0221F2E1D1FF}.png]]
