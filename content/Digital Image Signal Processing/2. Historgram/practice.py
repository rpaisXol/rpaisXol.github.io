# -*- coding: utf-8 -*-
# 히스토그램의 기본 집계부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: 히스토그램의 기본 집계
# 2×2 예제에서 값별 개수와 비율을 직접 확인한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT = Path.cwd()  # 노트북과 assets 폴더가 있는 위치
path = ROOT / 'assets' / 'Lenna.png'
if not path.exists():
    raise FileNotFoundError('assets/Lenna.png를 확인하세요.')
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
if img is None:
    raise ValueError('이미지 디코딩 실패')
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 8비트 밝기값 0~255를 256개 구간으로 세어 1차원 배열로 반환한다.
def hist(a):
    # channels는 집계할 채널, histSize는 구간 수, ranges의 끝값 256은 포함하지 않는다.
    return cv2.calcHist([a], [0], None, [256], [0, 256]).ravel()

sample = np.array([[0, 0], [128, 255]], dtype=np.uint8)
h = hist(sample)
for k in [0, 128, 255]:
    print(f'값 {k}: 개수 {int(h[k])}, 비율 {h[k]/sample.size:.2f}')
assert h.sum() == sample.size
print('OpenCV:', cv2.__version__)
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].imshow(sample, cmap='gray', vmin=0, vmax=255)
axes[0].set_title('2 x 2 pixels')
for y in range(2):
    for x in range(2):
        axes[0].text(x,y,str(sample[y,x]),ha='center',va='center',color='red')
axes[1].bar([0,128,255], h[[0,128,255]], width=12)
axes[1].set(xlabel='Pixel value', ylabel='Pixel count', xticks=[0,128,255])
fig.tight_layout()
plt.show()

# 셀 2: 레나의 그레이스케일 히스토그램
# 히스토그램의 합이 전체 픽셀 수와 같고 NumPy 집계와 일치하는지 확인한다.

h_gray = hist(gray)
assert h_gray.sum() == gray.size
assert np.array_equal(h_gray, np.bincount(gray.ravel(), minlength=256))
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].imshow(gray, cmap='gray', vmin=0, vmax=255)
axes[0].set_title('Lenna grayscale')
axes[0].axis('off')
axes[1].plot(h_gray, color='black')
axes[1].set(xlim=(0,255), xlabel='Pixel value', ylabel='Pixel count')
fig.tight_layout()
plt.show()
print('영상 크기:', gray.shape, '픽셀 수:', gray.size)
print('히스토그램 합:', int(h_gray.sum()))

# 셀 3: B·G·R 채널별 히스토그램
# 세 채널을 따로 집계한다. 각 그래프는 해당 성분의 값 분포를 나타낸다.

fig, ax = plt.subplots(figsize=(8, 4))
for channel, color in enumerate(['blue', 'green', 'red']):
    # channels는 집계할 채널, histSize는 구간 수, ranges의 끝값 256은 포함하지 않는다.
    h = cv2.calcHist([img], [channel], None, [256], [0, 256]).ravel()
    assert h.sum() == gray.size
    ax.plot(h, color=color, label=color.upper())
    print(color, '픽셀 수:', int(h.sum()))
ax.set(xlim=(0,255), xlabel='Channel value', ylabel='Pixel count')
ax.legend()
fig.tight_layout()
plt.show()

# 셀 4: 관심 영역의 히스토그램
# 마스크가 0이 아닌 위치만 세고, 크기가 다른 영역은 비율로 비교한다.

mask = np.zeros_like(gray)
mask[85:190, 95:180] = 255
# 8비트 마스크에서 0이 아닌 위치만 집계한다. 범위의 위쪽 끝 256은 제외된다.
h_roi = cv2.calcHist([gray], [0], mask, [256], [0,256]).ravel()
assert h_roi.sum() == np.count_nonzero(mask)
marked = img.copy()
# 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
cv2.rectangle(marked, (95,85), (179,189), (0,255,0), 2)
fig, axes = plt.subplots(1, 2, figsize=(10,4))
axes[0].imshow(cv2.cvtColor(marked, cv2.COLOR_BGR2RGB))
axes[0].axis('off')
axes[0].set_title('Selected ROI')
axes[1].plot(h_gray/gray.size, label='Whole image')
axes[1].plot(h_roi/h_roi.sum(), label='ROI')
axes[1].set(xlim=(0,255), xlabel='Pixel value', ylabel='Pixel fraction')
axes[1].legend()
fig.tight_layout()
plt.show()
print('선택한 픽셀 수:', int(h_roi.sum()))

# 셀 5: 전체 히스토그램 평활화
# 영상 전체의 누적 분포를 이용하여 밝기 값을 다시 배정한다.

# equalizeHist는 8비트 단일 채널 영상에 전체 히스토그램 평활화를 적용한다.
equalized = cv2.equalizeHist(gray)

# 모든 영상은 0~255, 히스토그램은 공통 y축 범위로 표시하여 비교한다.
def compare_gray(arrays, titles):
    fig, axes = plt.subplots(2, len(arrays), figsize=(4*len(arrays), 7), squeeze=False)
    ymax = max(hist(a).max() for a in arrays)*1.05
    for i, (a,title) in enumerate(zip(arrays,titles)):
        axes[0,i].imshow(a, cmap='gray', vmin=0, vmax=255)
        axes[0,i].set_title(title)
        axes[0,i].axis('off')
        axes[1,i].plot(hist(a), color='black')
        axes[1,i].set(xlim=(0,255), ylim=(0,ymax), xlabel='Pixel value', ylabel='Pixel count')
        print(f'{title}: min={a.min()}, max={a.max()}, mean={a.mean():.3f}, std={a.std():.3f}')
    fig.tight_layout()
    plt.show()

