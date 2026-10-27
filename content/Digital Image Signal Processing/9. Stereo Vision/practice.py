# -*- coding: utf-8 -*-
# Tsukuba 좌우 영상 실습. 노트북과 같은 순서의 코드다.

# 셀 1: 첨부된 좌우 영상을 읽고 같은 높이의 안내선을 표시한다.
from pathlib import Path
import csv
import hashlib
import json
import platform
import cv2
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Image, Markdown

# Python 파일은 파일 위치, 노트북은 현재 작업 폴더에서 assets를 찾는다.
ROOT = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
ASSETS = ROOT / 'assets'
cv2.setNumThreads(1)
cv2.setRNGSeed(42)

def read_gray(name):
    # 한글 경로도 읽을 수 있도록 파일 바이트를 OpenCV로 디코딩한다.
    path = ASSETS / name
    if not path.is_file():
        raise FileNotFoundError(f'입력 파일을 찾을 수 없습니다: {path}')
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f'이미지 디코딩 실패: {path}')
    return image

left = read_gray('tsukuba_l.png')
right = read_gray('tsukuba_r.png')
assert left.shape == right.shape and left.dtype == right.dtype == np.uint8
height, width = left.shape
print(f'입력 크기: {width} × {height}, OpenCV: {cv2.__version__}')

def finish(fig, name):
    # 같은 그림을 MD용 PNG와 노트북 출력으로 사용한다.
    fig.tight_layout()
    path = ASSETS / name
    fig.savefig(path, dpi=140, facecolor='white')
    plt.close(fig)
    display(Image(filename=str(path)))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, image, title in zip(axes, [left, right], ['Tsukuba: left', 'Tsukuba: right']):
    ax.imshow(image, cmap='gray', vmin=0, vmax=255)
    for y in [60, 140, 220]:
        ax.axhline(y, color='cyan', linewidth=0.7)
    ax.set_title(title)
    ax.axis('off')
finish(fig, '01_stereo_pair.png')

# 셀 2: 실제 체커보드 관측값으로 보정하는 함수이며, 이번 영상에는 호출하지 않는다.
def calibrate_pair(object_points, left_points, right_points, image_size):
    # object_points: 보드 위 3차원 점, left/right_points: 같은 점의 좌우 영상 좌표.
    count = len(object_points)
    if not (count == len(left_points) == len(right_points)) or count < 3:
        raise ValueError('서로 대응하는 여러 자세의 좌우 보정 관측이 필요합니다.')

    # OpenCV가 요구하는 float32 배열과 점 모양으로 맞춘다.
    obj = [np.asarray(p, np.float32).reshape(-1, 3) for p in object_points]
    pts_l = [np.asarray(p, np.float32).reshape(-1, 1, 2) for p in left_points]
    pts_r = [np.asarray(p, np.float32).reshape(-1, 1, 2) for p in right_points]
    for p3, pl, pr in zip(obj, pts_l, pts_r):
        if not (len(p3) == len(pl) == len(pr)):
            raise ValueError('한 관측 안의 3차원 점과 좌우 점 개수가 다릅니다.')

    # 각 카메라의 내부 행렬 K와 렌즈 왜곡 D를 추정한다.
    rms_l, K_l, D_l, _, _ = cv2.calibrateCamera(obj, pts_l, image_size, None, None)
    rms_r, K_r, D_r, _, _ = cv2.calibrateCamera(obj, pts_r, image_size, None, None)
    # 내부 파라미터를 고정하고 왼쪽→오른쪽 회전과 이동을 추정한다.
    rms, K_l, D_l, K_r, D_r, R, T, E, F = cv2.stereoCalibrate(
        obj, pts_l, pts_r, K_l, D_l, K_r, D_r, image_size,
        flags=cv2.CALIB_FIX_INTRINSIC)
    return dict(K_l=K_l, D_l=D_l, K_r=K_r, D_r=D_r, R=R, T=T,
                rms_left=rms_l, rms_right=rms_r, rms_stereo=rms, E=E, F=F)

