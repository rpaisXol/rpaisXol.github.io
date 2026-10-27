# -*- coding: utf-8 -*-
# 실습 영상과 출력 함수부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: 실습 영상과 출력 함수
# 그레이스케일을 float32로 바꾸어 미분과 차분의 음수를 보존한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
import json
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT = Path.cwd()  # 노트북과 assets 폴더가 있는 위치
OUT = ROOT / 'assets'
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
img = cv2.imdecode(np.fromfile(OUT/'Lenna.png', np.uint8), cv2.IMREAD_COLOR)
if img is None:
    raise FileNotFoundError('assets/Lenna.png를 확인하세요.')
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
f = gray.astype(np.float32)
border = cv2.BORDER_REFLECT_101

# 비교 그림의 배치를 통일하고, 영상 또는 결과 배열을 화면에 표시한다.
def panel(name, items, cols=3, signed=False):
    fig, axes = plt.subplots((len(items)+cols-1)//cols, cols, figsize=(4*cols,4*((len(items)+cols-1)//cols)), squeeze=False)
    for ax, (title, a) in zip(axes.flat, items):
        if signed:
            m = max(float(np.abs(a).max()), 1e-6)
            im = ax.imshow(a, cmap='coolwarm', vmin=-m, vmax=m)
            fig.colorbar(im, ax=ax, shrink=.65)
        else:
            ax.imshow(a, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title); ax.axis('off')
    for ax in list(axes.flat)[len(items):]: ax.axis('off')
    fig.tight_layout(); plt.show()


print('OpenCV:',cv2.__version__,'영상 크기:',gray.shape)
panel('original.png',[('Original grayscale',gray)],cols=1)

# 셀 2: 상관과 합성곱의 차이
# 중심 기준 비대칭 커널로 오른쪽 값 6과 왼쪽 값 4가 선택되는지 확인한다.

a = np.arange(1,10,dtype=np.float32).reshape(3,3)
k_mean = np.ones((3,3),np.float32)/9
# 오른쪽 이웃 하나만 선택하는 비대칭 커널로 뒤집기의 효과를 확인한다.
k_asym = np.array([[0,0,0],[0,0,1],[0,0,0]],np.float32)
# filter2D는 커널을 뒤집지 않는 상관 연산을 수행한다.
corr = cv2.filter2D(a,-1,k_asym,borderType=border)
# 중앙 anchor의 홀수 커널을 양축으로 뒤집어 합성곱 결과를 구한다.
conv = cv2.filter2D(a,-1,cv2.flip(k_asym,-1),borderType=border)
print('입력:\n',a)
print('평균 필터의 중심:',cv2.filter2D(a,-1,k_mean)[1,1])
print('상관 중심:',corr[1,1], '합성곱 중심:',conv[1,1])
assert corr[1,1] == 6 and conv[1,1] == 4

# 셀 3: 경계 밖 값의 처리
# 같은 입력이라도 0 채우기·반복·반사 방식에 따라 가장자리 계산이 달라진다.

line = np.array([[10,20,30]],np.float32)
for name,mode in [('CONSTANT',cv2.BORDER_CONSTANT),('REPLICATE',cv2.BORDER_REPLICATE),
                  ('REFLECT',cv2.BORDER_REFLECT),('REFLECT_101',cv2.BORDER_REFLECT_101)]:
    print(name,cv2.copyMakeBorder(line,0,0,1,1,mode,value=0).ravel().tolist())
bright_test = np.full((20,20),200,np.float32)
items=[]
for name,mode in [('Zero border',cv2.BORDER_CONSTANT),('Replicate',cv2.BORDER_REPLICATE),
                  ('Reflect 101',cv2.BORDER_REFLECT_101)]:
    result=cv2.blur(bright_test,(5,5),borderType=mode)
    items.append((name,result))
    print(name,'왼쪽 위:',result[0,0])
panel('border.png',items)

# 셀 4: 평균 및 가우시안 필터
# 같은 비중의 평균과 중심에 큰 비중을 주는 가우시안의 흐림 효과를 비교한다.

# 5×5 이웃을 같은 비중으로 평균내며 반사 경계 처리를 사용한다.
avg = cv2.blur(f,(5,5),borderType=border)
# 9×9 커널과 sigma=1.5를 사용하여 가까운 이웃에 더 큰 가중치를 준다.
gauss = cv2.GaussianBlur(f,(9,9),1.5,borderType=border)
panel('smoothing.png',[('Original',f),('Mean 5x5',avg),('Gaussian sigma=1.5',gauss)])

# 셀 5: Sobel과 라플라시안
# Sobel은 방향별 1차 변화, 라플라시안은 2차 변화를 나타낸다. 결과의 부호를 유지한다.

# dx=1, dy=0은 가로 방향 미분이며 세로 경계에 강하게 반응한다.
sx = cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3,borderType=border)
# dx=0, dy=1은 세로 방향 미분이며 가로 경계에 강하게 반응한다.
sy = cv2.Sobel(f,cv2.CV_32F,0,1,ksize=3,borderType=border)
# ksize=1의 라플라시안으로 2차 변화를 계산하고 CV_32F로 음수를 보존한다.
lap = cv2.Laplacian(f,cv2.CV_32F,ksize=1,borderType=border)

