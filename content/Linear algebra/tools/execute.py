"""각 장을 새 IPython 프로세스에서 실행하고 모든 출력과 그림을 nbformat으로 저장한다."""
import os
os.environ['MPLBACKEND']='Agg'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,io,base64,time,traceback
import nbformat as nf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import matplotlib.pyplot as plt
from IPython.display import display,Image

BASE=Path(__file__).resolve().parents[1]
os.chdir(BASE)
n=int(sys.argv[1])
path=next(BASE.glob(f'{n:02}. *.ipynb'))
nb=nf.read(path,as_version=4)
shell=InteractiveShell.instance()
shell.ast_node_interactivity='last_expr'
shell.colors='NoColor'
shell.display_formatter.formatters['text/html'].enabled=False

def show(*args,**kwargs):
    for num in plt.get_fignums():
        fig=plt.figure(num)
        if not fig.axes: continue
        buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=110,bbox_inches='tight')
        display(Image(data=buf.getvalue()))
    plt.close('all')

plt.show=show
errors=[]; count=0; start=time.time()
log=BASE/'execution_logs'; log.mkdir(exist_ok=True)
with (log/f'ch{n:02}.log').open('w',encoding='utf-8') as out:
    for idx,c in enumerate(nb.cells):
        if c.cell_type!='code':continue
        count+=1
        out.write(f'START {count} source_cell={c.metadata.get("original_cell")}\n');out.flush()
        with capture_output() as cap:
            result=shell.run_cell(c.source,store_history=True)
            show()
        outputs=[]
        if cap.stdout: outputs.append(nf.v4.new_output('stream',name='stdout',text=cap.stdout))
        if cap.stderr: outputs.append(nf.v4.new_output('stream',name='stderr',text=cap.stderr))
        for o in cap.outputs:
            data=dict(o.data)
            for key,v in list(data.items()):
                if isinstance(v,bytes):data[key]=base64.b64encode(v).decode()
            outputs.append(nf.v4.new_output('display_data',data=data,metadata=o.metadata))
        err=result.error_before_exec or result.error_in_exec
        if err:
            error={'cell':idx,'original_cell':c.metadata.get('original_cell'),'type':type(err).__name__,'message':str(err)}
            errors.append(error)
            outputs.append(nf.v4.new_output('error',ename=type(err).__name__,evalue=str(err),traceback=traceback.format_exception(type(err),err,err.__traceback__)))
            out.write('ERROR '+str(error)+'\n')
        c.outputs=outputs;c.execution_count=count
        out.write(f'END {count} outputs={len(outputs)}\n');out.flush()
        nf.write(nb,path)
summary={'chapter':n,'code_cells':count,'errors':errors,'seconds':round(time.time()-start,2)}
(log/f'ch{n:02}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True),flush=True)
