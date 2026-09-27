"""실행 결과를 유지하며 번호형 절·간결한 표·코드/결과 인접 배치로 MD만 재편집."""
from pathlib import Path
import ast,io,json,re,sys,tokenize,hashlib,zipfile,warnings
import nbformat
warnings.filterwarnings('ignore',category=SyntaxWarning)

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'tools'))
from lessons import LESSONS,EXERCISES

TABLES={
1:[('표현','의미','NumPy'),('1차원 배열','방향이 지정되지 않은 성분 목록','`np.array([1, 2, 3])`'),('행벡터','한 행에 성분을 배치','`np.array([[1, 2, 3]])`'),('열벡터','한 열에 성분을 배치','`np.array([[1], [2], [3]])`'),('내적','두 벡터의 방향 관계를 스칼라로 계산','`v @ w`')],
2:[('개념','핵심 질문','확인 방법'),('선형결합','어떤 가중치로 벡터를 합치는가?','`V @ weights`'),('생성공간','가중치를 바꿔 어디까지 만들 수 있는가?','선형결합의 점들을 시각화'),('선형독립','중복되는 방향이 있는가?','`np.linalg.matrix_rank(V)`'),('기저 좌표','이 기저에서 몇 배씩 써야 하는가?','`np.linalg.solve(B, p)`')],
3:[('연산','비교하는 것','해석'),('코사인 유사도','원점 기준 방향','벡터의 절대 기준점에 영향받음'),('상관계수','평균 제거 후 방향','함께 오르내리는 패턴을 비교'),('이동 내적','작은 창과 커널','평활화·변화점 검출'),('k-means','점과 중심의 제곱거리','가까운 중심에 배정하고 평균으로 갱신')],
4:[('연산','수학 표기','Python'),('원소별 곱',r'$A\odot B$','`A * B`'),('행렬 곱','$AB$','`A @ B`'),('전치',r'$A^T$','`A.T`'),('대각 이동',r'$A+\lambda I$','`A + lam * np.eye(n)`')],
5:[('개념','의미','확인 방법'),('열공간','행렬이 출력할 수 있는 방향','열들의 선형결합'),('영공간','출력에서 사라지는 입력 방향','`scipy.linalg.null_space(A)`'),('랭크','독립적인 방향 수','`np.linalg.matrix_rank(A)`'),('프로베니우스 노름','전체 원소를 펼친 벡터의 길이',"`np.linalg.norm(A, 'fro')`")],
6:[('행렬','행·열의 의미','핵심 연산'),('데이터 행렬','관측치 × 변수','열별 평균 제거'),('공분산 행렬','변수 × 변수','`Xc.T @ Xc / (N - 1)`'),('좌표 행렬','좌표 성분 × 점','`T @ points`'),('이미지 행렬','세로 픽셀 × 가로 픽셀','`convolve2d(image, kernel)`')],
7:[('종류','성립 조건','확인할 곱'),('일반 역행렬','정사각 완전랭크',r'$A^{-1}A=AA^{-1}=I$'),('왼쪽 역행렬','완전열랭크',r'$LA=I$'),('오른쪽 역행렬','완전행랭크',r'$AR=I$'),('의사역행렬','모든 행렬에 정의',r'$AA^+A=A$')],
8:[('대상','역할','확인할 관계'),('Q','서로 직교하는 단위 방향',r'$Q^TQ=I$'),('R','원래 열을 표현하는 가중치','상삼각 구조'),('QR','원래 행렬 재구성','$A=QR$'),('최소제곱','직교 좌표에서 계수 계산',r'$R\hat\beta=Q^Ty$')],
9:[('대상','의미','핵심 확인'),('RREF','행 연산으로 단순화한 방정식','피벗·자유변수'),('P','행 교환 기록',r'$P^TP=I$'),('L','전진 소거의 가중치','대각선이 1인 하삼각행렬'),('U','소거 후 상삼각 형태','SciPy 규약은 $A=PLU$')],
10:[('기호','의미','코드 표현'),('$X$','설명변수를 모은 설계행렬','`np.column_stack([ones, x])`'),(r'$\hat\beta$','적합한 계수','`np.linalg.lstsq(X, y, rcond=None)[0]`'),(r'$\hat y$','모델 예측값','`X @ beta`'),('$e$','설명하지 못한 잔차','`y - X @ beta`')],
11:[('상황','생기는 문제','대응'),('중복 설명변수','계수가 유일하지 않거나 불안정','랭크 확인·SVD 기반 최소제곱'),('큰 계수와 민감도','작은 변화가 해에 큰 영향','릿지 정규화'),('높은 다항식 차수','과적합·나쁜 조건수','중심화·스케일링·검증'),('상관제곱만 비교','큰 오프셋 오차를 놓칠 수 있음',r'$1-\mathrm{SSE}/\mathrm{SST}$와 구분')],
12:[('대상','의미','관계'),('고유벡터','변환 후에도 같은 직선 위에 남는 방향',r'$Av=\lambda v$'),('고윳값','해당 방향의 배율',r'$\det(A-\lambda I)=0$'),('대각화','고유기저로 좌표 변경',r'$A=V\Lambda V^{-1}$'),('대칭행렬','직교정규 고유기저를 선택 가능',r'$A=Q\Lambda Q^T$')],
13:[('대상','의미','NumPy 반환값'),('왼쪽 특이벡터','출력 방향','`U`의 열'),('특잇값','각 방향의 배율','`s`'),('오른쪽 특이벡터','입력 방향','`Vt`의 행'),('저랭크 근사','큰 특잇값 성분만 사용','`(U[:, :k] * s[:k]) @ Vt[:k]`')],
14:[('방법','찾는 것','판단 기준'),('PCA','전체 분산이 큰 방향','설명분산 비율'),('LDA','집단이 잘 분리되는 방향','집단 간·내 퍼짐의 비율'),('SVD 압축','적은 성분으로 표현한 이미지','복원 오차·인자 저장량'),('성분 제거','잡음 후보를 제외한 이미지','잡음 감소와 신호 손실을 함께 확인')]
}

