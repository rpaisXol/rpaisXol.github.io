"""실행 노트북 출력에서 Markdown과 정적 그림을 추출한다. 결과값을 재계산/조작하지 않는다."""
from pathlib import Path
import json,re,base64,hashlib,sys,platform
from urllib.parse import quote
import nbformat as nf
BASE=Path(__file__).resolve().parents[1]
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
report=[]
for item in manifest:
    n=item['chapter']; stem=item['stem']; nb=nf.read(BASE/(stem+'.ipynb'),as_version=4)
    lines=[f'> 실행 노트북: [{stem}.ipynb](<{stem}.ipynb>) · [전체 목차](README.md)\n']
    toc=[]
    for c in nb.cells:
        if c.cell_type=='markdown':
            for line in c.source.splitlines():
                if line.startswith('## '):toc.append(line[3:])
    figdir=BASE/'assets'/f'ch{n:02}'; figdir.mkdir(exist_ok=True,parents=True)
    figures=0; outputs=0; code=0; errors=[]; current='본문 예제'; current_label=''
    for c in nb.cells:
        if c.cell_type=='markdown':
            src=c.source
            if src.startswith('# '):
                src+='\n\n## 이 글의 구성\n\n'+'\n'.join('- '+t for t in toc if t!='실행 환경')
            if src.startswith('## 연습문제'): current=src.splitlines()[0].lstrip('# ')
            elif src.startswith('### ') and not src.startswith('### 코드'):current=src.splitlines()[0].lstrip('# ')
            if src.startswith('### 코드'):current_label=src.splitlines()[0].lstrip('# ')
            lines.append(src+'\n'); continue
        code+=1
        lines.append('```python\n'+c.source+'\n```\n')
        if not c.outputs:
            lines.append('- **실행 결과**: 출력 없이 변수·함수를 준비하는 셀입니다. 계산 결과는 이어지는 셀에서 사용합니다.\n')
        else:
            lines.append('**실행 결과**\n')
        for j,o in enumerate(c.outputs):
            outputs+=1
            if o.output_type=='error': errors.append({'code_cell':code,'error':o.ename,'message':o.evalue})
            if o.output_type=='stream':
                txt=re.sub(r'(?m)^Out\[\d+\]:\s*','',o.text).strip()
                if txt:lines.append('```text\n'+txt+'\n```\n')
            data=o.get('data',{})
            image_mimes=[('image/png','png'),('image/gif','gif'),('image/svg+xml','svg')]
            found=False
            for mime,ext in image_mimes:
                if mime not in data:continue
                figures+=1; fname=f'output_{code:03}_{j:02}.{ext}'
                content=data[mime]
                if isinstance(content,list):content=''.join(content)
                blob=content.encode() if ext=='svg' else base64.b64decode(content)
                (figdir/fname).write_bytes(blob)
                lines.append(f'![{current} — {current_label} 실행 그림 {figures}](assets/ch{n:02}/{fname})\n')
                lines.append(f'*그림 {n}-{figures}. {current}. 위 코드가 생성한 실제 실행 결과입니다.*\n')
                found=True; break
            if not found and 'text/plain' in data:
                txt=data['text/plain'];txt=''.join(txt) if isinstance(txt,list) else txt
                if txt.strip():lines.append('```text\n'+txt.strip()+'\n```\n')
            if o.output_type=='error':lines.append('```text\n'+o.ename+': '+o.evalue+'\n```\n')
    if n in [2,4]:lines.append(f'## 회전 가능한 3차원 그림\n\n- [3차원 생성공간 HTML 열기](assets/ch{n:02}/interactive_3d.html). 파일을 브라우저에서 열면 회전·확대할 수 있습니다.\n')
    lines.append('## 자료와 재현\n\n- 원본 코드: 제공된 `선형대수학.zip`의 `'+item['source']+'`. 코드 헤더와 기존 README에 표시된 원저자: Mike X Cohen, *Practical Linear Algebra for Data Science* / 한국어판 *개발자를 위한 실전 선형대수학*.\n- 한국어 설명·검증 예제: 본 자료를 위해 새로 작성. 문제 제목은 제공 코드의 학습 목표를 재구성.\n- [수정 내역](CHANGES.md) · [실행 및 데이터 안내](README.md) · [검증 보고서](VALIDATION.md).\n- 모든 본문 그림은 포함된 코드를 실제 실행해 생성했습니다. 6·14장 이미지 입력은 `tools/make_scene.py`에서 직접 생성했습니다.\n')
    (BASE/(stem+'.md')).write_text('\n'.join(lines),encoding='utf-8')
    report.append({**item,'executed_code_cells':code,'output_blocks':outputs,'figures':figures,'errors':errors})