print('보정 함수 정의 완료. 실제 보정 실행: 없음 — 체커보드 관측값 미제공')

# 셀 3: 보정값이 제공된 경우의 정렬 경로를 정의한다.
def rectify_with_calibration(image_l, image_r, calibration):
    # 현재 입력과 같은 해상도에 맞는 실제 보정값을 전달해야 한다.
    if image_l.shape[:2] != image_r.shape[:2]:
        raise ValueError('좌우 영상 크기가 다릅니다.')
    size = (image_l.shape[1], image_l.shape[0])
    c = calibration
    R_l, R_r, P_l, P_r, Q, roi_l, roi_r = cv2.stereoRectify(
        c['K_l'], c['D_l'], c['K_r'], c['D_r'], size, c['R'], c['T'],
        flags=cv2.CALIB_ZERO_DISPARITY, alpha=0)
    # 각 출력 픽셀이 원본의 어느 위치를 읽을지 좌표 맵을 만든다.
    map_l = cv2.initUndistortRectifyMap(c['K_l'], c['D_l'], R_l, P_l, size, cv2.CV_32FC1)
    map_r = cv2.initUndistortRectifyMap(c['K_r'], c['D_r'], R_r, P_r, size, cv2.CV_32FC1)
    rect_l = cv2.remap(image_l, *map_l, interpolation=cv2.INTER_LINEAR)
    rect_r = cv2.remap(image_r, *map_r, interpolation=cv2.INTER_LINEAR)
    return rect_l, rect_r, dict(P_l=P_l, P_r=P_r, Q=Q, roi_l=roi_l, roi_r=roi_r)

# 이번 입력은 정렬된 영상으로 가정해 원본 그대로 사용한다. 이 복사는 정렬 연산이 아니다.
rect_l = left.copy()
rect_r = right.copy()
print('현재 계산 경로: 제공된 Tsukuba 좌우 영상 그대로 사용')

# 셀 4: 특징점 대응으로 수평 정렬 가정을 점검한다.
orb = cv2.ORB_create(nfeatures=1500, fastThreshold=10)
key_l, desc_l = orb.detectAndCompute(rect_l, None)
key_r, desc_r = orb.detectAndCompute(rect_r, None)
if desc_l is None or desc_r is None:
    raise RuntimeError('정렬 진단에 필요한 특징점을 찾지 못했습니다.')

# ORB 기본 이진 기술자는 해밍 거리를 사용한다.
pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(desc_l, desc_r, k=2)
good = []
for pair in pairs:
    if len(pair) == 2:
        first, second = pair
        if first.distance < 0.75 * second.distance:
            good.append(first)
if not good:
    raise RuntimeError('비율 검사를 통과한 대응점이 없습니다.')

points_l = np.float32([key_l[m.queryIdx].pt for m in good])
points_r = np.float32([key_r[m.trainIdx].pt for m in good])
dx = points_l[:, 0] - points_r[:, 0]
dy = points_l[:, 1] - points_r[:, 1]
alignment = {
    'ratio_test_matches': len(good),
    'median_abs_vertical_error_px': float(np.median(np.abs(dy))),
    'p90_abs_vertical_error_px': float(np.percentile(np.abs(dy), 90)),
    'fraction_abs_vertical_error_le_1px': float(np.mean(np.abs(dy) <= 1)),
    'median_horizontal_disparity_px': float(np.median(dx)),
    'fraction_positive_horizontal_disparity': float(np.mean(dx > 0)),
}
print(json.dumps(alignment, ensure_ascii=False, indent=2))

# 그림에는 거리 순 상위 24쌍만 표시하지만, 통계에는 모든 통과 후보를 사용했다.
selected = sorted(good, key=lambda m: m.distance)[:24]
matched = cv2.drawMatches(rect_l, key_l, rect_r, key_r, selected, None,
    matchColor=(0, 255, 0), flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
fig, axes = plt.subplots(2, 1, figsize=(11, 7.5))
axes[0].imshow(cv2.cvtColor(matched, cv2.COLOR_BGR2RGB))
axes[0].set_title('24 descriptor matches: diagnostic only')
axes[0].axis('off')
axes[1].scatter(dx, dy, s=9, alpha=0.5)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].axhspan(-1, 1, color='green', alpha=0.12)
axes[1].set(xlabel='x_left - x_right (pixels)', ylabel='y_left - y_right (pixels)',
            title='All ratio-test matches: vertical residual')
