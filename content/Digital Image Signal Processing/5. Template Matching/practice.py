# -*- coding: utf-8 -*-
# 입력 경로와 공통 함수부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: 입력 경로와 공통 함수
# 원본과 템플릿을 읽고 결과 그림을 저장·표시할 준비를 한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
import csv
import json
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT = Path.cwd()  # 노트북 파일이 있는 폴더에서 실행
ASSETS = ROOT / 'assets'
assert (ASSETS / 'Lenna.png').is_file(), 'ROOT를 실습 폴더 경로로 바꾸세요.'

def read_image(name):
    # 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
    img = cv2.imdecode(np.fromfile(ASSETS / name, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(name)
    return img

# 비교 그림의 배치를 통일하고, 영상 또는 결과 배열을 화면에 표시한다.
def save_show(fig, name):
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=140)
    plt.show()
    plt.close(fig)

print('OpenCV:', cv2.__version__)

# 셀 2: 입력 영상과 템플릿 검사
# 크기·자료형을 맞추고, 분산이 없는 단색 템플릿을 제외한다.

bgr = read_image('Lenna.png')
template_bgr = read_image('template.png')
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
image = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
template = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
# shape는 (높이, 너비) 순서다. 좌표 (x, y)로 읽을 때는 배열 인덱스 [y, x]와 구분한다.
H, W = image.shape
# shape는 (높이, 너비) 순서다. 좌표 (x, y)로 읽을 때는 배열 인덱스 [y, x]와 구분한다.
h, w = template.shape
assert h <= H and w <= W
assert image.dtype == template.dtype == np.uint8
assert template.std() > 1e-6, '단색 템플릿은 피하세요.'
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
ax[0].imshow(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)); ax[0].set_title('Input')
ax[1].imshow(cv2.cvtColor(template_bgr, cv2.COLOR_BGR2RGB)); ax[1].set_title('Provided template')
for a in ax: a.axis('off')
save_show(fig, 'inputs.png')
print('입력:', image.shape, '템플릿:', template.shape)
print('예상 응답 맵:', (H-h+1, W-w+1))

# 셀 3: 여섯 가지 매칭 방법 비교
# SQDIFF 계열은 최솟값, 나머지는 최댓값의 위치를 최적 후보로 선택한다.

methods = ['TM_SQDIFF', 'TM_SQDIFF_NORMED', 'TM_CCORR',
           'TM_CCORR_NORMED', 'TM_CCOEFF', 'TM_CCOEFF_NORMED']
responses = {}
rows = []
for name in methods:
    # 템플릿을 움직이며 위치별 점수를 계산한다. 출력의 각 축 크기는 입력 크기에서 템플릿 크기를 뺀 뒤 1을 더한 값이다.
    response = cv2.matchTemplate(image, template, getattr(cv2, name))
    assert response.shape == (H-h+1, W-w+1)
    assert np.isfinite(response).all()
    # minMaxLoc은 점수의 최솟값·최댓값과 각각의 (x, y) 좌표를 반환한다.
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(response)
    # 제곱 차는 오차이므로 작을수록 좋고, 상관 계열은 클수록 좋은 후보로 선택한다.
    use_min = name in ('TM_SQDIFF', 'TM_SQDIFF_NORMED')
    score, loc = (min_val, min_loc) if use_min else (max_val, max_loc)
    responses[name] = response
    rows.append({'method': name, 'best': 'min' if use_min else 'max',
                 'score': score, 'x': loc[0], 'y': loc[1]})
header = '| 방법 | 최적 기준 | 점수 | x | y |\n| :---: | :---: | :---: | :---: | :---: |'
lines = [f"| {r['method']} | {r['best']} | {r['score']:.6g} | {r['x']} | {r['y']} |" for r in rows]
display(Markdown(header + '\n' + '\n'.join(lines)))
with (ROOT / 'matching_results.csv').open('w', newline='', encoding='utf-8-sig') as fp:
    # 사전의 키를 CSV 열 이름으로 사용하며, 각 매칭 방법의 점수와 좌표를 행으로 저장한다.
    writer = csv.DictWriter(fp, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)

# 셀 4: 응답 맵과 검출 위치 표시
# 응답 맵의 좌표는 템플릿 왼쪽 위 위치이며, 같은 좌표에 템플릿 크기의 상자를 그린다.

