# 6. 에지 및 직선 검출 — 검토 내역

검토일: 2026-10-25

## 개념·설명 검토

허프 변환의 비교 설명을 수정했다.

“전체 점의 모든 조합”이라는 표현을 삭제했다. 표준 허프는 각 에지 점의 후보 직선 투표이며, HoughLinesP는 점진적 확률적 방법으로 선분을 찾는다고 설명했다. Canny의 임계값은 픽셀 밝기가 아닌 미분 응답 크기에 적용하며, 허프의 theta는 법선 각도라는 설명도 확인했다.

## 이번 확인 범위

- 공식 문서와 핵심 개념·수식·함수 설명을 대조했다.
- 설명 수정은 MD와 노트북에 동일하게 반영했다. 계산 코드와 기존 출력은 변경하지 않았다.
- 8개 코드 셀의 Python 구문, MD·IPYNB·practice.py의 계산 코드 일치, 한국어 주석과 표 중앙 정렬을 확인했다.
- 본문의 이미지 경로와 ZIP 내부 파일의 무결성을 확인했다.
- 이번 개념 검토에서 OpenCV 전체 실습을 재실행하지 않았다. 기존 실행 결과와 각 본문에 적힌 검증 범위를 유지했다. 실제 Jupyter Run All을 새로 검증했다는 뜻은 아니다.

## 대조한 공식 문서

- [Hough Line Transform](https://docs.opencv.org/4.x/d6/d10/tutorial_py_houghlines.html)
- [Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html)
