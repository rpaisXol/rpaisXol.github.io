# 7. 특징점 검출 및 매칭

## 7.1 특징점과 특징 기술자

- **특징점(keypoint)**: 다른 사진에서도 다시 찾기 쉬운 위치다. 모서리나 독특한 무늬가 예다.
- **특징 기술자(descriptor)**: 그 점 주변의 생김새를 숫자나 비트로 표현한 것이다.
- 위치만 알아서는 다른 사진의 어느 점인지 비교하기 어렵다. 기술자를 비교해 대응 후보를 찾는다.
- 특징점에는 위치뿐 아니라 크기·방향·응답 강도 같은 정보도 포함될 수 있다.
- 평평한 벽처럼 무늬가 없거나 같은 무늬가 반복되면 대응을 찾기 어렵다.

| 개념 | 비유 | OpenCV 예 |
| :---: | :---: | :---: |
| 특징점 | 지도에서 눈에 띄는 장소 | `kp[i].pt` |
| 기술자 | 그 장소의 생김새 설명 | `des[i]` |
| 매칭 | 두 지도에서 같은 장소 후보 연결 | `DMatch` |

- 템플릿 매칭은 작은 영상 전체를 위치별로 비교한다. 
- 특징점 매칭은 여러 국소 특징의 대응을 찾으므로 회전·크기 변화에 대응할 여지가 있지만 모든 변화에 강한 것은 아니다.

### 준비

```python
# 셀 1: 특징점 실습 준비
# 원본과 투시 변환 영상을 비교하기 위한 출력 함수를 정의한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
import json
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT=Path.cwd()
ASSETS=ROOT/'assets'
assert (ASSETS/'Lenna.png').is_file(), 'ROOT를 실습 폴더로 바꾸세요.'
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
a=cv2.imdecode(np.fromfile(ASSETS/'Lenna.png',np.uint8),cv2.IMREAD_COLOR)
assert a is not None

# 비교 그림의 배치를 통일하고, 영상 또는 결과 배열을 화면에 표시한다.
def show(items,name):
    fig,axs=plt.subplots(1,len(items),figsize=(6*len(items),5),squeeze=False)
    for ax,(title,img) in zip(axs.flat,items):
        ax.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        ax.set_title(title);ax.axis('off')
    fig.tight_layout();fig.savefig(ASSETS/name,dpi=140)
    plt.show();plt.close(fig)
print('OpenCV:',cv2.__version__)
```

### 기하 변환을 아는 두 번째 영상 만들기

- 레나 전체를 알려진 호모그래피로 변환한다. 
- 실제로 다른 카메라로 촬영한 영상이 아닌 **통제된 합성 실험**이다. 
- 이 실험에서는 한 호모그래피가 정확한 모델이지만, 실제 입체 장면에서는 깊이에 따른 시차로 하나의 호모그래피가 맞지 않을 수 있다. 
- 정답 변환은 검증에만 사용하고 추정에는 제공하지 않는다.

```python
# 셀 2: 정답 변환을 아는 영상 쌍
# H_true로 합성한 영상을 만들며, 이 행렬은 추정 정확도 평가에 사용한다.

height,width=a.shape[:2]
src_corners=np.float32([[0,0],[width-1,0],[width-1,height-1],[0,height-1]])
dst_corners=np.float32([[55,35],[300,60],[280,300],[35,270]])
H_true=cv2.getPerspectiveTransform(src_corners,dst_corners)
b=cv2.warpPerspective(a,H_true,(340,340),borderValue=(60,60,60))
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray_a=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray_b=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
show([('Original',a),('Synthetic perspective view',b)],'pair.png')
```

![셀 실행 결과](assets/pair.png)

## 7.2 특징점 검출 및 기술자 계산

### ORB와 SIFT

| 항목 | ORB | SIFT |
| :---: | :---: | :---: |
| 기본 아이디어 | FAST 계열 검출·방향·BRIEF 계열 기술자 | 스케일 공간 검출·방향·기울기 분포 기술자 |
| 기본 기술자 | 256비트, 32바이트 | 128차원 실수 벡터 |
| 대표 거리 | 해밍 거리 | L2 거리 |
| 활용 관점 | 비교적 가벼운 처리 | 다양한 스케일·회전 변화의 대응 |

- 속도·정확도는 이미지와 설정에 따라 달라진다. 
- ORB의 `nfeatures`는 원하는 최대 보유 특징 수에 관한 설정이며 반드시 그만큼 검출되는 것은 아니다.

이번에는 `WTA_K=2`인 ORB를 사용한다. ORB의 `WTA_K=3` 또는 4라면 `NORM_HAMMING2`가 필요하다.

### ORB 검출과 기술자 확인

