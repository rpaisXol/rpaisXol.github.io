"""ZIP의 Python을 장별 실행 노트북으로 변환한다. 기존 ipynb는 셀 경계/문제 번호만 제공한다."""
from pathlib import Path
import json, zipfile, re, hashlib, textwrap, sys
import nbformat as nf

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
sys.path.insert(0,str(BASE/'tools'))
from lessons import LESSONS, EXERCISES
TITLES=['벡터와 벡터의 기본 연산','벡터의 확장 개념','데이터 분석에서의 벡터','행렬과 행렬의 기본 연산','행렬의 확장 개념','데이터 분석에서의 행렬','역행렬','직교 행렬과 QR 분해','행 축소와 LU 분해','일반 선형 모델 및 최소제곱법','최소제곱법 응용','고윳값 분해','특잇값 분해','고윳값 분해와 SVD 응용']
changes=[]

def patch(n,i,s):
    notes=[]
    def rep(a,b,why='입력 이미지와 일치하도록 표시 문구를 수정했습니다.'):
        nonlocal s
        if a in s:
            s=s.replace(a,b); notes.append(why)
    rep("set_matplotlib_formats('svg')","set_matplotlib_formats('png')",'Markdown 호환을 위해 그림 출력을 PNG로 지정했습니다.')
    # 파일은 장별 assets 폴더에만 저장한다.
    s=re.sub(r"plt.savefig\('([^']+)'",r"plt.savefig(ASSET / '\1'",s)
    rep('dpi=300','dpi=140','블로그용 그림 해상도를 140 dpi로 설정했습니다.')
    for line in s.splitlines():
        if line.strip().startswith('??'):
            obj=line.strip()[2:].removesuffix('()')
            rep(line,f'import inspect\nprint(inspect.signature({obj}))\nprint(inspect.getdoc({obj}).split("\\n\\n")[0])','IPython 소스 보기 명령을 함수 시그니처와 설명 출력으로 변환했습니다. 전체 소스는 inspect.getsource로 확인할 수 있습니다.')
    if 'fig.show()' in s:
        rep('fig.show()',"fig.write_html(str(ASSET / 'interactive_3d.html'), include_plotlyjs=True)\nax = plt.figure(figsize=(7, 6)).add_subplot(projection='3d')\nax.scatter(points[:,0], points[:,1], points[:,2], s=15)\nax.set(xlabel='x', ylabel='y', zlabel='z', title='Span: linear combinations')\nplt.show()",'Plotly 3차원 그림은 HTML로 보존하고, Markdown용 정적 3차원 산점도를 추가했습니다.')
    if n==4: rep("raise('Matrices must be the same size!')","raise ValueError('Matrices must be the same size!')",'문자열 raise를 ValueError로 수정했습니다.')
    if n==5:
        rep('{numIters-1}','{numIters}','반복문 종료 시 이미 거리 조건을 만족하므로 마지막 반복을 취소하던 출력 오류를 수정했습니다.')
        rep('{s/.9:.3f}','{s:.3f}','최종 스케일을 그대로 출력합니다.')
        rep('EuclideanDistance(s/.9*A,s/.9*B)','EuclideanDistance(s*A,s*B)','종료 조건을 만족한 최종 거리를 출력합니다.')
        rep('nIters[i] = numIters-1','nIters[i] = numIters','반복 횟수 집계의 1 차이를 수정했습니다.')
    if n==6:
        rep("pd.read_csv(url,sep=',',header=None)","pd.read_csv(DATA / 'communities.data',sep=',',header=None)",'UCI 원자료의 로컬 사본을 사용합니다. 결측 표식 ?가 있는 열은 원본 방식대로 숫자형 열 선택에서 제외됩니다.')
        rep('data.columns[i], data.columns[j]',"numberDataset.drop(['state','fold'],axis=1).columns[i], numberDataset.drop(['state','fold'],axis=1).columns[j]",'상관계수에 대응하는 열 이름을 전처리 후 열 목록에서 가져오도록 수정했습니다.')
        rep("io.imread('https://upload.wikimedia.org/wikipedia/commons/6/61/De_nieuwe_vleugel_van_het_Stedelijk_Museum_Amsterdam.jpg')","io.imread(DATA / 'generated_scene.png')",'이미지 입력을 코드로 직접 생성한 도형 그림으로 교체했습니다. 변수명 bathtub은 원본 연결을 위해 유지하며 박물관 사진의 결과가 아닙니다.')
        if 'animation.FuncAnimation' in s:
            s=re.sub(r'(?m)^animation.FuncAnimation\((.*)\)$',r"anim = animation.FuncAnimation(\1)\nanim.save(str(ASSET / 'animation_"+str(i)+r".gif'), writer='pillow', fps=10)\nfrom IPython.display import Image, display\ndisplay(Image(filename=str(ASSET / 'animation_"+str(i)+r".gif')))\nplt.close(fig)",s)
            notes.append('변환 애니메이션을 GIF로 저장해 Markdown에서도 볼 수 있게 했습니다.')
    if n==7 and 'W = np.random' in s:
        rep('np.linalg.matrix_rank(T)','np.linalg.matrix_rank(W)','오른쪽 역행렬 예제의 rank 출력 대상 T를 W로 수정했습니다.')
    if n==9:
        rep('spla.lu','scipy.linalg.lu','정의되지 않은 spla 이름을 scipy.linalg로 수정했습니다.')
        rep("axs[2].imshow(P.T,","axs[2].imshow(P,",'SciPy의 A=PLU 규약에 맞춰 순열행렬 그림을 P로 수정했습니다.')
        rep("axs[2].set_title(r'P$^T$')","axs[2].set_title('P')",'순열행렬 그림의 표기를 수정했습니다.')
    if n==10 and 'happiness_oops1' in s:
        rep('for n,y,yHat in zip(numcourses,y,pred_happiness):','for n,y_obs,yHat in zip(numcourses,y,pred_happiness):','잔차 표시 루프가 전체 y 벡터를 덮어쓰지 않게 수정했습니다.')
        rep("axi.plot([n,n],[y,yHat]","axi.plot([n,n],[y_obs,yHat]",'관측값 변수명을 분리했습니다.')
        rep('ylim=[0,100]','ylim=[0,185]','170인 이상치도 그림에 보이도록 y축 범위를 확대했습니다.')
    if n==11:
        if i==37:
            s='try:\n'+textwrap.indent(s,'    ')+'''\nexcept np.linalg.LinAlgError as exc:
    print('학습용 예상 오류: 공선성 행렬의 직접 역행렬', exc)
    beta1 = np.full((desmatM.shape[1], 1), np.nan)
    modelfit1 = np.nan
'''
            notes.append('공선성 직접 역행렬이 환경에 따라 예외를 내면 실패를 명시하고, 다음 lstsq·statsmodels 비교를 계속합니다.')
        rep("pd.read_csv(url,sep=',',encoding='unicode_escape')","pd.read_csv(DATA / 'SeoulBikeData.csv',sep=',',encoding='unicode_escape')",'서울 자전거 원자료의 로컬 사본을 사용합니다.')
        rep('data.corr()','data.corr(numeric_only=True)','문자열 열이 있는 DataFrame의 최신 pandas 호환성을 보완했습니다.')
        rep("data.replace(['Spring','Summer', 'Autumn','Winter'],[1,1,0,0], inplace=True)","data['Seasons'] = data['Seasons'].map({'Spring':1, 'Summer':1, 'Autumn':0, 'Winter':0}).astype(float)",'계절 열만 명시적으로 숫자 인코딩합니다.')
        rep('np.array(year)**i','np.array(year,dtype=float)**i','연도 거듭제곱에서 정수 오버플로를 방지합니다.')
        rep('np.argmax(r2)','np.nanargmax(r2)','상수 예측의 상관계수 NaN을 최댓값 탐색에서 제외합니다. 상관제곱의 한계 자체는 유지합니다.')
        if 'for i in range(len(gs))' in s:
            rep('np.linalg.inv(desmatM.T@desmatM + l*np.eye(desmatM.shape[1]))','np.linalg.pinv(desmatM.T@desmatM + l*np.eye(desmatM.shape[1]))','정규화 0에서 특이행렬이 되는 경우도 비교하도록 의사역행렬을 사용합니다.')
    if n==12:
        rep('evecs[[i],:]','evecs[:,i].reshape(1,-1)','고유벡터는 열에 저장되므로 영공간 비교 인덱스를 수정했습니다.')
        rep('null_space( A-evals[i]*np.eye(N) )','null_space( A-evals[i]*np.eye(N), rcond=1e-10 )','고윳값의 부동소수점 오차를 고려하여 영공간 허용오차를 명시했습니다.')
        rep('V[:,1]*np.conj(V[:,1])','V[:,i]*np.conj(V[:,i])','각 고유벡터의 노름을 출력하도록 루프 인덱스를 수정했습니다.')
        if 'swap only the two largest' in s or 'swap only the two smallest' in s:
            a='i = evals_sort_idx[np.r_[np.arange(N-2),N-1,N-2]][::-1]'
            rep(a,'i = np.arange(N)\na,b = evals_sort_idx[-2:]\ni[a],i[b] = i[b],i[a]','정렬 순서를 전체에 적용하지 않고 실제 두 고윳값의 위치만 교환합니다.')
            a='i = evals_sort_idx[np.r_[1,0,np.arange(2,N)]][::-1]'
            rep(a,'i = np.arange(N)\na,b = evals_sort_idx[:2]\ni[a],i[b] = i[b],i[a]','가장 작은 두 고윳값만 교환하도록 수정했습니다.')
    if n==13:
        rep('np.linalg.eig(A)','np.linalg.eigh(A)','실수 대칭행렬의 고유분해에는 전용 eigh를 사용합니다.')
        rep('100*s/np.sum(s)','100*s**2/np.sum(s**2)','SVD의 에너지 비율은 특잇값의 제곱으로 계산합니다.')
        rep("plt.ylabel('Variance explained (%)')","plt.ylabel('Squared singular-value energy (%)')",'중심화하지 않은 행렬이므로 분산 대신 제곱 에너지 비율로 표기했습니다.')
    if n==14:
        rep('np.linalg.eig(covmat)','np.linalg.eigh(covmat)','대칭 공분산 행렬에 eigh를 사용해 실수 고윳값과 직교기저를 구합니다.')
        rep('pd.read_excel(url,index_col=0,skiprows=1)',"pd.read_excel(DATA / 'data_akbilgic.xlsx',index_col=0,skiprows=1)",'이스탄불 주가 수익률 원자료의 로컬 사본을 사용합니다.')
        rep('components = data.values @ evecs[:,0:2]','components = X @ evecs[:,0:2]','PCA 점수를 중심화한 데이터로 계산합니다.')
        rep("[0,Vt[0,0]],[0,Vt[1,0]]","[0,Vt[0,0]],[0,Vt[0,1]]",'Vt의 행이 주성분 방향이므로 그림 좌표를 수정했습니다.')
        rep("[0,Vt[0,1]],[0,Vt[1,1]]","[0,Vt[1,0]],[0,Vt[1,1]]",'두 번째 주성분 방향의 좌표를 수정했습니다.')
        rep('predictedLabel = ( projA[:,0] > 0 )+0',"score = projA[:,0]\nmid = (score[labels==0].mean()+score[labels==1].mean())/2\npositive_is_one = score[labels==1].mean() > score[labels==0].mean()\npredictedLabel = ((score > mid) if positive_is_one else (score < mid)).astype(int)",'고유벡터 부호에 따라 클래스가 뒤집히지 않도록 학습 클래스 평균으로 방향과 경계를 정합니다.')
        rep('strav = io.imread(url)',"strav = io.imread(DATA / 'generated_scene.png')",'접속 불가인 원본 Picasso 이미지 대신 직접 생성한 도형 이미지를 사용합니다. 뒤의 압축·잡음 제거 수치는 이 대체 이미지 결과입니다.')
        rep('Stravinsky picture','generated scene')
        rep('noisy Stravinsky picture','noisy generated scene')
        rep('Noisy Stravinsky picture','Noisy generated scene')
        # 동일 분할로 shrinkage를 공정하게 비교
        if 'shrinkage = np.linspace' in s:
            rep('for i,s in enumerate(shrinkage):','splits = [np.random.permutation(alldata.shape[0]) for _ in range(50)]\nfor i,s in enumerate(shrinkage):','모든 shrinkage 값에 같은 학습/검증 분할을 적용합니다.')
            rep('for _ in range(50):','for split_i in range(50):','분할 인덱스를 사용합니다.')
            rep('randorder = np.random.permutation(alldata.shape[0])','randorder = splits[split_i]','검증 표본 변동과 shrinkage 효과를 분리합니다.')
    # 명시적인 오류 예제만 잡아 후속 셀 실행을 보장한다.
    expected={(2,14):'IndexError',(4,36):'ValueError',(4,39):'ValueError',(7,9):'np.linalg.LinAlgError',(7,45):'np.linalg.LinAlgError'}
    if (n,i) in expected:
        s='try:\n'+textwrap.indent(s,'    ')+f'\nexcept {expected[n,i]} as exc:\n    print("학습용 예상 오류:", type(exc).__name__, str(exc))'
        notes.append('의도된 오류를 해당 예외 타입으로 처리하고 오류 메시지를 출력합니다.')
    return s, list(dict.fromkeys(notes))

