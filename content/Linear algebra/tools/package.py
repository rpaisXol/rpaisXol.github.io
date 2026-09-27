from pathlib import Path
import zipfile
BASE=Path(__file__).resolve().parents[1]
target=BASE.parent/'선형대수학_14장_노트북_MD.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in sorted(BASE.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        z.write(p,Path(BASE.name)/p.relative_to(BASE))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    chapters=[s for s in z.namelist() if s.count('/')==1 and s.endswith('.ipynb')]
    assert len(chapters)==14
print(target,round(target.stat().st_size/1024**2,2),'MiB')