index='''# 선형대수학 개념·코드·연습문제

- **구성**: 장별 실행 노트북 14개와 같은 이름의 Markdown 14개. 각 장에는 쉬운 개념 설명, LaTeX 수식, 원본 기반 코드, 실제 실행 결과, 문제별 풀이를 담았습니다.
- **출처 범위**: ZIP의 Python 14개를 원본으로 사용했습니다. 작업 폴더에 있던 기존 ipynb는 셀 경계와 연습문제 번호를 확인하는 데만 사용했습니다. 기존 결과를 복사하지 않고 새 프로세스에서 재실행했습니다.
- **학습 순서**: 벡터 → 행렬 → 역행렬·분해 → 최소제곱 → 고유분해·SVD → 응용.
- **문제 범위**: 제공 코드에서 식별된 연습문제 116개. 책의 문제 원문은 제공되지 않아 목표를 코드에서 재구성했습니다. 6장의 중복 ‘Exercise 5’는 뒤쪽을 6으로 표시했고, 7장에는 원자료에 없는 3번 문제를 임의로 만들지 않았습니다.
- 노트북 출력은 파일 안에 포함되어 있으므로 실행하지 않고 읽을 수 있습니다. Markdown 그림은 `assets`의 상대 경로를 사용합니다.

## 장별 파일

| 장 | 주제 | Markdown | 실행 노트북 | 연습문제 |
|---:|---|---|---|---:|
'''
for r in report:
    stem=r['stem']; index+=f"| {r['chapter']} | {r['title']} | [읽기](<{stem}.md>) | [ipynb](<{stem}.ipynb>) | {r['exercises']} |\n"