finish(fig, '02_alignment_check.png')

# 셀 5: SGBM의 왼쪽 기준 시차를 계산한다.
MIN_DISPARITY = 0
NUM_DISPARITIES = 32
BLOCK_SIZE = 5
assert NUM_DISPARITIES > 0 and NUM_DISPARITIES % 16 == 0
assert BLOCK_SIZE >= 1 and BLOCK_SIZE % 2 == 1

def make_matcher(min_disparity):
    # 그레이스케일 입력이므로 채널 수 1에 맞춘 시차 변화 벌점을 사용한다.
    return cv2.StereoSGBM_create(
        minDisparity=min_disparity, numDisparities=NUM_DISPARITIES,
        blockSize=BLOCK_SIZE, P1=8 * BLOCK_SIZE**2, P2=32 * BLOCK_SIZE**2,
        uniquenessRatio=10, speckleWindowSize=50, speckleRange=2,
        disp12MaxDiff=1, preFilterCap=31, mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY)

matcher_l = make_matcher(MIN_DISPARITY)
raw_l = matcher_l.compute(rect_l, rect_r)
# 1/16픽셀 단위 정수를 실제 픽셀 단위 float32로 바꾼다.
disp_l = raw_l.astype(np.float32) / 16.0
valid_l = (raw_l > (MIN_DISPARITY - 1) * 16) & (disp_l > 0)
if not np.any(valid_l):
    raise RuntimeError('양의 시차가 없습니다. 좌우 순서와 탐색 범위를 확인하세요.')

# 시각화 상한은 계산값을 읽기 쉽게 올림한 것이며 검색 범위를 바꾸지 않는다.
view_max = float(np.ceil(np.max(disp_l[valid_l])))
disp_cmap = plt.get_cmap('turbo').copy()
disp_cmap.set_bad('#333333')
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
axes[0].imshow(rect_l, cmap='gray', vmin=0, vmax=255)
axes[0].set_title('Reference: left image')
im = axes[1].imshow(np.where(valid_l, disp_l, np.nan), cmap=disp_cmap,
                    vmin=0, vmax=view_max)
axes[1].set_title('SGBM disparity: positive values')
for ax in axes:
    ax.axis('off')
fig.colorbar(im, ax=axes[1], label='Disparity (pixels)', shrink=0.8)
print(f'양의 시차를 가진 픽셀 비율: {valid_l.mean():.2%}')
finish(fig, '03_disparity_raw.png')

# 셀 6: 오른쪽 기준 시차를 별도로 구하고 좌우 일관성을 확인한다.
MIN_DISPARITY_R = -MIN_DISPARITY - NUM_DISPARITIES + 1
matcher_r = make_matcher(MIN_DISPARITY_R)
raw_r = matcher_r.compute(rect_r, rect_l)
disp_r = raw_r.astype(np.float32) / 16.0

# 왼쪽 픽셀이 가리키는 오른쪽 x좌표를 구한다.
yy, xx = np.indices(disp_l.shape)
xr = np.rint(xx - disp_l).astype(np.int32)
inside = (xr >= 0) & (xr < width)
xr_safe = np.clip(xr, 0, width - 1)  # 배열 접근용 제한이며 유효 판정에는 inside도 필요하다.
sampled_r = disp_r[yy, xr_safe]
valid_r_at_match = (raw_r[yy, xr_safe] > (MIN_DISPARITY_R - 1) * 16) & (sampled_r <= 0)
lr_error = np.abs(disp_l + sampled_r)
LR_THRESHOLD = 1.0
valid = valid_l & inside & valid_r_at_match & (lr_error <= LR_THRESHOLD)
if not valid.any():
    raise RuntimeError('좌우 일관성 검사를 통과한 픽셀이 없습니다.')