panel('derivatives.png',[('Sobel x',sx),('Sobel y',sy),('Laplacian',lap)],signed=True)
print('Sobel x 범위:',float(sx.min()),float(sx.max()))
print('Laplacian 범위:',float(lap.min()),float(lap.max()))

# 셀 6: 샤프닝
# 원본에 미세 변화를 더해 경계를 강조하고, 표시할 때만 0~255로 제한한다.

# 원본에서 흐림 결과를 뺀 고주파 성분을 원본에 더한다.
sharp = np.clip(f + (f-gauss),0,255)
# 중앙 계수가 음수인 라플라시안 결과를 빼서 경계를 강조한다.
sharp_lap = np.clip(f-0.25*lap,0,255)
panel('sharpen.png',[('Original',f),('Unsharp alpha=1',sharp),('Laplacian sharpening',sharp_lap)])

# 셀 7: 비선형 필터와 잡음
# 동일한 소금·후추 잡음 입력에 가우시안·미디언·양방향 필터를 적용한다.

# 같은 잡음 입력으로 비교하며 난수 시드를 고정합니다.
rng = np.random.default_rng(42)
noisy = gray.copy(); u = rng.random(gray.shape)
noisy[u<.025]=0; noisy[u>.975]=255
# 5×5 이웃의 중앙값을 고른다. 드문 흰 점·검은 점에 덜 끌리는 특성이 있다.
med = cv2.medianBlur(noisy,5)
# 지름 9의 이웃에서 밝기 차이 규모 50, 거리 규모 5로 가중치를 조절한다.
bil = cv2.bilateralFilter(noisy,9,50,5,borderType=cv2.BORDER_REPLICATE)
ng = cv2.GaussianBlur(noisy,(5,5),1.2,borderType=cv2.BORDER_REPLICATE)
panel('nonlinear.png',[('Original reference',gray),('Salt & pepper: p=0.05',noisy),('Gaussian on noisy',ng),('Median 5x5',med),('Bilateral on noisy',bil)])
# 지름 9의 이웃에서 밝기 차이 규모 50, 거리 규모 5로 가중치를 조절한다.
bil_clean = cv2.bilateralFilter(gray,9,50,5,borderType=border)
panel('bilateral.png',[('Original',gray),('Gaussian',gauss),('Bilateral d=9, 50, 5',bil_clean)])


for name,a in [('Noisy',noisy),('Gaussian',ng),('Median',med),('Bilateral',bil)]:
    print(name,'원본 대비 MAE:',round(float(np.abs(a.astype(np.float32)-f).mean()),3))

# 셀 8: 구조 요소, 침식, 팽창
# 흰색을 전경으로 정하고 구조 요소가 선택한 이웃의 최솟값·최댓값을 계산한다.

