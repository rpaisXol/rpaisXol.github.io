# 1. 픽셀 및 색상 채널 처리 — 검토 내역

검토일: 2026-10-25

## 개념·설명 검토

핵심 설명에서 수정이 필요한 오류를 발견하지 않았다.

배열 [y, x]와 좌표 (x, y)의 구분, uint8 넘침, BGR/RGB 순서, Gray 및 YCrCb 변환식, split/merge의 정보 보존 조건을 확인했다.

## 이번 확인 범위

- 공식 문서와 핵심 개념·수식·함수 설명을 대조했다.
- 설명 수정은 MD와 노트북에 동일하게 반영했다. 계산 코드와 기존 출력은 변경하지 않았다.
- 8개 코드 셀의 Python 구문, MD·IPYNB·practice.py의 계산 코드 일치, 한국어 주석과 표 중앙 정렬을 확인했다.
- 본문의 이미지 경로와 ZIP 내부 파일의 무결성을 확인했다.
- 이번 개념 검토에서 OpenCV 전체 실습을 재실행하지 않았다. 기존 실행 결과와 각 본문에 적힌 검증 범위를 유지했다. 실제 Jupyter Run All을 새로 검증했다는 뜻은 아니다.

## 대조한 공식 문서

- [Color conversions](https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html)