compare_gray([gray,equalized], ['Original','Global equalization'])
constant = np.full((16,16),128,dtype=np.uint8)
assert np.array_equal(constant,cv2.equalizeHist(constant))

# 셀 6: 저대비 입력과 CDF 변환표
# 밝기 범위를 인위적으로 줄인 입력에서 직접 만든 변환표와 OpenCV 결과를 비교한다.

# 원본과 구분되는 교육용 저대비 영상을 만들어 변환 효과를 쉽게 비교한다.
low = np.round(80 + 0.4*gray.astype(np.float64)).astype(np.uint8)
low_eq = cv2.equalizeHist(low)
compare_gray([low,low_eq], ['Synthetic low contrast','Global equalization'])
p = hist(low)/low.size
# 밝기별 비율을 누적하여 해당 밝기 이하 픽셀의 비율 CDF를 구한다.
cdf = np.cumsum(p)
# 입력에 실제로 등장하는 가장 낮은 밝기의 누적 비율을 찾는다.
cmin = cdf[np.flatnonzero(p)[0]]
# 최초의 유효 CDF를 빼고 0~255로 재배정한다. 단색 입력은 분모가 0이므로 별도 처리가 필요하다.
lut = np.round(255*(cdf-cmin)/(1-cmin)).clip(0,255).astype(np.uint8)
# 각 입력 밝기를 변환표의 인덱스로 사용하여 전체 영상의 새 밝기를 얻는다.
manual = lut[low]
print('수식 구현과 OpenCV의 최대 차이:', int(np.abs(manual.astype(np.int16)-low_eq.astype(np.int16)).max()))
fig, axes = plt.subplots(1,2,figsize=(10,4))
axes[0].plot(cdf,label='Input CDF')
axes[0].plot(np.cumsum(hist(low_eq))/low_eq.size,label='Output CDF')
axes[0].set(xlim=(0,255),ylim=(0,1),xlabel='Pixel value',ylabel='Cumulative fraction')
axes[0].legend()
present = np.flatnonzero(p)
axes[1].plot(present,lut[present])
axes[1].set(xlim=(0,255),ylim=(0,255),xlabel='Input value',ylabel='Output value',title='Mapping of observed values')
fig.tight_layout()
plt.show()

# 셀 7: CLAHE와 설정 비교
# 영역별 대비를 조절하며, clipLimit과 영역 개수의 영향을 따로 살펴본다.

# clipLimit은 대비 제한값, tileGridSize는 픽셀 크기가 아니라 가로·세로 타일 개수다.
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
cl = clahe.apply(gray)
low_cl = clahe.apply(low)
compare_gray([gray,equalized,cl], ['Original','Global equalization','CLAHE'])
compare_gray([low,low_eq,low_cl], ['Synthetic low contrast','Global equalization','CLAHE'])
# 한 번에 한 설정만 바꾸어 효과를 비교한다.
settings = [(2.0,(8,8)), (8.0,(8,8)), (2.0,(4,4))]
fig, axes = plt.subplots(1,3,figsize=(12,4))
for ax, (limit,grid) in zip(axes,settings):
    result = cv2.createCLAHE(clipLimit=limit,tileGridSize=grid).apply(low)
    ax.imshow(result,cmap='gray',vmin=0,vmax=255)
    ax.set_title(f'clip={limit}, grid={grid}')
    ax.axis('off')
fig.tight_layout()
plt.show()

# 셀 8: 컬러 영상의 밝기 성분만 조절
# Y만 처리하고 Cr·Cb를 유지한 뒤 BGR로 되돌려 채널별 평활화와 비교한다.

# 밝기 성분 Y와 색차 성분 Cr·Cb를 분리할 수 있는 표현으로 변환한다.
ycrcb = cv2.cvtColor(img,cv2.COLOR_BGR2YCrCb)
# OpenCV의 반환 순서는 Y, Cr, Cb이다. 각 채널은 높이×너비 배열이다.
Y, Cr, Cb = cv2.split(ycrcb)
y_eq = cv2.merge([cv2.equalizeHist(Y),Cr,Cb])
y_cl = cv2.merge([clahe.apply(Y),Cr,Cb])
assert np.array_equal(y_cl[:,:,1:],ycrcb[:,:,1:])
color_eq = cv2.cvtColor(y_eq,cv2.COLOR_YCrCb2BGR)
color_cl = cv2.cvtColor(y_cl,cv2.COLOR_YCrCb2BGR)
# 비교용: 세 채널을 독립적으로 바꾸면 색 관계가 달라질 수 있다.
channel_eq = cv2.merge([cv2.equalizeHist(c) for c in cv2.split(img)])
fig, axes = plt.subplots(1,4,figsize=(16,4))
for ax,a,title in zip(axes,[img,channel_eq,color_eq,color_cl],
                      ['Original','Equalize B,G,R separately','Equalize Y only','CLAHE on Y only']):
    ax.imshow(cv2.cvtColor(a,cv2.COLOR_BGR2RGB))
    ax.set_title(title)
    ax.axis('off')
fig.tight_layout()
plt.show()
print('Y 처리 중 Cr, Cb 유지:', np.array_equal(y_cl[:,:,1:],ycrcb[:,:,1:]))
