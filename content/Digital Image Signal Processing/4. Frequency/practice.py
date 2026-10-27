# -*- coding: utf-8 -*-
# DFT 계산과 DC 성분부터 이어지는 장 전체 실습 코드입니다.
# 셀 1: DFT 계산과 DC 성분
# FFT로 복소 계수를 계산하고 DC를 픽셀 수로 나눈 값이 평균 밝기인지 확인한다.

# Path는 운영체제에 맞게 파일 경로를 조합하는 데 사용한다.
from pathlib import Path
import json
# OpenCV는 영상 처리, NumPy는 배열 계산, Matplotlib은 결과 시각화에 사용한다.
import cv2
import numpy as np
import matplotlib.pyplot as plt
# 현재 작업 폴더를 기준으로 assets를 찾는다. 노트북은 각 장의 폴더에서 실행한다.
ROOT=Path.cwd()  # 노트북과 assets 폴더가 있는 위치
OUT=ROOT/'assets'
# 파일을 바이트 배열로 읽어 디코딩한다. IMREAD_COLOR의 결과는 BGR 순서다.
bgr=cv2.imdecode(np.fromfile(OUT/'Lenna.png',np.uint8),cv2.IMREAD_COLOR)
if bgr is None: raise FileNotFoundError('assets/Lenna.png를 확인하세요.')
# B·G·R을 밝기 가중합으로 바꾸어 단일 채널 영상으로 만든다.
f=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY).astype(np.float64)

# 공간 영상을 복소수 주파수 계수로 변환한다. 기본 FFT는 정방향 스케일을 나누지 않는다.
F=np.fft.fft2(f)
print('OpenCV:',cv2.__version__,'영상 크기:',f.shape)
print('평균 밝기:',f.mean(),'DC / 픽셀 수:',F[0,0].real/f.size)
assert np.isclose(F[0,0].real,f.sum())
plt.figure(figsize=(4,4))
plt.imshow(f,cmap='gray',vmin=0,vmax=255)
plt.title('Lenna grayscale')
plt.axis('off')
plt.show()

# 셀 2: 줄무늬의 공간 주파수
# 128픽셀 동안 4회와 16회 반복하는 코사인파의 주파수 위치를 비교한다.

