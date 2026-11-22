---
title: "02. LabelMe 데이터와 누락된 673개 라벨"
description: "소형 녹색 클래스 복구, COCO 좌표 변환과 이미지 단위 분할"
---

[이전 · 논문과 문제 정의](./01-paper-and-problem.md) · [시리즈 목차](https://rpaisxol.github.io/%E5%A4%A7%E5%AD%A6%E9%99%A2%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/a-study-of-strawberry-maturity-classification-using-improved-faster-r-cnn/) · [다음 · 모델 연결](./03-detection-and-classification.md)

## 원본 라벨에서 찾은 문제

[KGCV_Strawberry 데이터셋](https://doi.org/10.5281/zenodo.10957909)은 사진과 LabelMe JSON을 함께 제공한다. `random`과 `tagged`를 합칠 때 뒤에 수치가 붙은 라벨은 쉼표 앞의 성숙도 이름만 써야 한다.

초기 변환 코드는 `small green`을 처리했지만 원본의 `small g`는 건너뛰었다. 원본과 변환 후의 클래스별 개수를 비교하자 **소형 녹색 딸기 673개가 모두 빠져 있었다.** 그 결과 분류기는 그 클래스를 한 번도 보지 못했고, 탐지기는 해당 위치를 정답 박스 없이 학습했다.

~~~python
from data_prepare import MATURITY_LABEL_MAP, parse_label

raw_label = "small g, 8.84, 7.62, 0.4"
name = parse_label(raw_label)
if name not in MATURITY_LABEL_MAP:
    raise ValueError(f"지원하지 않는 성숙도 라벨: {raw_label}")

assert name == "small g"
assert MATURITY_LABEL_MAP[name] == 1
~~~

라벨 별칭은 같은 ID를 쓰게 하고, 알 수 없는 라벨은 오류로 처리했다. 변환에 문제가 생기면 클래스 카운트가 정상처럼 보이는 상태로 학습이 진행되는 일을 막을 수 있다.

## 한 박스에서 두 학습 입력 만들기

LabelMe 사각형은 모서리 두 점을 기록한다. 두 점을 정렬하고 사진 경계로 제한한 뒤, 탐지용 COCO JSON에는 `[x, y, w, h]`를 넣는다. 원본의 같은 영역을 잘라 분류용 JPEG 패치로 저장하고 `labels.csv`에 원본 이미지 ID를 함께 기록한다.

~~~python
def labelme_rectangle(points, width, height):
    (ax, ay), (bx, by) = points
    x1, x2 = sorted((ax, bx))
    y1, y2 = sorted((ay, by))
    x1, x2 = (max(0, min(x, width)) for x in (x1, x2))
    y1, y2 = (max(0, min(y, height)) for y in (y1, y2))
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2 - x1, y2 - y1]
~~~

이 예제는 `convert_single_dataset`에 들어 있는 좌표 변환을 함수로 줄여 쓴 것이다. 변환 결과는 사진 1,477장과 유효 박스 3,992개였다. 원본 사각형 3,997개 중 경계 적용 후 면적이 0인 5개를 제외했다.

## 사진 단위로 학습과 검증 나누기

한 사진을 잘라 만든 패치를 임의로 섞으면 같은 배경과 조명이 학습과 검증에 동시에 들어갈 수 있다. 원본 사진을 먼저 나누고, 바이트가 완전히 같은 사진은 같은 그룹에 배정했다. 탐지와 분류는 `splits.json`을 공유한다.

~~~python
import pandas as pd
from training_utils import load_splits

splits = load_splits("dataset_prepared_v2/combined_annotations.json", seed=42)
patches = pd.read_csv("dataset_prepared_v2/labels.csv")
train_rows = patches[patches.image_id.isin(splits["train"])]
val_rows = patches[patches.image_id.isin(splits["val"])]

assert set(train_rows.image_id).isdisjoint(val_rows.image_id)
assert set(train_rows.maturity_class) == set(range(7))
~~~

학습 1,033장, 검증 222장, 테스트 222장이다. 이 분할은 원본 사진과 동일 파일을 기준으로 한다. 촬영 날짜가 다른 같은 식물까지 분리한 일반화 실험을 하려면 식물 ID나 촬영 세션을 기준으로 묶어야 한다.

[다음 · 모델 연결](./03-detection-and-classification.md)