```python
# 셀 3: ORB 특징점과 기술자
# 무늬가 뚜렷한 점의 위치와 주변 패턴을 나타내는 이진 기술자를 함께 계산한다.

# nfeatures는 유지할 특징점 수의 목표 상한이며, 검출 수는 입력의 무늬와 다른 설정에도 좌우된다.
# scaleFactor=1.2, nlevels=8은 피라미드 설정이며 WTA_K=2는 이진 비교 방식이다.
orb=cv2.ORB_create(nfeatures=1500,scaleFactor=1.2,nlevels=8,edgeThreshold=15,fastThreshold=10,WTA_K=2)
# 위치·방향·스케일을 담은 키포인트와 매칭에 사용할 기술자를 함께 구한다.
kp_a,des_a=orb.detectAndCompute(gray_a,None)
# 위치·방향·스케일을 담은 키포인트와 매칭에 사용할 기술자를 함께 구한다.
kp_b,des_b=orb.detectAndCompute(gray_b,None)
if des_a is None or des_b is None or len(des_b)<2:
    raise RuntimeError('매칭할 기술자가 부족합니다. 입력의 무늬와 검출 설정을 확인하세요.')
assert len(kp_a)==len(des_a) and len(kp_b)==len(des_b)
print('특징점:',len(kp_a),len(kp_b))
print('기술자:',des_a.shape,des_a.dtype,des_b.shape,des_b.dtype)
ka=cv2.drawKeypoints(a,kp_a,None,color=(0,255,0),flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
kb=cv2.drawKeypoints(b,kp_b,None,color=(0,255,0),flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
show([('ORB keypoints A',ka),('ORB keypoints B',kb)],'keypoints.png')
```

```text
특징점: 1472 1500
기술자: (1472, 32) uint8 (1500, 32) uint8

```

![셀 실행 결과](assets/keypoints.png)

## 7.3 특징점 매칭

### 기술자 거리로 후보 찾기

ORB의 해밍 거리는 두 비트열에서 서로 다른 비트 수다.

$$
d_H(p,q)=\sum_i\mathbf{1}[p_i\ne q_i]
$$

SIFT의 대표 거리인 L2는 다음과 같다.

$$
d_2(p,q)=\sqrt{\sum_i(p_i-q_i)^2}
$$

거리가 작을수록 기술자가 비슷하지만, 실제 같은 장소라는 보장은 아니다.

### 최근접 두 후보 비교: 비율 검사

$$
d_1<\tau d_2,\qquad d_1\le d_2
$$

- 1등이 2등보다 충분히 가까우면 남긴다.
- 두 후보의 거리가 비슷하면 모호한 대응으로 본다.
- $\tau=0.75$는 실습 설정이지 정답 확률이나 보편적인 최적값이 아니다.
- 더 작은 값은 일반적으로 더 엄격하게 걸러낸다.
- 비율 검사와 상호 최근접 검사(crossCheck)는 다른 조건이다. 이번에는 `crossCheck=False`와 k=2를 사용한다.

### KNN과 비율 검사

```python
# 셀 4: 최근접 매칭과 비율 검사
# 가장 가까운 두 후보를 비교해 구분이 불분명한 대응을 제외한다.

# WTA_K=2인 ORB의 이진 기술자는 해밍 거리로 비교하며, k=2 비율 검사를 위해 crossCheck를 끈다.
matcher=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=False)
# 질의 기술자마다 가까운 후보 두 개를 찾는다. 후보 수가 부족할 수 있어 길이를 확인한다.
pairs=matcher.knnMatch(des_a,des_b,k=2)
nearest=[p[0] for p in pairs if len(p)>0]
good=[]
for pair in pairs:
    if len(pair)<2: continue
    m,n=pair
    # 첫 후보 거리가 둘째 후보 거리의 75%보다 작을 때만 모호하지 않은 대응으로 채택한다.
    if m.distance<0.75*n.distance:good.append(m)
print('최근접 후보:',len(nearest),'비율 검사 통과:',len(good))
# 표시만 상위 60개로 제한하며 RANSAC에는 통과한 전체 대응을 사용한다.
def draw_matches(matches):
    return cv2.drawMatches(a,kp_a,b,kp_b,sorted(matches,key=lambda m:m.distance)[:60],None,
                          matchColor=(0,255,0),flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
show([('Nearest: up to 60 shown',draw_matches(nearest)),
      ('Ratio test: up to 60 shown',draw_matches(good))],'matches.png')
```

```text
최근접 후보: 1472 비율 검사 통과: 827
```

![셀 실행 결과](assets/matches.png)

## 7.4 잘못된 대응 제거

### RANSAC을 이용한 기하 모델 추정