EXTRA={
 (1,55):'''# 추가 검증: 합은 맞아도 직교가 깨질 수 있다.
t_perp_wrong = t - t_para
t_para_correct = r * (t @ r) / (r @ r)
print('잘못된 분모의 직교 잔차:', r @ t_perp_wrong)
print('올바른 분모의 직교 잔차:', r @ (t-t_para_correct))
assert np.allclose(r @ (t-t_para_correct), 0)
''',
 (12,58):'''# 추가 구현: 원본의 11장 연습 4 참조를 이 장에서 독립 실행
import pandas as pd
_bike = pd.read_csv(DATA / 'SeoulBikeData.csv', encoding='unicode_escape')
_X = np.column_stack([_bike['Rainfall(mm)'], _bike['Temperature(°C)'], np.ones(len(_bike))])
_Xm = np.column_stack([_X, 4*_X[:,0] + .4*_X[:,1]])
_y = _bike['Rented Bike Count'].to_numpy()
_gs = np.linspace(0,.2,40)
for _mat, _label in [(_X,'Original'), (_Xm,'Collinear')]:
    _scale = np.linalg.eigvalsh(_mat.T@_mat).mean()
    print(_label, '평균 고윳값:', _scale, 'Frobenius² / p:', np.linalg.norm(_mat,'fro')**2/_mat.shape[1])
    assert np.allclose(_scale,np.linalg.norm(_mat,'fro')**2/_mat.shape[1])
    _fits=[]
    for _g in _gs:
        _b = np.linalg.pinv(_mat.T@_mat+_g*_scale*np.eye(_mat.shape[1]))@_mat.T@_y
        _fits.append(1-np.sum((_y-_mat@_b)**2)/np.sum((_y-_y.mean())**2))
    plt.plot(_gs,_fits,label=_label)
plt.xlabel('Gamma'); plt.ylabel('R-squared: 1 - SSE/SST')
plt.legend(); plt.show()
'''
}

