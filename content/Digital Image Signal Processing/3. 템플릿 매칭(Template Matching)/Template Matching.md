---
title: 템플릿 매칭
aliases:
  - Template Matching
  - OpenCV matchTemplate
tags:
  - OpenCV
  - Computer-Vision
  - Image-Processing
  - Template-Matching
created: 2026-08-30
status: 정리완료_ver1
---

# OpenCV 템플릿 매칭

> [!abstract] 학습 목표
> - 템플릿 매칭의 개념과 동작 원리를 이해한다.
> - OpenCV에서 제공하는 6가지 비교 방법의 차이를 이해한다.
> - 비교 결과에서 최적의 위치를 찾는 방법을 익힌다.
> - Python과 OpenCV를 이용하여 템플릿 매칭을 구현한다.

## 목차

1. [[#1. 템플릿 매칭이란?|템플릿 매칭이란?]]
2. [[#2. 템플릿 매칭의 동작 원리|동작 원리]]
3. [[#3. 템플릿 매칭의 장점과 한계|장점과 한계]]
4. [[#4. 특징 공간을 이용한 템플릿 매칭|특징 공간]]
5. [[#5. OpenCV의 6가지 비교 방법|6가지 비교 방법]]
6. [[#6. 최적의 매칭 위치 찾기|매칭 위치 찾기]]
7. [[#7. Python과 OpenCV 실습|OpenCV 실습]]
8. [[#8. 6가지 방법을 한 번에 비교하기|전체 방법 비교]]
9. [[#9. 결과 해석 시 주의 사항|주의 사항]]
10. [[#10. 핵심 정리|핵심 정리]]

---

## 1. 템플릿 매칭이란?

템플릿 매칭(Template Matching)은 **큰 입력 영상 안에서 작은 템플릿 영상과 가장 비슷한 위치를 찾는 방법**이다.

- **입력 영상 $I$**: 찾으려는 물체가 들어 있는 큰 이미지
- **템플릿 영상 $T$**: 큰 이미지 안에서 찾고 싶은 작은 이미지
- **결과 영상 $R$**: 각 위치가 템플릿과 얼마나 비슷한지를 숫자로 나타낸 결과

예를 들어 단체 사진에서 특정 사람의 작은 얼굴 사진을 이용하여 그 사람이 있는 위치를 찾는 것과 비슷하다.

$$
\text{입력 영상 } I + \text{템플릿 } T
\longrightarrow
\text{비교 결과 } R
$$

> [!example] 쉽게 생각하기
> 작은 그림을 큰 그림 위에서 한 칸씩 움직이면서, 가장 비슷하게 겹치는 위치를 찾는 과정이다.

---

## 2. 템플릿 매칭의 동작 원리

템플릿 매칭은 다음 순서로 동작한다.

1. 템플릿을 입력 영상의 왼쪽 위에 놓는다.
2. 템플릿과 겹치는 입력 영상 영역의 픽셀을 비교한다.
3. 비교 결과를 하나의 점수로 계산한다.
4. 템플릿을 오른쪽으로 한 칸 이동하여 다시 비교한다.
5. 한 줄의 비교가 끝나면 아래쪽으로 이동한다.
6. 모든 위치를 비교한 후 가장 좋은 점수를 가진 위치를 찾는다.

현재 위치 $(x,y)$에서의 비교 결과는 다음과 같이 표현할 수 있다.

$$
R(x,y)=\operatorname{compare}
\left(
I(x:x+w,\;y:y+h),\;T
\right)
$$

- $(x,y)$: 템플릿의 현재 왼쪽 위 위치
- $w$: 템플릿의 너비
- $h$: 템플릿의 높이
- $R(x,y)$: 현재 위치에서 계산된 비교 점수

### 결과 영상의 크기

입력 영상의 크기가 $W_I \times H_I$이고 템플릿의 크기가 $W_T \times H_T$라면, 결과 영상의 크기는 다음과 같다.

$$
W_R=W_I-W_T+1
$$

$$
H_R=H_I-H_T+1
$$

따라서 결과 영상 $R$의 크기는 다음과 같다.

$$
(W_I-W_T+1)\times(H_I-H_T+1)
$$

> [!note]
> 결과 영상의 각 픽셀은 실제 색상을 나타내는 것이 아니라, 해당 위치에서 계산된 **차이 또는 유사도 점수**를 나타낸다.

---

## 3. 템플릿 매칭의 장점과 한계

### 3.1 장점

- 구현 방법이 비교적 간단하다.
- 별도의 모델 학습이 필요하지 않다.
- 물체가 입력 영상 안에서 좌우 또는 위아래로 이동해도 찾을 수 있다.
- 물체의 방향과 크기가 일정하면 좋은 결과를 얻을 수 있다.

### 3.2 한계

- 물체가 회전하면 픽셀 배열이 달라져 찾기 어려워진다.
- 물체가 확대되거나 축소되면 템플릿의 크기와 맞지 않는다.
- 조명과 밝기가 크게 달라지면 결과가 부정확해질 수 있다.
- 배경에 비슷한 무늬가 많으면 잘못된 위치를 선택할 수 있다.
- 입력 영상이나 템플릿이 크면 비교 횟수가 증가한다.

회전된 템플릿과 원본 템플릿은 픽셀 배열이 서로 다르다.

$$
T \neq \operatorname{Rotate}(T)
$$

크기가 변경된 템플릿도 원본과 픽셀 배열이 다르다.

$$
T \neq \operatorname{Scale}(T)
$$

> [!warning] 한계점
> - 기본 템플릿 매칭은 **이동(Translation)**에는 대응한다. 
> - 그러나 **회전(Rotation)**과 **크기 변화(Scaling)**에는 강하지 않다.

---

## 4. 특징 공간을 이용한 템플릿 매칭

가장 기본적인 템플릿 매칭은 픽셀의 밝기를 직접 비교한다.

$$
\text{비교 대상}=\text{픽셀의 밝기}
$$

상황에 따라 원본 영상을 다른 특징으로 변환한 후 매칭할 수도 있다.

- **에지(Edge)**: 물체의 경계선
- **코너(Corner)**: 두 개 이상의 선이 만나는 지점
- **색상(Color)**: 물체의 색 정보
- **주파수(Frequency)**: 밝기가 공간적으로 얼마나 빠르게 변하는지를 나타내는 정보

조명이 달라서 픽셀 밝기가 변한 경우에는 원본 영상보다 에지 영상을 사용하는 것이 효과적일 수 있다.

$$
I_{\mathrm{edge}}=\operatorname{Edge}(I)
$$

$$
T_{\mathrm{edge}}=\operatorname{Edge}(T)
$$

$$
R=\operatorname{matchTemplate}
\left(I_{\mathrm{edge}},T_{\mathrm{edge}}\right)
$$

OpenCV에서는 `cv2.Canny()`로 에지를 검출한 후 `cv2.matchTemplate()`을 적용할 수 있다.

```python
import cv2

image = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
template = cv2.imread("template.jpg", cv2.IMREAD_GRAYSCALE)

image_edge = cv2.Canny(image, 100, 200)
template_edge = cv2.Canny(template, 100, 200)

result = cv2.matchTemplate(
    image_edge,
    template_edge,
    cv2.TM_CCOEFF_NORMED,
)
```

---

## 5. OpenCV의 6가지 비교 방법

OpenCV의 `cv2.matchTemplate()`은 총 6가지 비교 방법을 제공한다.

| OpenCV 상수 | 비교 방법 | 최적의 결과 | 일반적인 점수 해석 |
|---|---|---:|---|
| `cv2.TM_SQDIFF` | 제곱 차 | 최솟값 | 작을수록 비슷함 |
| `cv2.TM_SQDIFF_NORMED` | 정규화 제곱 차 | 최솟값 | $0$에 가까울수록 비슷함 |
| `cv2.TM_CCORR` | 교차 상관 | 최댓값 | 클수록 비슷함 |
| `cv2.TM_CCORR_NORMED` | 정규화 교차 상관 | 최댓값 | $1$에 가까울수록 비슷함 |
| `cv2.TM_CCOEFF` | 상관 계수 | 최댓값 | 클수록 비슷함 |
| `cv2.TM_CCOEFF_NORMED` | 정규화 상관 계수 | 최댓값 | $1$에 가까울수록 비슷함 |

> [!important] 최솟값과 최댓값
> - `TM_SQDIFF` 계열은 **가장 작은 값**이 최적의 매칭이다.
> - `TM_CCORR`, `TM_CCOEFF` 계열은 **가장 큰 값**이 최적의 매칭이다.

### 5.1 `cv2.TM_SQDIFF` — 제곱 차

#### 쉬운 설명

- 입력 영상과 템플릿의 같은 위치에 있는 픽셀값을 뺀다.
- 차이를 제곱한 후 모두 더한다.
- 두 영상이 비슷하면 차이가 작다.
- 두 영상이 다르면 차이가 크다.
- 따라서 **가장 작은 결과값을 가진 위치**가 가장 좋은 위치이다.

#### 계산식

$$
R(x,y)=
\sum_{x',y'}
\left[
T(x',y')-I(x+x',y+y')
\right]^2
$$

- $T(x',y')$: 템플릿의 픽셀값
- $I(x+x',y+y')$: 입력 영상의 현재 비교 영역에 있는 픽셀값
- $R(x,y)$: 현재 위치에서 계산된 차이 점수

두 영상이 완전히 같다면 모든 픽셀의 차이가 $0$이 된다.

$$
R(x,y)=0
$$

결과값이 증가할수록 두 영상의 차이가 크다는 뜻이다.

$$
R(x,y)\uparrow
\quad\Longrightarrow\quad
\text{두 영상의 차이가 커짐}
$$

> [!tip] 선택 기준
> `TM_SQDIFF`에서는 `cv2.minMaxLoc()`이 반환한 `min_loc`을 사용한다.

---

### 5.2 `cv2.TM_SQDIFF_NORMED` — 정규화 제곱 차

#### 쉬운 설명

- `TM_SQDIFF`의 제곱 차 결과를 정규화한 방법이다.
- 서로 다른 영상이나 위치의 점수를 비교하기 편하게 만든다.
- $0$에 가까울수록 두 영상이 비슷하다.
- 일반적으로 값이 커질수록 두 영상의 차이가 크다.

#### 계산식

$$
R(x,y)=
\frac{
\displaystyle
\sum_{x',y'}
\left[T(x',y')-I(x+x',y+y')\right]^2
}{
\sqrt{
\displaystyle
\sum_{x',y'}T(x',y')^2
\sum_{x',y'}I(x+x',y+y')^2
}
}
$$

#### 결과 해석

$$
R(x,y)\approx 0
\quad\Longrightarrow\quad
\text{매우 비슷함}
$$

$$
R(x,y)\uparrow
\quad\Longrightarrow\quad
\text{두 영상의 차이가 커짐}
$$

> [!tip] 선택 기준
> `TM_SQDIFF_NORMED`에서도 `min_loc`을 사용한다.

---

### 5.3 `cv2.TM_CCORR` — 교차 상관

#### 쉬운 설명

- 입력 영상과 템플릿의 같은 위치에 있는 픽셀끼리 곱한다.
- 곱한 값을 모두 더한다.
- 두 영상의 밝기 모양이 비슷하면 큰 값이 나온다.
- 따라서 **가장 큰 결과값을 가진 위치**를 선택한다.

#### 계산식

$$
R(x,y)=
\sum_{x',y'}
T(x',y')I(x+x',y+y')
$$

#### 결과 해석

$$
R(x,y)\uparrow
\quad\Longrightarrow\quad
\text{두 영상이 비슷할 가능성이 커짐}
$$

> [!caution]
> 밝은 픽셀끼리 곱하면 값이 크게 증가하기 때문에 영상 전체의 밝기에 영향을 받을 수 있다.

---

### 5.4 `cv2.TM_CCORR_NORMED` — 정규화 교차 상관

#### 쉬운 설명

- `TM_CCORR`의 교차 상관 결과를 정규화한 방법이다.
- 픽셀값의 전체적인 크기를 함께 고려한다.
- 서로 다른 위치에서 얻은 결과를 비교하기 쉽다.
- $1$에 가까울수록 두 영상이 비슷하다.

#### 계산식

$$
R(x,y)=
\frac{
\displaystyle
\sum_{x',y'}T(x',y')I(x+x',y+y')
}{
\sqrt{
\displaystyle
\sum_{x',y'}T(x',y')^2
\sum_{x',y'}I(x+x',y+y')^2
}
}
$$

#### 결과 해석

$$
R(x,y)\approx 1
\quad\Longrightarrow\quad
\text{매우 비슷함}
$$

$$
R(x,y)\approx 0
\quad\Longrightarrow\quad
\text{관련성이 작음}
$$

---

### 5.5 `cv2.TM_CCOEFF` — 상관 계수

#### 쉬운 설명

- 템플릿과 현재 입력 영역에서 각각 평균 밝기를 구한다.
- 각 픽셀값에서 평균 밝기를 뺀다.
- 평균을 제거한 두 영상의 밝기 변화가 얼마나 비슷한지 비교한다.
- 단순한 전체 밝기보다 밝고 어두워지는 **변화의 모양**을 비교한다.
- 가장 큰 결과값을 가진 위치를 선택한다.

#### 평균이 제거된 템플릿

템플릿의 평균 밝기를 $\overline{T}$라고 하면 다음과 같다.

$$
T'(x',y')=T(x',y')-\overline{T}
$$

현재 입력 영역의 평균 밝기를 $\overline{I}_{x,y}$라고 하면 다음과 같다.

$$
I'(x+x',y+y')=
I(x+x',y+y')-\overline{I}_{x,y}
$$

#### 계산식

$$
R(x,y)=
\sum_{x',y'}
T'(x',y')I'(x+x',y+y')
$$

#### 결과 해석

$$
R(x,y)\uparrow
\quad\Longrightarrow\quad
\text{두 영상의 밝기 변화가 비슷함}
$$

> [!warning] 점수 범위 주의
> - `TM_CCOEFF`의 결과값은 반드시 $-1$부터 $1$ 사이가 아님
> - $-1$부터 $1$ 사이의 정규화된 점수는 `TM_CCOEFF_NORMED`에서 얻음

---

### 5.6 `cv2.TM_CCOEFF_NORMED` — 정규화 상관 계수

#### 쉬운 설명

- 템플릿과 입력 영역에서 각각 평균 밝기를 제거한다.
- 평균이 제거된 두 영상의 밝기 변화가 얼마나 비슷한지 계산한다.
- 결과를 정규화하여 해석하기 쉽게 만든다.
- 조명이나 전체 밝기가 어느 정도 달라져도 비교적 안정적이다.
- 일반적인 템플릿 매칭에서 자주 사용하는 방법이다.

#### 계산식

$$
R(x,y)=
\frac{
\displaystyle
\sum_{x',y'}T'(x',y')I'(x+x',y+y')
}{
\sqrt{
\displaystyle
\sum_{x',y'}T'(x',y')^2
\sum_{x',y'}I'(x+x',y+y')^2
}
}
$$

#### 결과 해석

$$
R(x,y)\approx 1
\quad\Longrightarrow\quad
\text{밝기 변화가 매우 비슷함}
$$

$$
R(x,y)\approx 0
\quad\Longrightarrow\quad
\text{뚜렷한 상관관계가 없음}
$$

$$
R(x,y)\approx -1
\quad\Longrightarrow\quad
\text{밝기 변화 방향이 서로 반대임}
$$

> [!tip] 처음 사용할 때의 추천
> - 특별한 조건이 없다면 점수 해석이 쉬운 `cv2.TM_CCOEFF_NORMED`부터 실험해 볼 수 있다. 
> - 다만 템플릿의 픽셀값이 모두 같아 분산이 $0$인 경우에는 상관 계수 방식이 적합하지 않을 수 있다.

---

## 6. 최적의 매칭 위치 찾기

`cv2.matchTemplate()`이 반환하는 것은 사각형 좌표가 아니라 **결과 점수 맵**이다. 최적의 위치는 `cv2.minMaxLoc()`으로 찾는다.

```python
min_value, max_value, min_location, max_location = cv2.minMaxLoc(result)
```

반환값은 다음과 같다.

| 반환값 | 의미 |
|---|---|
| `min_value` | 결과 맵의 최솟값 |
| `max_value` | 결과 맵의 최댓값 |
| `min_location` | 최솟값이 있는 위치 |
| `max_location` | 최댓값이 있는 위치 |

수식으로 표현하면 다음과 같다.

$$
(R_{\min},R_{\max},p_{\min},p_{\max})
=\operatorname{minMaxLoc}(R)
$$

비교 방법에 따라 선택해야 하는 위치가 다르다.

```python
if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
    top_left = min_location
else:
    top_left = max_location
```

- `TM_SQDIFF` 계열: `min_location` 사용
- 나머지 방법: `max_location` 사용

이를 최적화 식으로 표현하면 다음과 같다.

$$
(x^*,y^*)=
\begin{cases}
\displaystyle\operatorname*{arg\,min}_{x,y}R(x,y),
& \text{SQDIFF 계열}\\[6pt]
\displaystyle\operatorname*{arg\,max}_{x,y}R(x,y),
& \text{CCORR 또는 CCOEFF 계열}
\end{cases}
$$

---

## 7. Python과 OpenCV 실습

### 7.1 기본 템플릿 매칭

다음 코드는 `TM_CCOEFF_NORMED`를 사용하여 가장 비슷한 위치를 찾고 사각형으로 표시한다.

```python
from pathlib import Path

import cv2


def load_grayscale_image(path: str) -> cv2.typing.MatLike:
    """이미지를 그레이스케일로 불러오고 실패 여부를 검사한다."""
    image_path = Path(path)
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {image_path}")

    return image


def find_template(
    image: cv2.typing.MatLike,
    template: cv2.typing.MatLike,
) -> tuple[tuple[int, int], float]:
    """TM_CCOEFF_NORMED로 템플릿의 왼쪽 위 위치와 유사도를 반환한다."""
    image_height, image_width = image.shape[:2]
    template_height, template_width = template.shape[:2]

    if template_width > image_width or template_height > image_height:
        raise ValueError("템플릿은 입력 영상보다 클 수 없습니다.")

    result = cv2.matchTemplate(
        image,
        template,
        cv2.TM_CCOEFF_NORMED,
    )

    _, max_value, _, max_location = cv2.minMaxLoc(result)
    return max_location, max_value


def main() -> None:
    image = load_grayscale_image("input.jpg")
    template = load_grayscale_image("template.jpg")

    top_left, similarity = find_template(image, template)

    template_height, template_width = template.shape[:2]
    bottom_right = (
        top_left[0] + template_width,
        top_left[1] + template_height,
    )

    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(
        output,
        top_left,
        bottom_right,
        color=(0, 0, 255),
        thickness=2,
    )

    cv2.putText(
        output,
        f"score: {similarity:.4f}",
        (top_left[0], max(20, top_left[1] - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )

    print(f"최대 유사도: {similarity:.4f}")
    print(f"매칭 시작 위치: {top_left}")

    cv2.imshow("Template Matching", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
```

### 7.2 코드 실행에 필요한 파일 구조

```text
template-matching/
├── input.jpg
├── template.jpg
└── template_matching.py
```

### 7.3 OpenCV 설치

```bash
pip install opencv-python
```

> [!note]
> - `cv2.typing.MatLike`를 인식하지 못하는 구버전 OpenCV에서는 타입 표기를 제거를 혹은 업데이트할 수 있다.
> - 템플릿 매칭 동작 자체에는 영향을 주지 않는다.

---

## 8. 6가지 방법을 한 번에 비교하기

다음 코드는 동일한 입력 영상과 템플릿에 6가지 방법을 모두 적용한다.

```python
from pathlib import Path

import cv2


METHODS = {
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
}


def load_image(path: str) -> cv2.typing.MatLike:
    image = cv2.imread(str(Path(path)), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {path}")
    return image


def select_best_location(
    result: cv2.typing.MatLike,
    method: int,
) -> tuple[tuple[int, int], float]:
    min_value, max_value, min_location, max_location = cv2.minMaxLoc(result)

    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        return min_location, min_value

    return max_location, max_value


def main() -> None:
    image = load_image("input.jpg")
    template = load_image("template.jpg")

    image_height, image_width = image.shape[:2]
    template_height, template_width = template.shape[:2]

    if template_width > image_width or template_height > image_height:
        raise ValueError("템플릿은 입력 영상보다 작거나 같아야 합니다.")

    for method_name, method in METHODS.items():
        result = cv2.matchTemplate(image, template, method)
        top_left, score = select_best_location(result, method)

        bottom_right = (
            top_left[0] + template_width,
            top_left[1] + template_height,
        )

        output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(
            output,
            top_left,
            bottom_right,
            color=(0, 0, 255),
            thickness=2,
        )

        output_path = f"result_{method_name}.jpg"
        cv2.imwrite(output_path, output)

        print(
            f"{method_name:<20} "
            f"location={top_left}, score={score:.6f}, "
            f"saved={output_path}"
        )


if __name__ == "__main__":
    main()
```

> [!important] 점수 직접 비교 금지
> - 6가지 방법은 계산식과 점수 범위가 서로 다르다. 
> - 따라서 `TM_CCORR`의 점수와 `TM_CCOEFF_NORMED`의 점수를 숫자 크기만으로 직접 비교하면 안 된다.

---

## 9. 결과 해석 시 주의 사항

### 9.1 함수와 상수 이름

현재 Python OpenCV에서는 다음 이름을 사용한다.

- `cv2.TM_SQDIFF`
- `cv2.TM_SQDIFF_NORMED`
- `cv2.TM_CCORR`
- `cv2.TM_CCORR_NORMED`
- `cv2.TM_CCOEFF`
- `cv2.TM_CCOEFF_NORMED`

> [!warning] 오타 주의
> - `SQDDIFF`가 아니라 `SQDIFF`이다.
> - `TM_NORMED`라는 독립적인 방법은 없다.
> - 정규화 교차 상관의 정확한 이름은 `TM_CCORR_NORMED`이다.

### 9.2 정규화의 의미

정규화는 서로 다른 크기의 점수를 일정한 기준으로 비교하기 쉽게 만드는 과정이다.

$$
R_{\mathrm{norm}}
=
\frac{R}{\text{픽셀 에너지 또는 크기 기준}}
$$

하지만 정규화를 사용한다고 해서 모든 조명 변화가 완전히 해결되는 것은 아니다. 특히 그림자, 반사광, 부분 가림이 발생하면 매칭 성능이 떨어질 수 있다.

### 9.3 임계값 사용

가장 좋은 위치 하나만 찾는 것이 아니라 동일한 물체를 여러 개 찾으려면 임계값을 사용할 수 있다.

`TM_CCOEFF_NORMED`의 예시는 다음과 같다.

$$
R(x,y)\ge \tau
$$

- $\tau$: 매칭으로 인정할 최소 유사도
- 예: $\tau=0.8$

```python
import cv2
import numpy as np

image = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
template = cv2.imread("template.jpg", cv2.IMREAD_GRAYSCALE)

if image is None or template is None:
    raise FileNotFoundError("입력 영상 또는 템플릿을 불러올 수 없습니다.")

result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8

locations = np.where(result >= threshold)

for x, y in zip(locations[1], locations[0]):
    print(f"매칭 후보: x={x}, y={y}, score={result[y, x]:.4f}")
```

> [!caution]
> - 임계값만 사용하면 하나의 물체 주변에서 여러 개의 겹치는 위치가 검출될 수 있다. 
> - 실제 응용에서는 비최대 억제(Non-Maximum Suppression)나 좌표 군집화로 중복을 제거할 수 있다.

### 9.4 회전과 크기 변화 대응

기본 템플릿 매칭으로 회전이나 크기 변화에 대응하려면 여러 버전의 템플릿을 만들어 반복해서 비교할 수 있다.

$$
T_{s,\theta}
=
\operatorname{Rotate}
\left(
\operatorname{Scale}(T,s),\theta
\right)
$$

- $s$: 크기 비율
- $\theta$: 회전 각도

그러나 비교할 크기와 각도가 많아질수록 계산량이 증가한다. 변화가 큰 환경에서는 ORB, SIFT 같은 특징점 기반 방법이나 객체 탐지 모델을 검토할 수 있다.

---

## 10. 핵심 정리

> [!summary] 핵심 내용
> - 템플릿 매칭은 큰 입력 영상에서 작은 템플릿과 비슷한 위치를 찾는 방법이다.
> - 템플릿을 이동시키면서 각 위치의 차이 또는 유사도 점수를 계산한다.
> - `TM_SQDIFF` 계열은 **최솟값**을 선택한다.
> - `TM_CCORR`와 `TM_CCOEFF` 계열은 **최댓값**을 선택한다.
> - 정규화된 방법은 결과 점수를 해석하고 비교하기 편하다.
> - `TM_CCOEFF_NORMED`는 일반적인 실습에서 자주 사용된다.
> - 기본 템플릿 매칭은 이동에는 대응하지만 회전과 크기 변화에는 취약하다.

제곱 차 계열의 최적 위치는 다음과 같다.

$$
(x^*,y^*)
=
\operatorname*{arg\,min}_{x,y}R(x,y)
$$

교차 상관 및 상관 계수 계열의 최적 위치는 다음과 같다.

$$
(x^*,y^*)
=
\operatorname*{arg\,max}_{x,y}R(x,y)
$$

---

## 참고 자료

- [OpenCV 공식 문서: Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
- [OpenCV 공식 문서: TemplateMatchModes](https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html)

