from pathlib import Path
import subprocess,sys,concurrent.futures
BASE=Path(__file__).resolve().parents[1]
def run(n):
    r=subprocess.run([sys.executable,str(BASE/'tools/execute.py'),str(n)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(n,r.returncode,r.stdout[-4000:],r.stderr[-2000:],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(run,[int(n) for n in sys.argv[1:]] or range(1,15)))
