# 8. 영상 스티칭 — 검토 내역

검토일: 2026-10-25

## 개념·설명 검토

핵심 설명에서 수정이 필요한 오류를 발견하지 않았다.

B→A 변환 방향, 캔버스 이동 행렬 T와 H의 곱 순서, 역방향 샘플링, 별도 유효 마스크, 블렌딩과 정렬의 차이를 확인했다. 같은 사진의 겹치는 크롭 실험으로 실제 다중 촬영의 성능을 일반화하지 않는다.

## 이번 확인 범위

- 공식 문서와 핵심 개념·수식·함수 설명을 대조했다.
- 설명 수정은 MD와 노트북에 동일하게 반영했다. 계산 코드와 기존 출력은 변경하지 않았다.
- 7개 코드 셀의 Python 구문, MD·IPYNB·practice.py의 계산 코드 일치, 한국어 주석과 표 중앙 정렬을 확인했다.
- 본문의 이미지 경로와 ZIP 내부 파일의 무결성을 확인했다.
- 이번 개념 검토에서 OpenCV 전체 실습을 재실행하지 않았다. 기존 실행 결과와 각 본문에 적힌 검증 범위를 유지했다. 실제 Jupyter Run All을 새로 검증했다는 뜻은 아니다.

## 대조한 공식 문서

- [Geometric Image Transformations](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html)
- [Feature Matching and Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)
