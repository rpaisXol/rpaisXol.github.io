---
tags:
  - 파이썬
  - 데이터분석
  - 데이터전처리
title: (한일 고령화 분석 1편) 지역별 고령화 문제 정의 및 의료 및 돌봄 인프라 데이터 수집
aliases:
  - 데이터 분석 보고서 1장
  - 문제 정의 및 데이터 수집
created: 2026-09-02
status: Version 1.0
---

## 지방 소멸 위기와 고령화 인프라 격차

> [!abstract] 배경 및 목적
> * **문제점:** 한국과 일본은 전 세계적으로 고령화 속도가 가장 빠른 국가이나, 지역별 의료 및 돌봄 인프라 대응 수준은 심각한 불균형을 보이고 있다.
> * **문제의 핵심:** 인프라가 뒷받침되지 않은 채 진행되는 지방의 고령화는 의료 공백과 돌봄 부담을 가중시키며, 궁극적으로 '지방 소멸'을 가속화하는 근본 원인이다.
> * **분석 목표:** 양국의 고령화율, 인구 1만 명당 병상 수 및 요양기관 수, 자체 산출한 '인프라 격차지수'를 실증 데이터로 추적하여, 국가적 고령화 위기 극복을 위한 정책적 대안을 모색한다.

---

## 1. 데이터 수집

