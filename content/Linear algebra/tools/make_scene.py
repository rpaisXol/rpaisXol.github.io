"""외부 사진 없이 합성곱/SVD 실습에 쓸 원본 도형 이미지를 만든다."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).resolve().parents[1]/'data'
y,x=np.mgrid[0:240,0:320]
a=np.zeros((240,320,3),dtype=np.uint8)
a[:,:,0]=205+25*x/320
a[:,:,1]=220+20*y/240
a[:,:,2]=235
im=Image.fromarray(a);d=ImageDraw.Draw(im)
d.rectangle((0,175,320,240),fill=(70,125,90))
d.ellipse((235,20,285,70),fill=(250,190,65))
d.rectangle((50,95,235,190),fill=(222,170,120),outline=(30,45,70),width=3)
d.polygon([(35,95),(140,40),(250,95)],fill=(55,75,105))
for xx in [72,112,175,215]:
    d.rectangle((xx,112,xx+15,148),fill=(50,130,175),outline=(20,40,65),width=2)
d.rectangle((135,142,160,190),fill=(90,65,50))
d.line([(0,220),(320,197)],fill=(225,225,180),width=6)
im.save(p/'generated_scene.png')
print('Generated scene',im.size)
