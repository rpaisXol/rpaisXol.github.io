# -*- coding: utf-8 -*-
# 특징점 실습 준비부터 이어지는 장 전체 실습 코드입니다.
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