disparity = np.where(valid, disp_l, np.nan).astype(np.float32)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
im = axes[0].imshow(disparity, cmap=disp_cmap, vmin=0, vmax=view_max)
axes[0].set_title('Disparity after consistency check')
fig.colorbar(im, ax=axes[0], label='pixels', shrink=0.7)
axes[1].imshow(valid, cmap='gray', vmin=0, vmax=1)
axes[1].set_title('Accepted pixels (white)')
error_view = np.where(valid_l & inside & valid_r_at_match, lr_error, np.nan)
err_cmap = plt.get_cmap('magma').copy()
err_cmap.set_bad('#333333')
im = axes[2].imshow(error_view, cmap=err_cmap, vmin=0, vmax=3)
axes[2].set_title('Consistency residual (display capped)')
fig.colorbar(im, ax=axes[2], label='pixels; values > 3 share top color', shrink=0.7)
for ax in axes:
    ax.axis('off')
print(f'전체 픽셀 중 검사 통과 비율: {valid.mean():.2%} — 정확도 점수가 아님')
finish(fig, '04_consistency.png')

# 셀 7: 보정값을 가정해 미터 단위로 바꾸지 않고 상대 깊이 지표를 계산한다.
reference_disparity = float(np.median(disparity[valid]))
relative_depth_index = np.full(disparity.shape, np.nan, np.float32)
# 아래 지표는 주점 x좌표 차이가 0이라는 가정 아래 시차 역수를 비교한다.
relative_depth_index[valid] = reference_disparity / disparity[valid]

# 좌표는 (x0, y0, x1, y1)이며 끝 좌표는 포함하지 않는다. 사람이 직접 고른 영역이다.
regions = [
    ('Head', '머리 부근', (125, 160, 165, 220), '#00bfff'),
    ('Books', '배경 책장', (45, 15, 120, 65), '#00ff66'),
    ('Lamp', '스탠드 부근', (220, 115, 245, 155), '#ff9933'),
]
roi_rows = []
for name, label, (x0, y0, x1, y1), color in regions:
    mask_roi = valid[y0:y1, x0:x1]
    values = disparity[y0:y1, x0:x1][mask_roi]
    median_d = float(np.median(values)) if values.size else None
    median_index = float(np.median(relative_depth_index[y0:y1, x0:x1][mask_roi])) if values.size else None
    roi_rows.append(dict(region=name, label=label, x0=x0, y0=y0, x1=x1, y1=y1,
                         valid_fraction=float(mask_roi.mean()), median_disparity_px=median_d,
                         median_relative_depth_index=median_index))

table = '| 선택 영역 | 통과 픽셀 비율 | 시차 중앙값(px) | 상대 깊이 지표 중앙값 |\n'
table += '| :---: | :---: | :---: | :---: |\n'
for row in roi_rows:
    d = '계산 불가' if row['median_disparity_px'] is None else f"{row['median_disparity_px']:.3f}"
    z = '계산 불가' if row['median_relative_depth_index'] is None else f"{row['median_relative_depth_index']:.3f}"
    table += f"| {row['label']} | {row['valid_fraction']:.2%} | {d} | {z} |\n"
display(Markdown(table))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
axes[0].imshow(rect_l, cmap='gray', vmin=0, vmax=255)
for name, label, (x0, y0, x1, y1), color in regions:
    axes[0].add_patch(plt.Rectangle((x0, y0), x1-x0, y1-y0, fill=False, edgecolor=color, linewidth=2))
    axes[0].text(x0, y0-4, name, color=color, fontsize=10)
axes[0].set_title('Manually selected regions')
z_cmap = plt.get_cmap('viridis').copy()
z_cmap.set_bad('#333333')
im = axes[1].imshow(relative_depth_index, cmap=z_cmap,
                    vmin=0, vmax=float(np.nanmax(relative_depth_index)))
axes[1].set_title('Relative depth index: not meters')
fig.colorbar(im, ax=axes[1], label='d_reference / d (dimensionless)', shrink=0.8)
for ax in axes:
    ax.axis('off')