n=128
x=np.arange(n)
fig,axs=plt.subplots(2,2,figsize=(9,7))
for i,k in enumerate([4,16]):
    stripes=np.tile(128+80*np.cos(2*np.pi*k*x/n),(n,1))
    S=np.fft.fftshift(np.fft.fft2(stripes-128))
    axs[0,i].imshow(stripes,cmap='gray',vmin=0,vmax=255)
    axs[0,i].set_title(f'{k} cycles / 128 pixels')
    axs[0,i].axis('off')
    freq=np.fft.fftshift(np.fft.fftfreq(n))
    axs[1,i].plot(freq,np.abs(S[n//2])/n**2)
    axs[1,i].set(xlabel='fx (cycles/pixel)',ylabel='Normalized magnitude',xlim=(-0.5,0.5))
    peaks=np.sort(freq[np.argsort(np.abs(S[n//2]))[-2:]])
    assert np.allclose(peaks,[-k/n,k/n])
    print(k,'회 반복: 봉우리',peaks.tolist())
fig.tight_layout()
plt.show()

# 셀 3: 크기와 위상 표시
# 크기에는 log1p를 적용해 작은 성분도 보이게 하고, 위상은 라디안으로 표시한다.

# DC가 중앙에 오도록 배열 위치만 재배치한다. 주파수 값 자체를 새로 계산하지 않는다.
Fs=np.fft.fftshift(F)
magnitude=np.abs(Fs)
phase=np.angle(Fs)
fig,axs=plt.subplots(1,3,figsize=(12,4))
for ax,a,title,cmap in zip(axs,[magnitude,np.log1p(magnitude),phase],
                         ['Magnitude','Log magnitude','Phase (radians)'],['gray','gray','twilight']):
    im=ax.imshow(a,cmap=cmap,**({'vmin':-np.pi,'vmax':np.pi} if title.startswith('Phase') else {}))
    ax.set_title(title)
    ax.axis('off')
    fig.colorbar(im,ax=ax,shrink=.65)
fig.tight_layout()
plt.show()

# 셀 4: 순환 이동과 위상
# 오른쪽으로 30픽셀 이동하면 크기 스펙트럼은 유지되고 위상 관계가 달라진다.

shift=np.roll(f,30,axis=1)
assert np.allclose(abs(np.fft.fft2(shift)),abs(F),atol=1e-7)
fig,axs=plt.subplots(1,2,figsize=(8,4))
for ax,a,title in zip(axs,[f,shift],['Original','Circular shift: 30 pixels']):
    ax.imshow(a,cmap='gray',vmin=0,vmax=255);ax.set_title(title);ax.axis('off')
fig.tight_layout();plt.show()


F_shift=np.fft.fft2(shift)
print('순환 이동 전후 크기 최대 차이:',float(np.abs(np.abs(F_shift)-np.abs(F)).max()))
# 순환 이동 정리: 가로 30픽셀 이동은 주파수별 위상 변화를 만든다.
phase_factor=np.exp(-2j*np.pi*np.fft.fftfreq(f.shape[1])*30)
assert np.allclose(F_shift,F*phase_factor[None,:],atol=1e-7)
print('위상 변화 관계 검증 통과')

# 셀 5: fftshift 해제와 역변환
# ifftshift로 원래 순서를 복구한 후 역변환하며 실수부 오차와 허수 잔차를 확인한다.

# ifftshift로 배열 순서를 되돌린 뒤 역변환한다. NumPy는 역변환에서 픽셀 수로 나눈다.
rest=np.fft.ifft2(np.fft.ifftshift(Fs))
err=float(np.abs(rest.real-f).max())
assert err<1e-9 and np.abs(rest.imag).max()<1e-9
# 홀수 크기에서는 두 번 fftshift 하는 것으로 역이동을 대신할 수 없다.
odd=f[:249,:247]
odd_back=np.fft.ifft2(np.fft.ifftshift(np.fft.fftshift(np.fft.fft2(odd))))
assert np.max(np.abs(odd_back-odd))<1e-9
print('역변환 최대 오차:',err)
print('최대 허수 잔차:',float(np.abs(rest.imag).max()))
fig,axs=plt.subplots(2,3,figsize=(12,8))
for ax,title,a,cmap in zip(axs.flat,['Original','Unshifted log magnitude','Shifted log magnitude','Phase (radians)','Inverse DFT','Absolute reconstruction error'],[f,np.log1p(abs(F)),np.log1p(abs(Fs)),np.angle(Fs),rest.real,abs(rest.real-f)],['gray','gray','gray','twilight','gray','magma']):
    kwargs={'vmin':0,'vmax':255} if title in ['Original','Inverse DFT'] else {}
    im=ax.imshow(a,cmap=cmap,**kwargs)
    ax.set_title(title)
    ax.axis('off')
    if title in ['Phase (radians)','Absolute reconstruction error']:
        fig.colorbar(im,ax=ax,shrink=.7)
fig.tight_layout()
plt.show()

# 셀 6: NumPy와 OpenCV DFT 비교
# OpenCV의 실수부·허수부 2채널을 복소 배열로 조합하고 역변환 스케일을 맞춘다.

# DFT_COMPLEX_OUTPUT을 지정해 실수부·허수부 두 채널을 얻는다.
cvF=cv2.dft(f,flags=cv2.DFT_COMPLEX_OUTPUT)
cv_complex=cvF[:,:,0]+1j*cvF[:,:,1]
assert np.allclose(F,cv_complex,atol=1e-7)
# DFT_SCALE로 역변환 정규화를 적용하고 켤레 대칭 계수에서 실수 출력을 얻는다.
cvback=cv2.idft(cvF,flags=cv2.DFT_SCALE|cv2.DFT_REAL_OUTPUT)
assert np.max(np.abs(cvback-f))<1e-9
print('NumPy shape:',F.shape,'OpenCV shape:',cvF.shape)
print('변환 계수 최대 차이:',float(np.abs(F-cv_complex).max()))
print('OpenCV 역변환 최대 오차:',float(np.abs(cvback-f).max()))

# 셀 7: 반사 패딩과 주파수 좌표
# 경계 영향을 줄이기 위해 64픽셀 패딩하고 cycles/pixel 좌표를 만든다.

# 반사 패딩 후 주파수 영역에서 처리하고 원본 영역을 잘라냅니다.
pad=64
# 반사 패딩은 반대편 경계가 직접 연결되는 영향을 줄이며, 처리 후 원래 영역만 자른다.
padded=np.pad(f,pad,mode='reflect')
P=np.fft.fftshift(np.fft.fft2(padded))
# shape는 (높이, 너비) 순서다. 좌표 (x, y)로 읽을 때는 배열 인덱스 [y, x]와 구분한다.
h,w=padded.shape
# 세로 주파수 좌표를 cycles/pixel 단위로 만들고 스펙트럼과 같은 순서로 이동한다.
fy=np.fft.fftshift(np.fft.fftfreq(h))
# 가로 주파수 좌표도 동일하게 구성하여 직사각형 영상에서 축 간 단위를 맞춘다.
fx=np.fft.fftshift(np.fft.fftfreq(w))
FX,FY=np.meshgrid(fx,fy);rho=np.hypot(FX,FY)

print('원본 크기:',f.shape,'패딩 후:',padded.shape)
print('가로 주파수 간격:',1/w,'cycles/pixel')

# 셀 8: 저역·고역·대역 통과 필터
# 복소 스펙트럼에 마스크를 곱하고 역변환한다. 고역·대역 결과의 음수를 유지한다.

cut=.06; lo=.03; hi=.12
# 중심 저주파는 유지하고 멀어질수록 감쇠시키며, hp=1-lp로 보완 고역을 만든다.
lp=np.exp(-rho**2/(2*cut**2)); hp=1-lp
# 폭이 넓은 저역 마스크에서 좁은 저역 마스크를 빼 부드러운 대역 통과를 만든다.
bp=np.exp(-rho**2/(2*hi**2))-np.exp(-rho**2/(2*lo**2))
masks=[lp,hp,bp]; names=['Gaussian LP: s=0.06','Gaussian HP: s=0.06','Gaussian BP: 0.03 / 0.12']
outputs=[];residual=[]
for mask in masks:
    # 표시용 크기 그림이 아닌 복소 스펙트럼에 마스크를 곱하여 역변환한다.
    z=np.fft.ifft2(np.fft.ifftshift(P*mask))
    residual.append(float(abs(z.imag).max())); assert residual[-1]<1e-9
    # 반사 패딩을 제외하고 입력과 같은 크기로 결과를 자른다.
    outputs.append(z.real[pad:pad+f.shape[0],pad:pad+f.shape[1]])
assert np.max(abs(outputs[0]+outputs[1]-f))<1e-9
fig,axs=plt.subplots(2,3,figsize=(12,8))
for i,(name,mask,out) in enumerate(zip(names,masks,outputs)):
    im=axs[0,i].imshow(mask,cmap='gray',vmin=0,vmax=1,extent=[fx[0],fx[-1],fy[-1],fy[0]])
    axs[0,i].set_title(name);axs[0,i].set_xlabel('fx (cycles/pixel)');axs[0,i].set_ylabel('fy (cycles/pixel)')
    if i==0: im=axs[1,i].imshow(out,cmap='gray',vmin=0,vmax=255)
    else:
        m=abs(out).max();im=axs[1,i].imshow(out,cmap='coolwarm',vmin=-m,vmax=m)
    axs[1,i].axis('off');fig.colorbar(im,ax=axs[1,i],shrink=.7)
fig.tight_layout();plt.show()
r=np.linspace(0,.5,1000)
fig,ax=plt.subplots(figsize=(8,4))
for a,label in zip([np.exp(-r*r/(2*cut*cut)),1-np.exp(-r*r/(2*cut*cut)),np.exp(-r*r/(2*hi*hi))-np.exp(-r*r/(2*lo*lo))],names):ax.plot(r,a,label=label)
ax.set(xlabel='Radial frequency (cycles/pixel)',ylabel='Gain',ylim=(0,1.05),xlim=(0,.5));ax.legend();ax.grid(alpha=.3)
fig.tight_layout();plt.show()

print('필터 결과 최대 허수 잔차:',max(residual))
print('LP + HP 복원 최대 오차:',float(abs(outputs[0]+outputs[1]-f).max()))
for name,a in zip(names,outputs):
    print(name,'범위:',float(a.min()),float(a.max()))
# 다시 분석할 수 있도록 계산 배열을 원래 자료형으로 보존한다.
np.savez_compressed(ROOT/'frequency_arrays.npz',spectrum=F,lowpass=outputs[0],highpass=outputs[1],bandpass=outputs[2])
