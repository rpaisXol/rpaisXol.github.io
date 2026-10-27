# -*- coding: utf-8 -*-
# 영상 불러오기와 픽셀 확인부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: 영상 불러오기와 픽셀 확인
# BGR 순서로 읽은 배열에서 [y, x] 위치의 값을 확인하고 RGB로 표시한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT = Path.cwd()
ASSETS = ROOT / 'assets'
path = ASSETS / 'Lenna.png'
if not path.exists():
    raise FileNotFoundError('노트북과 같은 폴더의 assets/Lenna.png를 확인하세요.')
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
if img is None:
    raise ValueError('이미지 디코딩 실패')

# 비교 그림의 배치를 통일하고, 영상 또는 결과 배열을 화면에 표시한다.
def panel(items, cols=3):
    rows = (len(items) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows), squeeze=False)
    for ax, (title, image) in zip(axes.flat, items):
        if image.ndim == 2:
            ax.imshow(image, cmap='gray', vmin=0, vmax=255)
        else:
            ax.imshow(image)
        ax.set_title(title)
        ax.axis('off')
    for ax in list(axes.flat)[len(items):]:
        ax.axis('off')
    fig.tight_layout()
    plt.show()

# shape는 (높이, 너비) 순서다. 좌표 (x, y)로 읽을 때는 배열 인덱스 [y, x]와 구분한다.
h, w = img.shape[:2]
x, y = 120, 120
print('OpenCV:', cv2.__version__)
print('shape:', img.shape, 'dtype:', img.dtype)
print('(x, y):', (x, y), 'BGR:', img[y, x].tolist())
plt.figure(figsize=(4, 4))
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.scatter([x], [y], c='lime', marker='+')
plt.title('Pixel at (120, 120)')
plt.show()

# 셀 2: 8×8 픽셀 영역 확대
# 그레이스케일 값은 0~255로 표시하며, 배열의 끝 인덱스는 포함하지 않는다.

# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 선택 영역을 독립 사본으로 만들어 원본과의 메모리 공유를 끊는다.
patch = gray[y:y+8, x:x+8].copy()
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(patch, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
for row in range(8):
    for col in range(8):
        value = int(patch[row, col])
        ax.text(col, row, str(value), ha='center', va='center',
                color='white' if value < 128 else 'black')
ax.set_xticks(range(8), range(x, x+8))
ax.set_yticks(range(8), range(y, y+8))
ax.set_xlabel('x (column)')
ax.set_ylabel('y (row)')
ax.set_title('8 x 8 grayscale pixels')
fig.tight_layout()
plt.show()
print('Gray at (120, 120):', int(gray[y, x]))

# 셀 3: 밝기 덧셈과 자료형
# 넓은 정수형으로 계산한 뒤 0~255로 제한하여 uint8 값의 순환을 막는다.

# int16에서 밝기를 더하고 0~255로 자른 뒤 uint8로 되돌린다.
bright = np.clip(img.astype(np.int16) + 30, 0, 255).astype(np.uint8)
sample = np.array([240], dtype=np.uint8)
print('uint8 240 + 30:', (sample + np.uint8(30)).tolist())
print('범위 제한:', np.clip(sample.astype(np.int16) + 30, 0, 255).tolist())
panel([('Original', cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
       ('Add 30 with clipping', cv2.cvtColor(bright, cv2.COLOR_BGR2RGB))], cols=2)

# 셀 4: BGR과 RGB의 표시 차이
# 채널의 수치는 유지하고 순서만 바꾸며, 왕복 변환이 원본과 같은지 확인한다.

# Matplotlib은 RGB 순서로 해석하므로 BGR의 빨강·파랑 위치를 바꾼다.
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
panel([('Correct: RGB display', rgb), ('Wrong: BGR as RGB', img)], cols=2)
print('BGR:', img[y, x].tolist(), 'RGB:', rgb[y, x].tolist())
assert np.array_equal(img, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))

# 셀 5: 그레이스케일 변환
# 색을 가중합으로 밝기 하나로 줄인다. 다시 3채널로 늘려도 원래 색은 복원되지 않는다.

# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Gray 값을 세 채널에 복제한다. 원래의 색 정보가 복원되는 것은 아니다.
gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
panel([('Original RGB', rgb), ('Grayscale', gray), ('Gray to RGB', gray_rgb)])
B, G, R = img[y, x].astype(float)
print('가중합:', 0.299*R + 0.587*G + 0.114*B)
print('OpenCV Gray:', int(gray[y, x]), 'shape:', gray.shape)
print('Gray to RGB:', gray_rgb[y, x].tolist())

# 셀 6: YCrCb 변환과 왕복 오차
# Y는 밝기 성분, Cr·Cb는 색차 성분이며 8비트 변환에는 반올림 오차가 생길 수 있다.

# 밝기 성분 Y와 색차 성분 Cr·Cb를 분리할 수 있는 표현으로 변환한다.
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
# OpenCV의 반환 순서는 Y, Cr, Cb이다. 각 채널은 높이×너비 배열이다.
Y, Cr, Cb = cv2.split(ycrcb)
back = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
# uint8끼리 빼면 값이 순환할 수 있어 부호 있는 정수형으로 바꿔 차이를 계산한다.
error = np.abs(img.astype(np.int16) - back.astype(np.int16))
panel([('Y: luma', Y), ('Cr: red difference', Cr), ('Cb: blue difference', Cb)])
print('YCrCb pixel:', ycrcb[y, x].tolist())
print('왕복 최대 절대 오차:', int(error.max()))
print('왕복 평균 절대 오차:', float(error.mean()))

# 셀 7: 채널 분리와 시각화
# 각 성분을 회색으로 표시한 결과와 다른 성분을 0으로 둔 컬러 표시를 비교한다.

# BGR 입력을 파랑·초록·빨강 순서의 세 단일 채널 배열로 분리한다.
b, g, r = cv2.split(img)
zero = np.zeros_like(b)
# 아래 컬러 배열은 Matplotlib에서 표시하므로 RGB 순서다.
panel([('B values', b), ('G values', g), ('R values', r),
       ('Blue only', cv2.merge([zero, zero, b])),
       ('Green only', cv2.merge([zero, g, zero])),
       ('Red only', cv2.merge([r, zero, zero]))])
print('분리한 배열:', b.shape, g.shape, r.shape)

# 셀 8: 채널 병합과 배열의 메모리 공유
# 같은 순서로 병합하면 원본이 복원되고, 슬라이싱 뷰와 copy는 수정 영향이 다르다.

# 분리할 때와 같은 B, G, R 순서로 합쳐 원본 배열을 복원한다.
merged = cv2.merge([b, g, r])
# 채널 순서를 바꾼 비교용 배열이다. merge는 색의 의미를 자동으로 판단하지 않는다.
wrong_order = cv2.merge([r, g, b])
assert np.array_equal(img, merged)
print('같은 순서로 병합하면 원본과 같음:', np.array_equal(img, merged))
print('순서를 바꾸면 원본과 같음:', np.array_equal(img, wrong_order))
# 슬라이싱으로 얻은 뷰는 원본과 메모리를 공유하므로 수정 시 원본도 바뀔 수 있다.
blue_view = img[:, :, 0]
# copy는 별도의 메모리를 만들어 원본에 영향을 주지 않고 수정할 수 있게 한다.
blue_copy = blue_view.copy()
print('슬라이싱은 메모리 공유:', np.shares_memory(img, blue_view))
print('copy는 메모리 공유:', np.shares_memory(img, blue_copy))
print('split 결과는 메모리 공유:', np.shares_memory(img, b))
panel([('Original', rgb), ('Correct merge', cv2.cvtColor(merged, cv2.COLOR_BGR2RGB)),
       ('Wrong BGR channel order', cv2.cvtColor(wrong_order, cv2.COLOR_BGR2RGB))])
