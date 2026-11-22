---
title: "03. Faster R-CNN과 DenseNet-121 연결"
description: "MobileNetV3-Large, RoI Align, 탐지 헤드와 분류 패치"
---

[이전 · 데이터와 라벨](./02-data-and-labels.md) · [시리즈 목차](https://rpaisxol.github.io/%E5%A4%A7%E5%AD%A6%E9%99%A2%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/a-study-of-strawberry-maturity-classification-using-improved-faster-r-cnn/) · [다음 · 학습과 오류 해결](./04-training-and-debugging.md)

## 탐지기에서 박스 구하기

torchvision의 MobileNetV3-Large FPN Faster R-CNN을 사용했다. 모델은 기본적으로 MultiScaleRoIAlign을 사용하므로 후보 박스의 특징을 읽는 연산을 따로 작성할 필요가 없었다. 사전학습 가중치를 불러온 뒤 COCO 클래스 대신 배경과 딸기를 출력하도록 ROI 헤드를 바꿨다.

~~~python
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

model = fasterrcnn_mobilenet_v3_large_fpn(weights="DEFAULT", weights_backbone=None)
box_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_classes=2)
~~~

Dataset은 COCO 박스의 너비와 높이를 더해 torchvision이 받는 `[x1, y1, x2, y2]` 형태로 바꾼다. 학습에서 사진을 좌우 반전하는 경우에는 좌표도 함께 변환한다. 반전 전 왼쪽과 오른쪽 좌표를 동시에 보존해야 한다.

~~~python
# boxes는 [N, 4] 형태의 float32 텐서다.
boxes[:, [0, 2]] = image_width - boxes[:, [2, 0]]
~~~

## DenseNet-121에 열매 패치 넣기

DenseNet-121의 ImageNet 사전학습 가중치를 이용하고 마지막 선형층을 7개 출력으로 바꿨다. 입력 패치는 224×224 RGB로 바꾸고 ImageNet 통계로 정규화한다.

~~~python
from torch import nn
from torchvision.models import DenseNet121_Weights, densenet121

classifier = densenet121(weights=DenseNet121_Weights.DEFAULT)
classifier.classifier = nn.Linear(classifier.classifier.in_features, 7)
~~~

분류 학습은 정답 박스에서 자른 패치로 시작한다. 추론에서는 탐지기가 예측한 박스를 사용하므로 작게 잘리거나 주변 잎이 포함될 수 있다. 이 차이를 재현하기 위해 정답 박스 분류 점수와 전체 파이프라인 점수를 각각 기록했다.

추론 구현에서는 패치 좌표를 이미지 경계 안으로 제한하고 최대 16개씩 분류한다. 분류를 모두 끝낸 다음 복사한 이미지 위에 박스를 그린다. 예측 박스가 겹칠 때 먼저 그린 박스의 색이 뒤 패치에 섞이는 문제를 이 순서로 해결했다.

~~~python
from dataset import get_classification_transform
from inference import classify_boxes

# original은 그리기 전 PIL RGB 이미지, boxes는 원본 좌표의 [N, 4] 텐서다.
crops, probabilities = classify_boxes(
    original, boxes, classifier, device, get_classification_transform()
)
confidence, labels = probabilities.max(dim=1)
canvas = original.copy()
~~~

[다음 · 학습과 오류 해결](./04-training-and-debugging.md)