index+='''
## 블로그에 올리는 방법

1. 원하는 장의 `.md`와 해당 `assets/chXX` 폴더를 함께 옮깁니다. 2·4장 HTML과 6장 GIF도 해당 폴더에 있습니다.
2. 블로그가 이미지 업로드 후 새 URL을 반환하면 `![...](assets/...)` 경로를 그 URL로 바꿉니다. Markdown만 단독 복사하면 그림 경로가 끊길 수 있습니다.
3. 수식은 `$...$`와 `$$...$$`입니다. KaTeX 또는 MathJax를 지원하는 환경에서 렌더링합니다.
4. 노트북 링크·전체 목차·수정 내역 링크도 게시 위치에 맞게 조정합니다. 영어 변수명과 원본 주석은 코드 대조를 위해 보존했습니다.

## 다시 실행하기

- Python 3.12에서 검증했습니다. 패키지 버전은 `requirements-lock.txt`에 기록했습니다.
- 새 가상환경에 `python -m pip install -r requirements-lock.txt`로 설치합니다.
- **이 README가 있는 폴더를 작업 폴더로 설정**하고 노트북의 Python 커널에서 ‘모두 실행’을 선택합니다.
- `data`에 필요한 CSV·XLSX·PNG가 들어 있어 노트북 자체 실행에는 인터넷이 필요하지 않습니다.
- 모든 장을 일괄 실행하려면 `python tools/run_all.py`, 실행 결과로 Markdown을 다시 만들려면 `python tools/export.py`를 실행합니다.
- `python tools/make_scene.py`는 6·14장의 도형 입력 이미지를 재생성합니다.
- `tools/build.py`는 원본 ZIP과 작업 폴더의 기존 노트북이 있는 제작 환경용 변환 도구입니다. 배포받은 노트북 실행에는 필요하지 않습니다. 다시 변환하면 저장된 실행 출력이 초기화됩니다.
- 난수 시드는 `20260925 + 장 번호`입니다. BLAS·OS·라이브러리에 따라 마지막 자릿수·고유벡터 부호·측정 시간은 달라질 수 있습니다.

## 데이터와 이미지

| 파일 | 사용 장 | 출처·처리 |
|---|---|---|
| `data/communities.data` | 6 | 제공 코드의 UCI Communities and Crime 원자료. 비수치 열과 state/fold를 제외하는 원본 전처리 유지 |
| `data/SeoulBikeData.csv` | 11·12 | 제공 코드의 UCI Seoul Bike Sharing Demand 원자료. 계절은 봄·여름과 가을·겨울 두 집단으로 인코딩 |
| `data/data_akbilgic.xlsx` | 14 | 제공 코드의 UCI Istanbul Stock Exchange 원자료. 평균 중심화한 수익률로 PCA |
| `data/generated_scene.png` | 6·14 | 이 자료를 위해 Python/Pillow로 직접 생성한 320×240 컬러 도형. 외부 사진·작품을 사용하지 않음 |

- 원본 다운로드 URL은 `data/sources.json`, 데이터 파일 해시는 `data/checksums.json`에 있습니다.
- 코드에 이미 들어 있는 인구 배가시간 표는 과거의 고정 예제이며 현재 전망으로 갱신하지 않았습니다.
- 원본 이미지 입력을 도형으로 바꾼 부분은 각 장과 수정 내역에 표시했습니다. 알고리즘은 같은 구조지만 수치·시각적 결과는 원본 이미지와 다릅니다.
- 원본 저작자와 데이터 인용은 코드에 보존했습니다. 문서 설명과 실행 그림을 추가했다고 원본 코드의 저작권이 바뀌는 것은 아닙니다.

## 품질 확인 및 구성 파일

- [VALIDATION.md](VALIDATION.md): 셀 실행·파일 대응·이미지 링크·수학 검증 결과.
- [CHANGES.md](CHANGES.md): 원본 대비 수정과 보완 이유.
- `original_py/`: ZIP에서 복사한 원본 Python 14개. 변경하지 않았습니다.
- `manifest.json`: 장 이름, 원본 SHA-256, 셀 수·문제 수.
- `execution_logs/`: 실제 실행 로그와 장별 오류 집계.
- `tools/`: 한국어 원고, 변환·실행·Markdown 추출·검증 스크립트.
'''
(BASE/'README.md').write_text(index,encoding='utf-8')
changes=json.loads((BASE/'changes.json').read_text(encoding='utf-8'))
ch='# 원본 대비 수정 내역\n\n- 원본 파일은 `original_py/`에 보존했습니다. 아래 내용은 새 노트북에만 반영됩니다.\n- 공통: 난수 시드, 상대 경로, PNG 출력, 140 dpi 저장, 문제별 한국어 해설, 장말 assert 검증을 추가했습니다.\n- 기존 노트북과 Python에 서로 다른 값이 있을 때는 ZIP의 Python을 기준으로 했습니다.\n\n'
for n in range(1,15):
    ch+=f'## {n}장\n\n'
    for c in changes:
        if c['chapter']!=n:continue
        ns=[s for s in c['notes'] if not s.startswith(('Markdown 호환','블로그용 그림'))]
        if ns:ch+=f"- 원본 {c['lines'][0]}–{c['lines'][1]}행: "+' '.join(ns)+'\n'
    ch+='\n'
ch+='## 유지한 학습용 반례\n\n- 1장: 영벡터 정규화의 NaN, 잘못된 투영 분모.\n- 2·4·7장: 목록 인덱스·차원 불일치·특이/직사각 역행렬 오류는 해당 타입의 try/except로 출력.\n- 11장: 공선성에서의 직접 역행렬과 상관제곱 지표 한계.\n- 12장: 행을 고유벡터로 잘못 해석하는 그림과 스케일된 V에 전치를 역행렬처럼 사용하는 반례.\n- 14장: 고정된 잡음 후보 성분 [1,2] 제거는 대체 이미지의 검증 대상이며 자동 정답으로 해석하지 않음.\n'
(BASE/'CHANGES.md').write_text(ch,encoding='utf-8')
(BASE/'export_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Exported 14 Markdown chapters;',sum(r['figures'] for r in report),'figures')