### 1.1. 주요 지표 및 수집 출처
한일 양국의 정부 공식 통계 포털 원천 데이터를 직접 수집 혹은 API 호출을 진행.
* **한국 (KOSIS 국가데이터처):** 
  * 고령인구비율(한국, 시도) [고령화 인구비율](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
  * 시도별 장기요양기관 현황(한국, 시도) [시도별 장기요양기관 현황](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
  * 인구 천 명당 의료기관 병상수(한국, 시도) [한국의 인구 천 명당 의료기관 병상수](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
* **일본 (e-Stat 정부통계포털):** 
  * 인구추계(일본, 도도부현) [인구추계](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
  * 사회·인구통계체계의 의료 및 복지 분야 지표(일본, 도도부현)[사회·인구통계체계의 의료 및 복지 분야](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)

### 1.2. 데이터 수집 파이프라인

* 사전준비 (1): 파이썬 설치 및 라이브러리 설치
1. 파이썬 및 아나콘다 설치
2. 파이썬 `requests`,`pandas` 라이브러리를 설치

```bash
pip install requests pandas
```

사전준비 (2): e-stat 회원가입
1. https://www.e-stat.go.jp 회원가입 (이메일 인증)
2. 마이페이지 > API機能 에서 appId 발급
3. 프로젝트 루트(고령화/)에 .env 파일을 만들고 아래처럼 채워넣기: ESTAT_APP_ID=발급받은_appId 

사전준비 (3): kosis 회원가입
1. https://kosis.kr 회원가입
2. 로그인 후 Open API > 활용신청 > 인증키 발급 (자동승인, 즉시 발급)

<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>

#### 1.2.1 e-Stat API로 일본 도도부현별 고령화·의료·복지 데이터 수집

* **데이터 수집 개선 사항**
1. 데이터 누락 방지 (페이지네이션 적용)
   - API의 1회 최대 제공량(10만 건) 제한으로 인한 데이터 잘림 현상을 해결하기 위해, startPosition 기반의 페이지네이션을 도입하여 모든 데이터를 끝까지 수집
2. 중복 집계 방지 (지역 단위 정제)
   - 시/구 단위 데이터가 혼재된 원본에서, 하위 행정구역(구, 레벨3)을 제외하고 '시(레벨2)' 단위만 추출하여 도도부현(광역) 단위로 정확하게 합산
3. 끊김 없는 시계열 데이터 확보 (데이터 소스 변경)
   - 매년 갱신되는 '인구추계(2015~2023)' 데이터를 활용하여 연도별 빈틈없는 총인구 및 65세 이상 인구 통계를 구축

<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 1. 환경설정
```python
import os
import time
import requests
import pandas as pd

# 1. 환경 설정 (.env 로드)
def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


load_env(os.path.join(os.path.dirname(__file__), "..", ".env"))

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID")
if not ESTAT_APP_ID:
    raise RuntimeError(
        "ESTAT_APP_ID가 설정되지 않았습니다. 고령화/.env 파일에 "
        "ESTAT_APP_ID=발급받은_appId 를 추가하세요."
    )

API_VERSION = "2.1" # API키 버전
MAX_RECORDS_PER_REQUEST = 100000  # e-Stat API 응답 상한

```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 2. 데이터 단일 요청
```python
# 인구 데이터용 (매년 갱신되는 인구추계 데이터 활용)
POP_ESTIMATE_SERIES = [
    ("0003459027", "2015년국세조사기준"),  # 2015~2019
    ("0003448237", "2020년국세조사기준"),  # 2020~2023
]
POP_CAT02_TOTAL = "01000"
POP_CAT02_65PLUS = ["01014", "01015", "01016", "01017", "04018"]

# 의료 및 복지 데이터용
TABLES = {
    "I_의료": {
        "stats_data_id": "0000020209",
        "cat01": ["I5211", "I5212"],  # 병원 병상수, 일반진료소 병상수
    },
    "J_복지": {
        "stats_data_id": "0000020210",
        # 개호노인복지시설 수/정원. 조사양식이 변경되어 두 버전을 모두 받아 합칩니다.
        "cat01": ["J230121", "J230124", "J230127", "J230128"],
    },
}

# 분리된 조사양식 항목명을 통일하기 위한 맵핑 규칙
CAT01_NAME_UNIFY = {
    "J230121_介護老人福祉施設数（詳細票）": "介護老人福祉施設数",
    "J230127_介護老人福祉施設数（基本票）": "介護老人福祉施設数",
    "J230124_介護老人福祉施設定員数（詳細票）": "介護老人福祉施設定員数",
    "J230128_介護老人福祉施設定員数（基本票）": "介護老人福祉施設定員数",
}

# 분석 대상 연도 범위
TIME_FROM = "2015100000"
TIME_TO = "2023100000"
```
<!-- ------------------------------------------------------------------------------------구분선------------------------------------------------------------------------------------------------>
##### 3. API 통신 및 원시 데이터 수집
```python
# API 서버에 특정 페이지의 통계 데이터를 요청
def fetch_estat_page(stats_data_id: str, cat01_codes: list, start_position: int):
    url = f"https://api.e-stat.go.jp/rest/{API_VERSION}/app/json/getStatsData"
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "J",
        "statsDataId": stats_data_id,
        "cdCat01": ",".join(cat01_codes),
        "cdTimeFrom": TIME_FROM,
        "cdTimeTo": TIME_TO,
        "metaGetFlg": "Y",
        "cntGetFlg": "N",
        "sectionHeaderFlg": "1",
        "startPosition": start_position,
    }
    res = requests.get(url, params=params, timeout=30)
    res.raise_for_status()
    data = res.json()

    result = data.get("GET_STATS_DATA", {}).get("RESULT", {})
    if result.get("STATUS") != 0:
        raise RuntimeError(f"e-Stat API 오류: {result.get('ERROR_MSG')}")

    return data["GET_STATS_DATA"]["STATISTICAL_DATA"]

# cat01/연도로 좁힌 뒤에도 10만 건이 넘을 수 있으므로 끝까지 페이지네이션
def fetch_estat(stats_data_id: str, cat01_codes: list) -> pd.DataFrame:
    all_values = []
    code_maps = {}
    area_levels = {}
    start_position = 1

    while True:
        stat_data = fetch_estat_page(stats_data_id, cat01_codes, start_position)
        values = stat_data["DATA_INF"]["VALUE"]
        if isinstance(values, dict):
            values = [values]
        all_values.extend(values)

        # 메타정보는 첫 페이지에서만 파싱하면 충분 (매 페이지 동일)
        if not code_maps:
            class_objs = stat_data.get("CLASS_INF", {}).get("CLASS_OBJ", [])
            for obj in class_objs:
                obj_id = obj.get("@id")
                classes = obj.get("CLASS")
                if isinstance(classes, dict):
                    classes = [classes]
                if classes:
                    code_maps[obj_id] = {c["@code"]: c["@name"] for c in classes}
                    if obj_id == "area":
                        area_levels = {c["@code"]: c.get("@level") for c in classes}

        result_inf = stat_data.get("RESULT_INF", {})
        total = result_inf.get("TOTAL_NUMBER", len(all_values))
        to_number = result_inf.get("TO_NUMBER", len(all_values))
        next_key = result_inf.get("NEXT_KEY")
        print(f"    {to_number}/{total} 건 수신...")

        if not next_key or int(to_number) >= int(total):
            break
        start_position = int(next_key)
        time.sleep(0.5)

    df = pd.DataFrame(all_values)
    return df, code_maps, area_levels

# 데이터 누락을 방지하기 위해 다음 페이지를 반복 호출하여 모든 데이터를 확보
def fetch_estat(stats_data_id: str, cat01_codes: list) -> pd.DataFrame:
    all_values = []
    code_maps = {}
    area_levels = {}
    start_position = 1

    while True:
        stat_data = fetch_estat_page(stats_data_id, cat01_codes, start_position)
        values = stat_data["DATA_INF"]["VALUE"]
        if isinstance(values, dict):
            values = [values]
        all_values.extend(values)

        if not code_maps:
            class_objs = stat_data.get("CLASS_INF", {}).get("CLASS_OBJ", [])
            for obj in class_objs:
                obj_id = obj.get("@id")
                classes = obj.get("CLASS")
                if isinstance(classes, dict):
                    classes = [classes]
                if classes:
                    code_maps[obj_id] = {c["@code"]: c["@name"] for c in classes}
                    if obj_id == "area":
                        area_levels = {c["@code"]: c.get("@level") for c in classes}

        result_inf = stat_data.get("RESULT_INF", {})
        total = result_inf.get("TOTAL_NUMBER", len(all_values))
        to_number = result_inf.get("TO_NUMBER", len(all_values))
        next_key = result_inf.get("NEXT_KEY")
        print(f"    {to_number}/{total} 건 수신...")

        if not next_key or int(to_number) >= int(total):
            break
        start_position = int(next_key)
        time.sleep(0.5)

    df = pd.DataFrame(all_values)
    return df, code_maps, area_levels
```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 4. 데이터 해독 및 가공
```python
# 암호화된 코드를 사람이 읽을 수 있는 실제 명칭으로 치환
def apply_code_maps(df: pd.DataFrame, code_maps: dict) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        key = col.lstrip("@")
        if key in code_maps:
            df[f"{key}_name"] = df[col].map(code_maps[key])
    return df

# 시/구 단위 데이터를 도도부현(광역) 단위로 묶어 합산하며, 중복 집계를 방지
def aggregate_to_prefecture(df: pd.DataFrame, area_levels: dict) -> pd.DataFrame:
    df = df.copy()
    df["area_level"] = df["@area"].map(area_levels)
    
    muni = df[df["area_level"] == "2"].copy()
    muni["prefecture"] = muni["area_name"].str.split(" ", n=1).str[0]
    muni["value"] = pd.to_numeric(muni["$"], errors="coerce")
    muni["cat01_name"] = muni["cat01_name"].replace(CAT01_NAME_UNIFY)

    agg = (
        muni.groupby(["prefecture", "cat01_name", "time_name"], as_index=False)["value"]
        .sum()
    )
    return agg
```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 5. 인구 데이터 전용 특수 수집
```python
# 2015~2023년 총인구 및 65세 이상 인구를 추출하는 전용 모듈
def fetch_population_estimates() -> pd.DataFrame:
    all_rows = []

    for stats_data_id, series_label in POP_ESTIMATE_SERIES:
        print(f"[e-Stat] 수집 중: 인구추계 {series_label} ({stats_data_id})")
        url = f"https://api.e-stat.go.jp/rest/{API_VERSION}/app/json/getStatsData"
        params = {
            "appId": ESTAT_APP_ID,
            "lang": "J",
            "statsDataId": stats_data_id,
            "cdCat01": "000",
            "cdCat02": ",".join([POP_CAT02_TOTAL] + POP_CAT02_65PLUS),
            "cdCat03": "001",
            "metaGetFlg": "Y",
            "cntGetFlg": "N",
        }
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        data = res.json()
        result = data.get("GET_STATS_DATA", {}).get("RESULT", {})
        if result.get("STATUS") != 0:
            raise RuntimeError(f"e-Stat API 오류: {result.get('ERROR_MSG')}")

        stat_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]
        values = stat_data["DATA_INF"]["VALUE"]
        if isinstance(values, dict):
            values = [values]

        class_objs = stat_data.get("CLASS_INF", {}).get("CLASS_OBJ", [])
        code_maps = {}
        for obj in class_objs:
            obj_id = obj.get("@id")
            classes = obj.get("CLASS")
            if isinstance(classes, dict):
                classes = [classes]
            if classes:
                code_maps[obj_id] = {c["@code"]: c["@name"] for c in classes}

        df = pd.DataFrame(values)
        df["area_name"] = df["@area"].map(code_maps["area"])
        df["cat02_name"] = df["@cat02"].map(code_maps["cat02"])
        df["time_name"] = df["@time"].map(code_maps["time"])
        
        df["value"] = pd.to_numeric(df["$"], errors="coerce") * 1000
        df = df[df["@area"] != "00000"].copy()
        df["year"] = df["time_name"].str.extract(r"(\d{4})")[0]

        total = df[df["@cat02"] == POP_CAT02_TOTAL].copy()
        total["cat01_name"] = "A1101_総人口"

        plus65 = (
            df[df["@cat02"].isin(POP_CAT02_65PLUS)]
            .groupby(["area_name", "year"], as_index=False)["value"]
            .sum()
        )
        plus65["cat01_name"] = "A1303_65歳以上人口"

        for part in (total[["area_name", "year", "value", "cat01_name"]], plus65):
            part = part.rename(columns={"area_name": "prefecture", "year": "time_name"})
            part["time_name"] = part["time_name"] + "年度"
            all_rows.append(part[["prefecture", "cat01_name", "time_name", "value"]])

    return pd.concat(all_rows, ignore_index=True).sort_values(
        ["prefecture", "cat01_name", "time_name"]
    )
```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 6. 전체 파이프라인 통합 및 실행
```python
# 인구, 의료, 복지 데이터를 차례대로 수집하고 통합
def collect_all() -> dict:
    results = {"A_인구세대": fetch_population_estimates()}
    for name, cfg in TABLES.items():
        print(f"[e-Stat] 수집 중: {name} ({cfg['stats_data_id']}, cat01={cfg['cat01']})")
        try:
            df, code_maps, area_levels = fetch_estat(cfg["stats_data_id"], cfg["cat01"])
            df = apply_code_maps(df, code_maps)
            pref_df = aggregate_to_prefecture(df, area_levels)
            results[name] = pref_df
        except Exception as e:
            print(f"  -> 실패: {e}")
    return results

if __name__ == "__main__":
    print("=== e-Stat 데이터 수집 시작 (도도부현 단위 집계) ===")
    data = collect_all()
    for name, df in data.items():
        out_path = f"../data/raw/estat_{name}_prefecture.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {out_path} ({len(df)} rows, {df['prefecture'].nunique()}개 도도부현)")
        print(df.head())
```
---

#### 1.2.2 KOSIS Open API로 한국 시도별 고령화·인구·인프라 데이터 수집

* **데이터 수집 개선 사항**
1. 통신 속도 및 안정성 최적화
   - 응답 데이터의 인코딩을 UTF-8로 명시하여 JSON 파싱 시 발생하는 지연을 해결
2. 데이터 정제 및 무결성 확보
   - 항목명(item)에 포함된 불필요한 HTML 줄바꿈 태그(`<br>`)를 자동으로 제거
   - 분류축이 여러 개인 통계(예: 장기요양기관현황)에서 세부 카테고리(C2_NM)를 보존하여 데이터가 중복으로 합산되거나 뭉개지는 현상을 방지
3. 다차원 통계표 대응
   - 통계표마다 요구하는 지역 파라미터(objL) 개수가 다른 KOSIS API의 특성에 맞춰, 필요한 개수만큼 동적으로 파라미터를 생성하여 호출

<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 1. 환경 설정
```python
# API 키를 소스 코드 외부(.env)에서 불러옴
def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

load_env(os.path.join(os.path.dirname(__file__), "..", ".env"))

KOSIS_API_KEY = os.environ.get("KOSIS_API_KEY")
if not KOSIS_API_KEY:
    raise RuntimeError(
        "KOSIS_API_KEY가 설정되지 않았습니다. 고령화/.env 파일에 "
        "KOSIS_API_KEY=발급받은_인증키 를 추가하세요."
    )
```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 2. 데이터 대상 설정
```python
# API 키를 소스 코드 외부(.env)에서 불러옴
START_YEAR = "2015"
END_YEAR = "2023"

# 수집 대상 통계표 매핑: 지표명 -> (orgId, tblId, 분류축(objL) 개수)
KOSIS_TABLES = {
    "고령인구비율": ("101", "DT_1YL20631", 1),
    "장기요양기관현황": ("350", "DT_35006_N019", 2),
    "의료기관병상수": ("101", "DT_1YL20971", 1),
}
```

<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 3. API 통신 및 데이터 정제
```python
# KOSIS API와 통신하여 데이터를 수집하고, 분석하기 좋은 형태로 1차 정제
def fetch_kosis(org_id: str, tbl_id: str, start_year: str, end_year: str, obj_l_count: int = 1) -> pd.DataFrame:
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    params = {
        "method": "getList",
        "apiKey": KOSIS_API_KEY,
        "itmId": "ALL",
        "format": "json",
        "jsonVD": "Y",
        "prdSe": "Y",
        "startPrdDe": start_year,
        "endPrdDe": end_year,
        "orgId": org_id,
        "tblId": tbl_id,
    }
    
    # 통계표의 분류축(objL) 개수만큼 파라미터를 동적으로 추가합니다.
    for i in range(1, obj_l_count + 1):
        params[f"objL{i}"] = "ALL"

    res = requests.get(url, params=params, timeout=30)
    res.raise_for_status()
    res.encoding = "utf-8"  # JSON 파싱 속도 저하 방지
    data = res.json()

    if isinstance(data, dict) and "err" in data:
        raise RuntimeError(f"KOSIS API 오류: {data}")

    df = pd.DataFrame(data)
    
    # 필수 컬럼만 추출하고 직관적인 이름으로 변경합니다.
    # 분류축이 2개 이상일 때 세부 유형(C2_NM)이 누락되어 중복행이 발생하는 것을 방지합니다.
    keep_cols = [c for c in ["C1_NM", "C2_NM", "PRD_DE", "ITM_NM", "DT"] if c in df.columns]
    df = df[keep_cols].rename(columns={
        "C1_NM": "region", 
        "C2_NM": "category2", 
        "PRD_DE": "year", 
        "ITM_NM": "item", 
        "DT": "value"
    })

    # 데이터 내 불필요한 HTML 태그를 깔끔하게 제거합니다.
    if "item" in df.columns:
        df["item"] = (
            df["item"]
            .str.replace("＜br＞", "", regex=False)
            .str.replace("<br>", "", regex=False)
        )

    return df
```
<!-- ------------------------------------------------------------------------------------ 구분선 ------------------------------------------------------------------------------------------------>
##### 4. 전체 파이프라인 통합 및 실행
```python
# 설정된 모든 KOSIS 통계표를 순회하며 수집
def collect_all_kosis() -> dict:
    results = {}
    for name, (org_id, tbl_id, obj_l_count) in KOSIS_TABLES.items():
        print(f"[KOSIS] 수집 중: {name} (orgId={org_id}, tblId={tbl_id}, objL 개수={obj_l_count})")
        try:
            df = fetch_kosis(org_id, tbl_id, START_YEAR, END_YEAR, obj_l_count)
            results[name] = df
            time.sleep(1)  # 서버 과부하를 막기 위한 간격 유지
        except Exception as e:
            print(f"  -> 실패: {e}")
            if "err': '20'" in str(e) or "'20'" in str(e):
                print(f"     -> objL(분류축) 개수 오류, KOSIS_TABLES에서 '{name}'의 objL 개수를 "
                      f"{obj_l_count + 1}로 늘려서 다시 시도해보세요.")
    return results

if __name__ == "__main__":
    print("=== KOSIS 데이터 수집 시작 ===")
    data = collect_all_kosis()
    for name, df in data.items():
        out_path = f"../data/raw/kosis_{name}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {out_path} ({len(df)} rows)")
        print(df.head())
        if "item" in df.columns:
            print("포함된 항목 목록:", df["item"].unique()[:20])
```