- 기술자가 비슷한 후보들 가운데 같은 기하 변환으로 설명되는 대응을 찾는다.
- 작은 표본으로 모델을 가정하고, 그 모델에 동의하는 대응을 센다.
- 반복해서 지지가 큰 모델을 찾는다. 여기서는 호모그래피를 추정한다.
- **인라이어**는 현재 모델과 임계값에 맞는 대응이지, 절대적으로 참이라고 인증된 대응이 아니다.
- 가짜 대응이 일관된 패턴을 만들거나 올바른 대응이 너무 적으면 실패할 수 있다.

$$
\begin{bmatrix}u'\\v'\\w'\end{bmatrix}
=H\begin{bmatrix}x\\y\\1\end{bmatrix},\qquad
\hat x'=u'/w',\quad \hat y'=v'/w'
$$

$$
e_i=\sqrt{(x'_i-\hat x'_i)^2+(y'_i-\hat y'_i)^2}
$$

- 이번 재투영 임계값은 목적 영상 기준 3픽셀이다. 
- 임계값을 크게 하면 부정확한 대응도 포함될 수 있다.

호모그래피에는 일반 위치의 대응점이 최소 4쌍 필요하다. 점이 한 직선에 몰리는 등 퇴화된 배치는 안 되며, 4개가 있다고 신뢰할 수 있는 추정이 보장되지는 않는다.

### 호모그래피와 인라이어 추정

```python
# 셀 5: RANSAC 호모그래피 추정
# 전체 대응 중 하나의 투시 변환으로 설명되는 인라이어를 찾는다.

if len(good)<4:
    raise RuntimeError('호모그래피 추정에 필요한 대응이 부족합니다.')
# 질의 영상의 키포인트 좌표를 (N,1,2) 형태로 모아 변환 추정의 출발점으로 사용한다.
points_a=np.float32([kp_a[m.queryIdx].pt for m in good]).reshape(-1,1,2)
# trainIdx에 해당하는 대상 영상 좌표를 같은 대응 순서로 모은다.
points_b=np.float32([kp_b[m.trainIdx].pt for m in good]).reshape(-1,1,2)
cv2.setRNGSeed(42)
# RANSAC의 허용 재투영 오차는 3픽셀이며, 반환 mask는 추정 모델의 인라이어 표시다.
# maxIters=5000은 반복 상한, confidence=0.995는 RANSAC 모델 탐색의 목표 신뢰 수준이다.
H_est,mask=cv2.findHomography(points_a,points_b,cv2.RANSAC,3.0,maxIters=5000,confidence=0.995)
if H_est is None or mask is None or not np.isfinite(H_est).all():
    raise RuntimeError('기하 모델 추정에 실패했습니다.')
# OpenCV의 0/1 인라이어 표시를 1차원 불리언 배열로 바꾼다.
inlier_mask=mask.ravel().astype(bool)
if inlier_mask.sum()<4:raise RuntimeError('유효 인라이어가 부족합니다.')
inliers=[m for m,keep in zip(good,inlier_mask) if keep]
outliers=[m for m,keep in zip(good,inlier_mask) if not keep]
print('인라이어:',len(inliers),'아웃라이어:',len(outliers))
show([('RANSAC inliers: up to 60',draw_matches(inliers)),
      ('Rejected: up to 60',draw_matches(outliers))],'ransac.png')
```

```text
인라이어: 771 아웃라이어: 56
```

![셀 실행 결과](assets/ransac.png)

### 알려진 변환으로 추정 결과 검증

인라이어의 재투영 오차는 모델 적합도를 보여준다. 
별도로, 정답 변환과 추정 변환이 영상 내부의 격자점을 어디로 보내는지 비교한다. 
이 합성 예제의 성공이 실제 모든 사진에 대한 성능을 뜻하지는 않는다.
주황색은 정답 경계, 초록색은 추정 경계다. 두 선이 겹칠수록 추정 위치가 비슷하다.