shapes = [('RECT',cv2.MORPH_RECT),('CROSS',cv2.MORPH_CROSS),('ELLIPSE',cv2.MORPH_ELLIPSE)]
panel('elements.png',[(name,cv2.getStructuringElement(shape,(9,9))*255) for name,shape in shapes])
binary=np.zeros((160,200),np.uint8)
# 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
cv2.rectangle(binary,(35,30),(150,125),255,-1)
cv2.circle(binary,(85,75),3,0,-1)
# 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
cv2.rectangle(binary,(110,30),(113,65),0,-1)
cv2.circle(binary,(175,45),2,255,-1)
# 9×9 타원 구조 요소에서 0이 아닌 위치를 형태학 연산의 이웃으로 사용한다.
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
def morph(a,op):
    return cv2.morphologyEx(a,op,k,borderType=cv2.BORDER_REPLICATE)
# 이웃의 최솟값을 선택하여 흰색 전경을 줄인다.
er=cv2.erode(binary,k,borderType=cv2.BORDER_REPLICATE)
# 이웃의 최댓값을 선택하여 흰색 전경을 넓힌다.
di=cv2.dilate(binary,k,borderType=cv2.BORDER_REPLICATE)
panel('erode_dilate.png',[('White foreground',binary),('Erosion',er),('Dilation',di)])
assert np.all(er<=binary) and np.all(di>=binary)
print('흰 픽셀 수:',*[int(np.count_nonzero(a)) for a in [binary,er,di]])

# 셀 9: 열림·닫힘과 형태학적 차이 연산
# 이진 도형과 그레이스케일에서 작은 구조 및 경계에 대한 반응을 비교한다.

ops=[('Opening',cv2.MORPH_OPEN),('Closing',cv2.MORPH_CLOSE),
     ('Gradient',cv2.MORPH_GRADIENT),('Top-hat',cv2.MORPH_TOPHAT),('Black-hat',cv2.MORPH_BLACKHAT)]
panel('binary.png',[('Binary input',binary)]+[(name,morph(binary,op)) for name,op in ops])
panel('gray.png',[('Gray input',gray)]+[(name,morph(gray,op)) for name,op in ops])
# 침식 다음 팽창을 적용하여 구조 요소보다 작은 밝은 구조를 줄인다.
opened=morph(binary,cv2.MORPH_OPEN)
# 팽창 다음 침식을 적용하여 작은 어두운 구멍이나 틈을 메운다.
closed=morph(binary,cv2.MORPH_CLOSE)
assert np.all(opened<=binary) and np.all(closed>=binary)
assert np.array_equal(morph(binary,cv2.MORPH_GRADIENT),cv2.subtract(di,er))
print('작은 흰 점 제거:',int(opened[45,175])==0)
print('작은 검은 구멍 채움:',int(closed[75,85])==255)

# 셀 10: 가우시안 차분 DoG
# 서로 다른 두 흐림 결과를 빼 중간 규모의 변화를 추출한다.

# DoG: 동일 크기 25x25 커널로 두 스케일을 비교합니다.
g1=cv2.GaussianBlur(f,(25,25),1.0,borderType=border)
g2=cv2.GaussianBlur(f,(25,25),3.0,borderType=border)
# 덜 흐린 결과에서 더 흐린 결과를 뺀다. 음수도 의미가 있으므로 절댓값을 취하지 않는다.
dog=g1-g2
panel('dog_blurs.png',[('Original',f),('Gaussian sigma=1',g1),('Gaussian sigma=3',g2)])
panel('dog_signed.png',[('DoG: sigma 1 minus 3',dog)],cols=1,signed=True)

constant=np.full_like(f,100)
dc=cv2.GaussianBlur(constant,(25,25),1)-cv2.GaussianBlur(constant,(25,25),3)
assert np.max(np.abs(dc))<1e-3
print('DoG 범위:',float(dog.min()),float(dog.max()))
print('일정한 영상의 최대 절대 응답:',float(np.abs(dc).max()))

# 셀 11: DoG의 주파수 응답
# 연속 가우시안 모델의 응답을 그린다. 실제 유한 이산 커널의 측정값은 아니다.

nu=np.linspace(0,.5,501)
response=np.exp(-2*np.pi**2*1**2*nu**2)-np.exp(-2*np.pi**2*3**2*nu**2)
fig,ax=plt.subplots(figsize=(7,4)); ax.plot(nu,response)
ax.set(xlabel='Spatial frequency (cycles/pixel)',ylabel='Response',title='Continuous Gaussian model: DoG response',xlim=(0,.5))
ax.grid(alpha=.3); fig.tight_layout(); plt.show()