def build():
    archive=zipfile.ZipFile(next((ROOT/'pyFiles').glob('*.zip')))
    (BASE/'original_py').mkdir(exist_ok=True)
    manifest=[]
    for n,title in enumerate(TITLES,1):
        filename=f'LA4DS_ch{n:02}.py'; raw=archive.read(filename)
        (BASE/'original_py'/filename).write_bytes(raw)
        lines=raw.decode('utf-8-sig').splitlines()
        src=[(k+1,l) for k,l in enumerate(lines) if l.strip()]
        old=json.loads((ROOT/f'LA4DS_ch{n:02}.ipynb').read_text(encoding='utf-8'))
        stem=f'{n:02}. {title}'
        intro=f'# {n}. {title}\n\n'+LESSONS[n]
        intro+='\n\n## 읽기 안내\n\n- 이 글은 제공된 Python 예제를 바탕으로 새로 작성한 해설입니다. 연습문제의 질문은 코드에서 확인되는 학습 목표를 재구성했으며 책의 문제 원문을 옮긴 것이 아닙니다.\n- 코드·실행 결과는 아래 순서로 연결됩니다. 앞 셀의 변수를 쓰므로 노트북은 처음부터 실행하세요.\n- 난수 시드는 장마다 고정했습니다. 실행 시간과 마지막 소수 자릿수는 환경에 따라 달라질 수 있습니다.\n- `1e-14` 같은 작은 잔차는 부동소수점 오차일 수 있습니다. 수학적 0과 컴퓨터의 정확한 0을 구분하세요.\n\n## 실행 환경\n'
        nb=nf.v4.new_notebook(cells=[nf.v4.new_markdown_cell(intro)])
        setup=f'''from pathlib import Path
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display
ROOT = Path.cwd()
if not (ROOT / 'data').exists():
    ROOT = ROOT / 'blog_linear_algebra'
DATA = ROOT / 'data'
ASSET = ROOT / 'assets' / 'ch{n:02}'
ASSET.mkdir(parents=True, exist_ok=True)
np.random.seed({20260925+n})
np.set_printoptions(precision=6, suppress=True, threshold=120)
plt.rcParams.update({{'figure.dpi': 100, 'savefig.dpi': 140, 'font.size': 12}})
print('재현용 난수 시드:', {20260925+n})'''
        nb.cells.append(nf.v4.new_code_cell(setup,metadata={'role':'setup'}))
        pos=0; ex=None; seen=0; section='본문 예제'; code_seq=0
        for i,c in enumerate(old['cells']):
            cs=''.join(c['source']).strip()
            if c['cell_type']=='markdown':
                m=re.search(r'Exerci(?:se|es)\s+(\d+)',cs)
                if m:
                    seen+=1; ex=int(m[1]); ex=6 if n==6 and seen==6 else ex
                    info=EXERCISES[n][ex]
                    section=f'연습문제 {ex} · {info[0]}'
                    nb.cells.append(nf.v4.new_markdown_cell(f'## {section}\n\n- **목표**: {info[1]}\n- **풀이 순서**: {info[2]}\n- **결과 해석**: {info[3]}',metadata={'exercise':ex}))
                elif ex is None and i>0 and cs and 'Exercises' not in cs and 'Solutions' not in cs:
                    section=cs.lstrip('# ').splitlines()[0]
                    nb.cells.append(nf.v4.new_markdown_cell('### '+SECTION_KO.get(section,section)))
                continue
            if not cs: continue
            cnt=sum(bool(l.strip()) for l in cs.splitlines())
            chunk=src[pos:pos+cnt]; pos+=cnt
            assert len(chunk)==cnt,(n,i)
            a,b=chunk[0][0],chunk[-1][0]
            s='\n'.join(lines[a-1:b]); code_seq+=1
            s,notes=patch(n,i,s)
            if (n,i) in EXTRA:
                s+='\n\n'+EXTRA[(n,i)]
                notes.append('원본에 없던 독립 실행·검증 코드를 추가했습니다.')
            label=f'코드 {n:02}-{code_seq:02}'
            note=f'### {label}\n\n- 원본: `original_py/{filename}` {a}–{b}행.'
            if notes:
                note+='\n'+ '\n'.join('- **보완**: '+v for v in notes)
                changes.append({'chapter':n,'cell':i,'lines':[a,b],'notes':notes})
            nb.cells.append(nf.v4.new_markdown_cell(note))
            nb.cells.append(nf.v4.new_code_cell(s,metadata={'source_file':filename,'source_lines':[a,b],'original_cell':i,'exercise':ex,'label':label}))
        assert pos==len(src),(n,pos,len(src))
        from checks import CHECKS
        nb.cells.append(nf.v4.new_markdown_cell('## 핵심 결과 다시 확인하기\n\n- 아래는 원본과 별도로 추가한 작은 검증 예제입니다.\n- `assert`가 통과하면 해당 수학적 관계가 지정한 수치 허용오차 안에서 성립한 것입니다.\n- 큰 예제의 숫자를 외우기보다 이 관계가 왜 성립하는지 설명해 보세요.'))
        nb.cells.append(nf.v4.new_code_cell(CHECKS[n],metadata={'role':'verification'}))
        nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'},'source_sha256':hashlib.sha256(raw).hexdigest(),'chapter':n}
        nf.write(nb,BASE/(stem+'.ipynb'))
        manifest.append({'chapter':n,'title':title,'stem':stem,'source':filename,'sha256':hashlib.sha256(raw).hexdigest(),'original_code_cells':code_seq,'exercises':seen})
    (BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Built 14 notebooks')

SECTION_KO={'Creating vectors':'벡터의 모양과 차원','Geometry of vectors':'화살표로 보는 벡터','Adding vectors':'벡터 덧셈','Subtracting vectors':'벡터 뺄셈','Vector-scalar multiplication':'스칼라 곱과 방향','Vector transpose':'행·열과 전치','The dot product is distributive':'내적의 분배법칙','Linear weighted combinations':'선형결합','Basis vectors and points':'기저와 좌표','Visualizing matrices as images':'행렬을 색상으로 읽기','Slicing out rows and columns':'행·열 슬라이싱','Some special matrices':'특수 행렬','Some more details about special matrices':'특수 행렬의 성질','Matrix addition':'행렬 덧셈','Shifting a matrix':'대각 이동','Scalar multiplication':'스칼라 곱','Hadamard multiplication':'원소별 곱','"Standard" matrix multiplication':'행렬 곱','Geometry of matrix-vector multiplication':'행렬이 벡터를 움직이는 방법','Transpose':'전치','Column space':'열공간','Now for R3':'3차원 열공간','Null spaces':'영공간','Covariance matrix':'공분산 행렬','Transformation matrices':'선형변환','Animating transformations':'변환 애니메이션','Image convolution':'이미지 합성곱','The matrix inverse':'역행렬','Inverse of a diagonal matrix':'대각행렬의 역행렬','The left-inverse':'왼쪽 역행렬','MP pseudoinverse':'무어–펜로즈 의사역행렬','Orthogonal matrices':'직교행렬','QR decomposition':'QR 분해','Working with matrix equations':'행렬 방정식','RREF':'기약 행 사다리꼴','LU':'LU 분해','Example in fake data':'학습용 데이터로 회귀하기','Korean bike rental regression':'서울 자전거 대여량 회귀','Using statsmodels':'statsmodels 결과 읽기','Polynomial regression':'다항 회귀','Geometry of eigenvectors':'고유벡터의 기하학','Finding eigenvalues':'고윳값 계산','Finding eigenvectors':'고유벡터 계산','Diagonalizing a matrix':'대각화','Special properties of symmetric matrices':'대칭행렬의 고유분해','Eigendecomposition of singular matrices':'특이행렬의 고유분해','Quadratic form':'이차형식','Generalized eigendecomposition':'일반화 고유분해','The SVD':'특잇값 분해','Symmetric matrix':'대칭행렬과 SVD','Creating Figure 1':'차원 축소의 기하학'}
if __name__=='__main__': build()
