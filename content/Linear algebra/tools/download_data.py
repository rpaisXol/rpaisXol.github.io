from pathlib import Path
import urllib.request,json
p=Path(__file__).resolve().parents[1]/'data'
urls=json.loads((p/'sources.json').read_text(encoding='utf-8'))
for name,url in urls.items():
    req=urllib.request.Request(url,headers={'User-Agent':'LinearAlgebraEducationalNotebook/1.0'})
    with urllib.request.urlopen(req,timeout=40) as response:
        (p/name).write_bytes(response.read())
    print(name,(p/name).stat().st_size)