def table(rows):
    return '\n'.join(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(row)+' |' for row in rows[1:]])

def clean_code(src):
    """보통의 영어 설명 주석만 줄이고, 실행문·대체 실험용 코드·한국어 주석은 보존."""
    lines=src.splitlines()
    try: tokens=list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError:return src
    for tok in reversed(tokens):
        if tok.type!=tokenize.COMMENT:continue
        comment=tok.string
        if re.search('[가-힣]',comment):continue
        if re.match(r'#\s*(?:[A-Za-z_]\w*\s*=|(?:print|plt|np)\.)',comment):continue
        r,c=tok.start
        lines[r-1]=lines[r-1][:c].rstrip()
    result=re.sub(r'\n\s*\n(?:\s*\n)+','\n\n','\n'.join(lines)).strip()
    assert ast.dump(ast.parse(src))==ast.dump(ast.parse(result)), 'Code semantics changed'
    return result

def outputs(c,n,seq):
    parts=[]
    for j,o in enumerate(c.outputs):
        if o.output_type=='stream':
            txt=re.sub(r'(?m)^Out\[\d+\]:\s*','',o.text).strip()
            # Python 문자열 표기 경고·내부 셀 경로는 수치 결과와 무관한 제작 로그다.
            # 영벡터/상관/수치조건 관련 RuntimeWarning·RankWarning은 유지한다.
            if o.get('name')=='stderr':
                kept=[]; skip_source=False
                for line in txt.splitlines():
                    if 'SyntaxWarning:' in line:
                        skip_source=True;continue
                    if skip_source and line.startswith('  '):
                        skip_source=False;continue
                    skip_source=False;kept.append(line)
                txt='\n'.join(kept).strip()
            txt=re.sub(r'\n{3,}','\n\n',txt)
            if txt:parts.append('```text\n'+txt+'\n```')
        data=o.get('data',{}); found=False
        for mime,ext in [('image/png','png'),('image/gif','gif'),('image/svg+xml','svg')]:
            if mime in data:
                ref=f'assets/ch{n:02}/output_{seq:03}_{j:02}.{ext}'
                assert (BASE/ref).is_file(),ref
                parts.append(f'![셀 실행 결과]({ref})');found=True;break
        if not found and 'text/plain' in data:
            txt=data['text/plain'];txt=''.join(txt) if isinstance(txt,list) else txt
            if txt.strip():parts.append('```text\n'+txt.strip()+'\n```')
        assert o.output_type!='error'
    return parts