```python
# 셀 6: 재투영 오차와 정답 비교
# 선택된 대응점의 오차와 별도 격자점에서 알려진 변환에 대한 오차를 확인한다.

pred=cv2.perspectiveTransform(points_a,H_est)
errors=np.linalg.norm(pred-points_b,axis=2).ravel()
xx,yy=np.meshgrid(np.linspace(20,width-21,8),np.linspace(20,height-21,8))
grid=np.stack([xx.ravel(),yy.ravel()],axis=1).astype(np.float32).reshape(-1,1,2)
true_grid=cv2.perspectiveTransform(grid,H_true)
est_grid=cv2.perspectiveTransform(grid,H_est)
# 매칭에 쓰지 않은 격자에서 추정 변환과 정답 변환의 좌표 차이를 측정한다.
grid_error=np.linalg.norm(true_grid-est_grid,axis=2).ravel()
outline=cv2.perspectiveTransform(src_corners.reshape(-1,1,2),H_est)
marked=b.copy()
cv2.polylines(marked,[np.rint(dst_corners).astype(np.int32)],True,(0,165,255),3)
cv2.polylines(marked,[np.rint(outline).astype(np.int32)],True,(0,255,0),1)
show([('Orange: true / Green: estimated',marked)],'homography.png')
summary={'opencv':cv2.__version__,'keypoints':[len(kp_a),len(kp_b)],'ratio_matches':len(good),
         'inliers':len(inliers),'outliers':len(outliers),
         'inlier_median_reprojection_px':float(np.median(errors[inlier_mask])),
         'grid_median_error_px':float(np.median(grid_error)),
         'grid_max_error_px':float(grid_error.max())}
print(json.dumps(summary,indent=2))
assert np.median(grid_error)<5, '이 합성 예제에서 추정 오차가 큽니다.'
# 수치 결과를 UTF-8 JSON으로 저장하여 그림과 별도로 확인할 수 있게 한다.
(ROOT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# 다시 분석할 수 있도록 계산 배열을 원래 자료형으로 보존한다.
np.savez(ROOT/'homography_results.npz',H_true=H_true,H_est=H_est,inlier_mask=inlier_mask,
         points_a=points_a,points_b=points_b)
```

```text
{
  "opencv": "5.0.0",
  "keypoints": [
    1472,
    1500
  ],
  "ratio_matches": 827,
  "inliers": 771,
  "outliers": 56,
  "inlier_median_reprojection_px": 0.8571128845214844,
  "grid_median_error_px": 0.646217942237854,
  "grid_max_error_px": 3.446655750274658
}
```

![셀 실행 결과](assets/homography.png)

### 셀 7. 단색 입력과 SIFT 기술자 확인

단색에서 특징점이 없을 때를 확인한다. 
SIFT는 검출·기술자 모양만 비교하며, 앞의 ORB 결과로 SIFT의 정확도를 평가하지 않는다. 
SIFT로 매칭을 바꿀 때는 기술자뿐 아니라 거리도 L2로 바꿔야 한다.

```python
# 셀 7: 단색 입력과 SIFT 기술자
# 특징점이 없는 경우를 확인하고, 사용 가능한 환경에서 SIFT 기술자의 형태도 출력한다.

blank=np.full((100,100),128,np.uint8)
blank_kp,blank_des=orb.detectAndCompute(blank,None)
assert len(blank_kp)==0 and blank_des is None
print('단색 입력의 기술자 없음 처리 확인')
if hasattr(cv2,'SIFT_create'):
    sift=cv2.SIFT_create(nfeatures=1000)
    skp,sdes=sift.detectAndCompute(gray_a,None)
    print('SIFT 특징점:',len(skp),'기술자:',None if sdes is None else (sdes.shape,str(sdes.dtype)))
    # SIFT 매칭에서는 cv2.BFMatcher(cv2.NORM_L2)를 사용한다.
else:
    print('현재 빌드에 SIFT가 없습니다. ORB 실습 결과는 그대로 확인 가능합니다.')
```

```text
단색 입력의 기술자 없음 처리 확인
SIFT 특징점: 283 기술자: ((283, 128), 'float32')
```

## 실패를 해석하는 방법

| 증상 | 확인할 것 |
| :---: | :---: |
| 특징점이 거의 없음 | 텍스처·해상도·흐림·검출 임계값 |
| 비율 검사 후 대응이 부족 | 겹치는 영역·반복 무늬·변환 크기 |
| 인라이어가 적음 | 잘못된 대응·기하 모델의 적합성 |
| 인라이어는 많지만 경계가 이상함 | 점의 공간 분포·퇴화 배치·반복 패턴 |
| 실제 입체 장면에서 오차가 큼 | 깊이 차이와 시차, 다른 기하 모델 필요 여부 |

- 호모그래피는 평면 또는 적절한 카메라 회전 상황 등에 알맞다. 
- 일반적인 입체 장면에서 대응 관계를 검증할 때는 기본행렬, 또는 카메라 내부 파라미터를 아는 경우 필수행렬 등의 모델을 고려한다. 
- 이 행렬들은 대응점이 놓일 에피폴라 선의 제약을 표현하며, 호모그래피처럼 한 점을 다른 영상의 한 점으로 직접 보내는 워핑 행렬은 아니다. 
- RANSAC이 모델 선택의 잘못까지 자동 해결하지는 않는다.

## 참고 문서

- [OpenCV — Feature Matching](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html)
- [OpenCV — Feature Matching and Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)

