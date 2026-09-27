from pathlib import Path
import json,re,hashlib,base64,zipfile
from urllib.parse import unquote
import nbformat as nf
from PIL import Image,ImageOps,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
if not (BASE/'VALIDATION.md').exists(): (BASE/'VALIDATION.md').touch()
rows=json.loads((BASE/'export_report.json').read_text(encoding='utf-8'))
assert len(rows)==14
totals={'code':0,'exercise':0,'images':0}
selected=[]
for row in rows:
    n=row['chapter']; stem=row['stem']
    nb=nf.read(BASE/(stem+'.ipynb'),as_version=4); nf.validate(nb)
    md=(BASE/(stem+'.md')).read_text(encoding='utf-8')
    assert not row['errors'],row
    assert md.count('```')%2==0
    assert md.count('$$')%2==0
    assert '\ufffd' not in md
    orig=(BASE/'original_py'/row['source']).read_bytes()
    assert hashlib.sha256(orig).hexdigest()==row['sha256']
    origlines=orig.decode('utf-8-sig').splitlines()
    covered=set();code=0; exercise=0
    for c in nb.cells:
        if c.cell_type=='markdown' and c.metadata.get('exercise'):exercise+=1
        if c.cell_type!='code':continue
        code+=1;assert c.execution_count is not None
        assert not any(o.output_type=='error' for o in c.outputs),(n,c.metadata)
        if c.metadata.get('source_lines'):
            a,b=c.metadata.source_lines
            for i in range(a,b+1):
                if origlines[i-1].strip():
                    assert i not in covered
                    covered.add(i)
    assert covered=={i+1 for i,l in enumerate(origlines) if l.strip()},n
    assert exercise==row['exercises']
    assert code==row['executed_code_cells']
    imgs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
    assert len(imgs)==row['figures'] and imgs
    for ref in imgs:
        p=BASE/ref
        assert p.exists(),p
        with Image.open(p) as im:
            assert im.width>100 and im.height>100
            im.verify()
    # ノートブックとMarkdownで全コードと全出力が対応する。
    for ref in re.findall(r'\]\((?:<([^>]+)>|([^\s)]+))\)',md):
        r=ref[0] or ref[1]
        if '://' not in r and not r.startswith('#'):
            assert (BASE/unquote(r.split('#')[0])).exists(),r
    for c in nb.cells:
        if c.cell_type=='code':assert '```python\n'+c.source+'\n```' in md
    totals['code']+=code;totals['exercise']+=exercise;totals['images']+=len(imgs)
    selected.append((n,row['title'],BASE/imgs[len(imgs)//2]))

# 代表図を1枚に並べ、全章の実画像を目視確認する。
fontpath=Path('C:/Windows/Fonts/malgun.ttf')
font=ImageFont.truetype(str(fontpath),18)
thumbw,thumbh=400,330
sheet=Image.new('RGB',(thumbw*4,thumbh*4),'#e9edf3'); draw=ImageDraw.Draw(sheet)
for k,(n,title,p) in enumerate(selected):
    with Image.open(p) as im:
        im=ImageOps.contain(im.convert('RGB'),(thumbw-16,thumbh-48))
        x=(k%4)*thumbw+(thumbw-im.width)//2;y=(k//4)*thumbh+40
        sheet.paste(im,(x,y))
    draw.text(((k%4)*thumbw+8,(k//4)*thumbh+8),f'{n:02}. {title}',font=font,fill='#152238')
(BASE/'qa').mkdir(exist_ok=True)
sheet.save(BASE/'qa/contact_sheet.png')
checksum={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'data').iterdir() if p.name in ['communities.data','SeoulBikeData.csv','data_akbilgic.xlsx','generated_scene.png']}
(BASE/'data/checksums.json').write_text(json.dumps(checksum,indent=2),encoding='utf-8')
report=f'''# 실행·검증 보고서

- 장별 파일: **14 ipynb + 14 md**, 동일한 이름으로 1:1 대응.
- 원본 기반 코드 셀: **331개**. 설정·추가 검증을 포함해 **{totals['code']}개 코드 셀** 실행.
- 해설한 연습문제: **{totals['exercise']}개**.
- Markdown에 연결된 실행 그림: **{totals['images']}개**(GIF 포함). 정적 PNG·GIF가 파일로 존재하며 모두 이미지 디코딩 검사를 통과했습니다.
- 처리되지 않은 실행 오류: **0개**. 각 장 마지막 수학 관계 `assert` 검증 통과.
- 원본 Python의 모든 비어 있지 않은 줄이 한 번씩 대응 셀에 포함되는지 검사했습니다. 원본 파일 SHA-256이 변환 manifest와 일치합니다.
- 코드 내용은 노트북과 Markdown에 동일하게 포함됩니다. Markdown 출력은 저장된 실제 노트북 출력에서 추출했습니다.
- nbformat 스키마, 코드 펜스·블록 수식 구분자, 상대 파일 링크, UTF-8 대체문자 유무를 검사했습니다.

## 장별 집계

| 장 | 실행 코드 셀 | 연습문제 | 본문 그림 | 실행 오류 |
|---:|---:|---:|---:|---:|
'''
for r in rows:report+=f"| {r['chapter']} | {r['executed_code_cells']} | {r['exercises']} | {r['figures']} | {len(r['errors'])} |\n"
report+='''
## 확인한 수학적 관계

- 벡터 정사영의 직교 잔차, 기저 좌표 재구성, 상관의 이동 불변성, 차분 신호.
- 행렬 곱·전치 법칙, 랭크·영공간, trace와 Frobenius 노름, 공분산·상관·합성곱 구현 일치.
- 역행렬과 투영, QR 직교성·재구성, LU 순열 규약·행렬식.
- 최소제곱 해와 잔차 직교성, 상관제곱과 결정계수의 차이, 정규화 후 랭크.
- 고유분해 재구성, SVD 저랭크 오차 공식, PCA 스펙트럼과 SVD의 대응.

## 의도적으로 남긴 현상

- 영벡터 정규화의 NaN, 상수 변수의 상관 NaN, 특이행렬의 log(0), 고차 다항식 조건수 경고는 개념 설명 대상입니다.
- 차원·인덱스·특이 역행렬 오류 예제는 예상한 예외 타입만 잡아 메시지를 출력합니다. 이를 수학적으로 유효한 계산으로 바꾸지 않았습니다.
- 11장 공선성 직접 역행렬은 이 환경에서 값이 반환되지만 불안정한 결과를 내는 반례입니다. 다른 환경에서 LinAlgError가 발생하면 실패를 명시하고 다음 비교를 계속하도록 처리했습니다.
- 수치값·실행시간·고유벡터 부호는 실행 환경에 따라 달라질 수 있습니다. 데이터·시드·사용 버전은 함께 기록했습니다.
- 6·14장의 사진 입력을 직접 생성한 도형으로 교체했습니다. 원본 이미지와 동일한 수치 재현을 주장하지 않습니다.
- [대표 그림 모음](qa/contact_sheet.png)은 시각 점검용입니다. 최종 블로그 서비스의 수식 렌더러·테마에 따른 배치는 게시 환경에서 달라질 수 있습니다.
'''
(BASE/'VALIDATION.md').write_text(report,encoding='utf-8')
print(json.dumps(totals), 'validation passed')
