# 7. 특징점 검출 및 매칭 — 검토 내역

검토일: 2026-10-25

## 개념·설명 검토

기하 모델의 역할을 더 분명하게 설명했다.

기본행렬·필수행렬은 대응 검증에 쓰는 에피폴라 제약이며 호모그래피 같은 점 대 점 워핑 행렬이 아님을 추가했다. ORB/SIFT의 거리 함수, 비율 검사, RANSAC 인라이어가 절대적인 정답은 아니라는 설명을 확인했다.

## 이번 확인 범위

- 공식 문서와 핵심 개념·수식·함수 설명을 대조했다.
- 설명 수정은 MD와 노트북에 동일하게 반영했다. 계산 코드와 기존 출력은 변경하지 않았다.
- 7개 코드 셀의 Python 구문, MD·IPYNB·practice.py의 계산 코드 일치, 한국어 주석과 표 중앙 정렬을 확인했다.
- 본문의 이미지 경로와 ZIP 내부 파일의 무결성을 확인했다.
- 이번 개념 검토에서 OpenCV 전체 실습을 재실행하지 않았다. 기존 실행 결과와 각 본문에 적힌 검증 범위를 유지했다. 실제 Jupyter Run All을 새로 검증했다는 뜻은 아니다.

## 대조한 공식 문서

- [Feature Matching](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html)
- [Camera Calibration and 3D Reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)
