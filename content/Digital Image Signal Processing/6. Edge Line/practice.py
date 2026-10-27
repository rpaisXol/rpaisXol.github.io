# -*- coding: utf-8 -*-
# 입력 영상 준비부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: 입력 영상 준비
# 에지 계산에는 그레이스케일을 사용하고, 컬러 출력은 BGR을 RGB로 바꿔 표시한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
import json
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT = Path.cwd()  # 필요하면 Path('/실습/폴더')로 변경
ASSETS = ROOT / 'assets'
assert (ASSETS/'Lenna.png').is_file(), 'ROOT를 확인하세요.'
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
bgr = cv2.imdecode(np.fromfile(ASSETS/'Lenna.png',np.uint8),cv2.IMREAD_COLOR)
assert bgr is not None
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
gray = cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)

# 비교 그림의 배치를 통일하고, 영상 또는 결과 배열을 화면에 표시한다.
def show_panels(items, filename, cols=3):
    fig, axes = plt.subplots((len(items)+cols-1)//cols,cols,figsize=(4*cols,4*((len(items)+cols-1)//cols)),squeeze=False)
    for ax,(title,a) in zip(axes.flat,items):
        if a.ndim==2: ax.imshow(a,cmap='gray',vmin=0,vmax=255)
        else: ax.imshow(cv2.cvtColor(a,cv2.COLOR_BGR2RGB))
        ax.set_title(title);ax.axis('off')
    for ax in list(axes.flat)[len(items):]:ax.axis('off')
    fig.tight_layout();fig.savefig(ASSETS/filename,dpi=140)
    plt.show();plt.close(fig)

print('OpenCV:',cv2.__version__,'영상:',gray.shape)
show_panels([('Original',bgr),('Grayscale',gray)],'input.png',2)

# 셀 2: Canny 임계값 비교
# 약한 에지와 강한 에지를 구분하는 두 임계값을 바꾸어 검출 결과를 비교한다.

# Canny 전에 가우시안으로 작은 밝기 잡음을 줄여 불필요한 에지 반응을 완화한다.
blur = cv2.GaussianBlur(gray,(5,5),1.2,borderType=cv2.BORDER_REFLECT_101)
thresholds = [(30,90),(60,180),(100,250)]
edge_maps = []
for low,high in thresholds:
    # low/high는 약한·강한 에지 기준이며 L2gradient=True는 유클리드 그래디언트 크기를 사용한다.
    edges = cv2.Canny(blur,low,high,apertureSize=3,L2gradient=True)
    assert edges.shape==gray.shape
    assert set(np.unique(edges)).issubset({0,255})
    edge_maps.append(edges)
    print((low,high),'에지 픽셀:',np.count_nonzero(edges))
show_panels([(f'Canny {lo}/{hi}',e) for (lo,hi),e in zip(thresholds,edge_maps)],'canny.png')

# 셀 3: 허프 변환의 투표 원리
# 같은 수평선 위 세 점이 법선각 90도, 거리 40픽셀에서 만나는지 그래프로 확인한다.

theta = np.linspace(0,np.pi,361)
fig,ax = plt.subplots(figsize=(7,4))
for x in [20,60,100]:
    # 점 (x, y)의 허프 곡선은 rho=x*cos(theta)+y*sin(theta)이다. theta는 직선의 법선각이다.
    rho = x*np.cos(theta)+40*np.sin(theta)
    ax.plot(np.rad2deg(theta),rho,label=f'Point ({x},40)')
ax.scatter([90],[40],color='black',zorder=5)
ax.set(xlabel='Normal angle (degrees)',ylabel='Signed rho (pixels)',title='Votes meet at (90 deg, 40 px)')
ax.legend();ax.grid(alpha=.3);fig.tight_layout()
fig.savefig(ASSETS/'votes.png',dpi=140);plt.show();plt.close(fig)

# 셀 4: 선 검출용 합성 영상
# 방향과 간격이 알려진 선분을 만들고 Canny 에지에 허프 변환을 적용할 준비를 한다.

scene = np.zeros((300,400),np.uint8)
cv2.line(scene,(40,50),(350,50),255,3)
cv2.line(scene,(60,90),(60,260),255,3)
cv2.line(scene,(120,260),(350,110),255,3)
cv2.line(scene,(160,220),(220,220),255,3)
cv2.line(scene,(235,220),(350,220),255,3)
scene_edges = cv2.Canny(scene,50,150,L2gradient=True)
show_panels([('Synthetic lines',scene),('Canny edges',scene_edges)],'scene.png',2)

# 셀 5: 표준 허프 변환
# rho와 theta로 표현한 직선을 영상 위 두 점으로 바꾸어 그린다.

def draw_standard(source, lines, max_draw=20):
    out = cv2.cvtColor(source,cv2.COLOR_GRAY2BGR)
    # 화면을 가로지르는 직선을 그릴 수 있도록 영상 대각선보다 긴 양방향 구간을 사용한다.
    length = int(np.hypot(*source.shape)*2)
    if lines is not None:
        for rho,theta in lines[:max_draw,0]:
            a,b = np.cos(theta),np.sin(theta)
            # 직선의 원점에서 가장 가까운 점을 구한 뒤 법선에 수직인 방향으로 양 끝점을 확장한다.
            x0,y0 = a*rho,b*rho
            p1=(int(round(x0-length*b)),int(round(y0+length*a)))
            p2=(int(round(x0+length*b)),int(round(y0-length*a)))
            cv2.line(out,p1,p2,(0,0,255),1)
    return out

# 거리 1픽셀, 각도 1도 간격으로 누적하며 threshold=100은 필요한 투표 수다.
standard = cv2.HoughLines(scene_edges.copy(),1,np.pi/180,threshold=100)
print('표준 허프 후보 수:',0 if standard is None else len(standard))
if standard is not None:
    print('앞 5개 (rho, theta 라디안):',standard[:5,0])
show_panels([('Standard Hough: max 20 drawn',draw_standard(scene,standard))],'standard.png',1)

# 셀 6: 확률적 허프 변환
# 선분 양 끝점을 직접 얻으며, 허용 간격 maxLineGap에 따른 연결 변화를 비교한다.

def draw_segments(source, lines):
    # 회색 입력을 3채널로 늘려 검출선을 컬러로 표시할 수 있게 한다.
    out=cv2.cvtColor(source,cv2.COLOR_GRAY2BGR)
    if lines is not None:
        for x1,y1,x2,y2 in np.asarray(lines).reshape(-1,4):
            cv2.line(out,(int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),2)
    return out

segment_results={}
for gap in [5,25]:
    cv2.setRNGSeed(42)
    # 투표 수 40, 최소 길이 40픽셀을 적용하고 maxLineGap으로 끊긴 구간의 연결 허용치를 정한다.
    seg=cv2.HoughLinesP(scene_edges.copy(),1,np.pi/180,threshold=40,
                       minLineLength=40,maxLineGap=gap)
    segment_results[gap]=seg
    print('maxLineGap:',gap,'선분 수:',0 if seg is None else len(seg))
show_panels([(f'Probabilistic Hough: gap={gap}',draw_segments(scene,seg))
             for gap,seg in segment_results.items()],'segments.png',2)

# 셀 7: 레나 영상의 직선 후보
# 에지 중 직선으로 설명되는 부분을 찾는다. 검출된 선이 물체의 의미를 나타내지는 않는다.

lenna_edges=edge_maps[1]
ls=cv2.HoughLines(lenna_edges.copy(),1,np.pi/180,threshold=60)
cv2.setRNGSeed(42)
# 레나에서는 투표 수 25, 최소 길이 25픽셀, 최대 연결 간격 8픽셀로 선분 후보를 구한다.
lp=cv2.HoughLinesP(lenna_edges.copy(),1,np.pi/180,threshold=25,
                  minLineLength=25,maxLineGap=8)
show_panels([('Lenna Canny',lenna_edges),
             ('Standard: max 20 drawn',draw_standard(gray,ls)),
             ('Probabilistic segments',draw_segments(gray,lp))],'lenna_lines.png')
summary={'opencv':cv2.__version__,
         'canny_counts':{f'{lo}/{hi}':int(np.count_nonzero(e)) for (lo,hi),e in zip(thresholds,edge_maps)},
         'synthetic_standard_count':0 if standard is None else len(standard),
         'synthetic_segment_counts':{str(g):0 if s is None else len(s) for g,s in segment_results.items()},
         'lenna_standard_count':0 if ls is None else len(ls),
         'lenna_segment_count':0 if lp is None else len(lp)}
# 수치 결과를 UTF-8 JSON으로 저장하여 그림과 별도로 확인할 수 있게 한다.
(ROOT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))

# 셀 8: 알려진 직선과 빈 입력 확인
# 위치를 아는 수평선은 검출되고, 에지가 없는 입력에서는 None을 반환하는지 확인한다.

test=np.zeros((120,160),np.uint8)
test[40,20:140]=255
known=cv2.HoughLines(test,1,np.pi/180,threshold=90)
assert known is not None
assert any(abs(float(rho)-40)<=1 and abs(float(theta)-np.pi/2)<np.deg2rad(1.1)
           for rho,theta in known[:,0])
blank=np.zeros_like(test)
assert cv2.HoughLines(blank,1,np.pi/180,30) is None
assert cv2.HoughLinesP(blank,1,np.pi/180,30,minLineLength=20,maxLineGap=3) is None
print('수평선 rho=40, theta=90도 검증 및 빈 입력 처리 통과')