def render_group(cells,n):
    """출력이 없는 준비 셀은 다음 계산 셀과 묶어 불필요한 블록 구분을 줄인다."""
    parts=[]; pending=[]
    for seq,c in cells:
        src=clean_code(c.source)
        if src:pending.append(src)
        rendered=outputs(c,n,seq)
        if rendered:
            if pending:parts.append('```python\n'+'\n\n'.join(pending)+'\n```');pending=[]
            parts+=rendered
    if pending:parts.append('```python\n'+'\n\n'.join(pending)+'\n```')
    return '\n\n'.join(parts)

def numbered_lessons(n):
    src=LESSONS[n].strip()
    chunks=re.split(r'(?m)^## ',src)[1:]
    rendered=[]
    for i,chunk in enumerate(chunks,1):
        title,body=chunk.split('\n',1)
        body=re.sub(r'(?m)^- \*\*배울 것\*\*: .*\n','',body).strip()
        rendered.append(f'## {n}.{i} {title}\n\n'+body)
        if i==1:rendered.append(table(TABLES[n]))
    return rendered,len(chunks)

manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
snapshot={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob('*.ipynb')}
report=[]
for item in manifest:
    n=item['chapter']; stem=item['stem']; nb=nbformat.read(BASE/(stem+'.ipynb'),as_version=4)
    sections,k=numbered_lessons(n)
    parts=[f'# {n}. {item["title"]}']+sections
    parts.append(f'## {n}.{k+1} 파이썬으로 확인하기')
    parts.append('- 코드는 위에서부터 순서대로 실행한다. 앞에서 만든 변수와 함수를 다음 예제에서도 사용한다.\n- 아래 숫자와 그림은 고정된 난수 시드로 실행한 결과다. 환경에 따라 마지막 소수 자릿수와 실행 시간은 달라질 수 있다.')
    groups=[{'title':'준비','cells':[]}]; exgroups=[]; current=groups[0]; verification=[]; seq=0
    for c in nb.cells[1:]:
        if c.cell_type=='markdown':
            if c.metadata.get('exercise'):
                e=c.metadata['exercise']; current={'exercise':e,'cells':[]};exgroups.append(current)
            elif c.source.startswith('### ') and not c.source.startswith('### 코드'):
                current={'title':c.source.splitlines()[0][4:],'cells':[]};groups.append(current)
            continue
        seq+=1
        if c.metadata.get('role')=='verification':verification.append((seq,c));continue
        # 준비 절에는 설정과 import 셀만 포함하고, 제목 없는 본문은 별도 실습으로 표시한다.
        code=clean_code(c.source)
        if current is groups[0] and c.metadata.get('original_cell') not in [None,1,2] and code:
            current={'title':'기본 연산 살펴보기','cells':[]};groups.append(current)
        if current is groups[0] and c.metadata.get('original_cell')==2 and n==3:
            current={'title':'상관관계를 산점도로 확인하기','cells':[]};groups.append(current)
        current['cells'].append((seq,c))
    step=0
    for g in groups:
        if g['title']=='준비':
            sources=[clean_code(c.source) for _,c in g['cells']]
            ready='\n\n'.join(s for s in sources if s)
            content='```python\n'+ready+'\n```\n\n'+'\n\n'.join(p for seq,c in g['cells'] for p in outputs(c,n,seq))
        else:content=render_group(g['cells'],n)
        if not content:continue
        step+=1
        parts.append(f'### {step}. {g["title"]}')
        parts.append(content)
    parts.append(f'## {n}.{k+2} 연습문제')
    for g in exgroups:
        e=g['exercise'];title,goal,method,result=EXERCISES[n][e]
        parts.append(f'### 연습문제 {e}. {title}')
        sentences=re.split(r'(?<=[다요])\.\s+',method)
        bullets=['- '+goal]+['- '+s.rstrip('.')+'.' for s in sentences if s]
        parts.append('\n'.join(bullets))
        content=render_group(g['cells'],n)
        if content:parts.append(content)
        parts.append('- **결과 해석**: '+result)
    parts.append(f'## {n}.{k+3} 핵심 관계 확인')
    parts.append('- 작은 입력으로 핵심 공식을 다시 확인한다. `assert`가 통과하면 지정한 허용오차 안에서 관계가 성립한다.')
    parts.append(render_group(verification,n))
    # 제작 정보는 읽는 흐름을 가로막지 않도록 끝에 짧게 배치한다.
    parts.append('## 실습에서 확인할 점')
    notes=[('항목','확인할 점'),('작은 잔차','`1e-14` 수준의 값은 부동소수점 오차일 수 있음'),('셀 실행 순서','앞에서 준비한 변수·데이터를 다음 코드에서 사용'),('문제 범위','제공된 코드의 학습 목표를 재구성한 풀이이며 책의 문제 원문은 아님')]
    if n in [2,4,7]:notes.append(('예상 오류','차원·인덱스·역행렬 조건을 어기는 예제는 오류 메시지로 원인을 확인'))
    if n in [6,14]:notes.append(('이미지 입력','직접 생성한 도형 이미지 사용. 원본 사진과 수치·시각적 결과가 다름'))
    if n==7:notes.append(('문제 번호','제공 자료에 없는 3번 문제를 새로 만들어 넣지 않음'))
    if n==6:notes.append(('문제 번호','중복된 Exercise 5 중 뒤쪽을 6번으로 정리'))
    parts.append(table(notes))
    if n in [2,4]:parts.append(f'- [3차원 생성공간 살펴보기](assets/ch{n:02}/interactive_3d.html): 브라우저에서 회전·확대 가능')
    parts.append('## 참고 자료')
    parts.append(f'- 제공된 `선형대수학.zip`의 `{item["source"]}`\n- Mike X Cohen, *Practical Linear Algebra for Data Science* / 한국어판 *개발자를 위한 실전 선형대수학*\n- 한국어 개념 설명과 연습문제 해설은 선형대수학 코드에 맞춰 작성했다. 코드 보완 내역은 기존 자료의 `CHANGES.md`에서 확인할 수 있다.')
    md='\n\n'.join(p.strip() for p in parts if p.strip())+'\n'
    assert md.count('```')%2==0 and md.count('$$')%2==0
    assert len(re.findall(r'^### 연습문제 ',md,re.M))==item['exercises']
    old=(BASE/(stem+'.md')).read_text(encoding='utf-8')
    old_images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',old)
    new_images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
    assert old_images==new_images,(n,'Image ordering/count changed')
    # 모든 실행문을 순서대로 보존했는지 검사한다.
    fences=re.findall(r'```python\n(.*?)\n```',md,re.S)
    expected=[]; actual=[]
    for c in nb.cells:
        if c.cell_type=='code':expected.extend(ast.dump(node) for node in ast.parse(c.source).body)
    for code in fences:actual.extend(ast.dump(node) for node in ast.parse(code).body)
    assert expected==actual,(n,'Executable statements changed')
    assert '\ufffd' not in md
    (BASE/(stem+'.md')).write_text(md,encoding='utf-8')
    report.append({'chapter':n,'exercises':item['exercises'],'images':len(new_images),'before_bytes':len(old.encode()),'after_bytes':len(md.encode()),'code_blocks':len(fences)})

assert all(hashlib.sha256((BASE/name).read_bytes()).hexdigest()==h for name,h in snapshot.items())
target=BASE.parent/'선형대수학_디자인개정_MD만.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for item in manifest:
        name=item['stem']+'.md';z.write(BASE/name,name)
with zipfile.ZipFile(target) as z:
    assert len(z.namelist())==14 and all(p.endswith('.md') for p in z.namelist())
    assert z.testzip() is None
(BASE/'tools/redesign_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True));print('MD-only ZIP:',target)