fig, axes = plt.subplots(6, 2, figsize=(10, 21))
for i, row in enumerate(rows):
    name, x, y = row['method'], row['x'], row['y']
    im = axes[i, 0].imshow(responses[name], cmap='viridis')
    axes[i, 0].plot(x, y, 'rx')
    axes[i, 0].set_title(f"{name}: {row['best']}")
    fig.colorbar(im, ax=axes[i, 0], shrink=.7)
    marked = bgr.copy()
    # 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
    cv2.rectangle(marked, (x, y), (x+w-1, y+h-1), (0, 255, 0), 2)
    axes[i, 1].imshow(cv2.cvtColor(marked, cv2.COLOR_BGR2RGB))
    axes[i, 1].set_title(f"({x}, {y}), score={row['score']:.5g}")
    axes[i, 1].axis('off')
save_show(fig, 'six_methods.png')

# 셀 5: 정규화 상관 계수 결과 저장
# TM_CCOEFF_NORMED의 최적 위치를 선택하여 표시용 그림과 검출 영상을 저장한다.

chosen = next(row for row in rows if row['method'] == 'TM_CCOEFF_NORMED')
x, y = chosen['x'], chosen['y']
result = bgr.copy()
# 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
cv2.rectangle(result, (x,y), (x+w-1,y+h-1), (0,255,0), 2)
ok, encoded = cv2.imencode('.png', result)
assert ok
encoded.tofile(ASSETS / 'template_matching_result.png')
fig, ax = plt.subplots(figsize=(5,5))
ax.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)); ax.axis('off')
ax.set_title(f"CCOEFF_NORMED: {chosen['score']:.4f}")
save_show(fig, 'best_match.png')
print('선택 위치:', (x,y), '영역 크기:', (w,h))

# 셀 6: 회전·크기 변화에 대한 통제 실험
# 같은 원본 패치를 회전·확대하여 넣고, 변형하지 않은 템플릿으로 찾았을 때의 점수를 비교한다.

base = image[60:140, 95:155].copy()
bh, bw = base.shape
angle = 25
# 패치 중심을 기준으로 회전하며, 다음 단계에서 캔버스 크기와 이동량을 보정한다.
M = cv2.getRotationMatrix2D(((bw-1)/2, (bh-1)/2), angle, 1.0)
c, s = abs(M[0,0]), abs(M[0,1])
nw, nh = int(np.ceil(bw*c+bh*s)), int(np.ceil(bh*c+bw*s))
M[0,2] += (nw-bw)/2; M[1,2] += (nh-bh)/2
# 확장한 캔버스에 회전 패치를 배치하고 빈 곳은 배경값 110으로 채운다.
rot = cv2.warpAffine(base, M, (nw,nh), borderValue=110)
# 가로·세로를 각각 1.3배로 보간하여 크기 변화 실험용 패치를 만든다.
scaled = cv2.resize(base, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_LINEAR)
variants = [('Original patch', base), ('Rotated 25 deg', rot), ('Scaled x1.3', scaled)]
experiment = []
fig, axes = plt.subplots(1,3,figsize=(12,4))
for ax, (label, patch) in zip(axes, variants):
    canvas = np.full((250,250), 110, np.uint8)
    px, py = 80, 80
    ph, pw = patch.shape
    canvas[py:py+ph, px:px+pw] = patch
    # 템플릿을 움직이며 위치별 점수를 계산한다. 출력의 각 축 크기는 입력 크기에서 템플릿 크기를 뺀 뒤 1을 더한 값이다.
    response = cv2.matchTemplate(canvas, base, cv2.TM_CCOEFF_NORMED)
    _, score, _, loc = cv2.minMaxLoc(response)
    foundx, foundy = loc
    marked = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)
    # 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
    cv2.rectangle(marked,(px,py),(px+pw-1,py+ph-1),(255,165,0),2)
    # 오른쪽 아래 좌표도 포함해 그린다. 폭·높이에서 1을 빼면 지정한 픽셀 범위와 맞는다.
    cv2.rectangle(marked,loc,(foundx+bw-1,foundy+bh-1),(0,255,0),1)
    ax.imshow(marked);ax.axis('off');ax.set_title(f'{label}\nscore={score:.4f}, pos={loc}')
    experiment.append({'case':label,'score':score,'x':foundx,'y':foundy})
assert experiment[0]['score'] > .999
assert (experiment[0]['x'],experiment[0]['y']) == (80,80)
save_show(fig, 'rotation_scale.png')
print(json.dumps(experiment, indent=2))
# 수치 결과를 UTF-8 JSON으로 저장하여 그림과 별도로 확인할 수 있게 한다.
(ROOT/'experiment_results.json').write_text(json.dumps(experiment, indent=2), encoding='utf-8')