finish(fig, '05_relative_depth.png')

# 셀 8: 실제 보정값이 있을 때만 사용하는 깊이 함수와 현재 실습 결과를 저장한다.
def metric_depth_from_calibration(disparity_px, valid_mask, focal_px, baseline_m, cx_offset_px):
    # baseline_m을 미터로 넣었을 때 출력도 미터가 된다. 외부에서 확인한 값을 전달한다.
    parameters = np.asarray([focal_px, baseline_m, cx_offset_px], dtype=np.float64)
    if not np.all(np.isfinite(parameters)) or focal_px <= 0 or baseline_m <= 0:
        raise ValueError('유효한 초점거리·베이스라인·주점 차이가 필요합니다.')
    if disparity_px.shape != valid_mask.shape:
        raise ValueError('시차와 마스크의 크기가 다릅니다.')
    d_eff = np.asarray(disparity_px, np.float32) - float(cx_offset_px)
    valid_depth = np.asarray(valid_mask, bool) & np.isfinite(d_eff) & (d_eff > 0)
    depth_m = np.full(d_eff.shape, np.nan, np.float32)
    depth_m[valid_depth] = float(focal_px) * float(baseline_m) / d_eff[valid_depth]
    return depth_m, valid_depth

# 원본 파일 해시를 기록해 어떤 좌우 입력을 계산했는지 구분한다.
input_hashes = {name: hashlib.sha256((ASSETS/name).read_bytes()).hexdigest()
                for name in ['tsukuba_l.png', 'tsukuba_r.png']}
results = {
    'python': platform.python_version(), 'opencv': cv2.__version__, 'numpy': np.__version__,
    'input_pair': 'user-provided Tsukuba', 'image_size_wh': [width, height],
    'input_sha256': input_hashes, 'rectification_assumed': True,
    'calibration_performed': False, 'calibration_parameters_provided': False,
    'ground_truth_available': False, 'metric_depth_computed': False,
    'relative_index_assumption_cx_difference_px': 0.0,
    'matcher': {'min_disparity_left': MIN_DISPARITY, 'min_disparity_right': MIN_DISPARITY_R,
                'num_disparities': NUM_DISPARITIES, 'block_size': BLOCK_SIZE,
                'lr_threshold_px': LR_THRESHOLD, 'mode': 'SGBM_3WAY'},
    'alignment_diagnostic': alignment,
    'positive_disparity_fraction': float(valid_l.mean()),
    'consistency_pass_fraction': float(valid.mean()),
    'accepted_disparity_min_px': float(np.min(disparity[valid])),
    'accepted_disparity_max_px': float(np.max(disparity[valid])),
    'reference_disparity_px': reference_disparity,
    'manual_regions': roi_rows,
}
# PNG는 표시용이며, 재분석에는 NaN과 부호를 보존한 NPZ 배열을 사용한다.
np.savez_compressed(ROOT/'stereo_results.npz', left=rect_l, right=rect_r,
    disparity_left_raw=raw_l, disparity_right_raw=raw_r,
    disparity_left_px=disp_l, disparity_right_px=disp_r,
    disparity_accepted_px=disparity, positive_mask=valid_l, consistent_mask=valid,
    lr_error_px=lr_error, relative_depth_index=relative_depth_index)
(ROOT/'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
with (ROOT/'roi_summary.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(roi_rows[0]))
    writer.writeheader()
    writer.writerows(roi_rows)

# 계산 구조를 확인한다. 정답 시차와 비교하는 정확도 검사는 아니다.
assert raw_l.dtype == np.int16 and disparity.shape == left.shape
assert np.all(np.isfinite(disparity[valid])) and np.all(disparity[valid] > 0)
assert np.isnan(disparity[~valid]).all()
assert np.all(lr_error[valid] <= LR_THRESHOLD)
assert np.allclose(relative_depth_index[valid] * disparity[valid], reference_disparity)
print('저장 완료: results.json, stereo_results.npz, roi_summary.csv')
print('미터 단위 깊이: 계산하지 않음 / 정답 대비 오차: 계산하지 않음')
