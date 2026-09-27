CHECKS={
1:'''_v=np.array([3.,4.]); _a=np.array([1.,2.]); _b=np.array([1.5,.5])
_p=_a*(_a@_b)/(_a@_a); _e=_b-_p
print('길이:',np.linalg.norm(_v),'단위벡터:',_v/np.linalg.norm(_v))
print('투영:',_p,'잔차:',_e,'직교 내적:',_a@_e)
assert np.allclose(_p,[.5,1]) and np.allclose(_a@_e,0)
''',
2:'''_B=np.array([[3.,-3.],[1.,1.]])
for _p in [np.array([3.,1.]),np.array([-6.,2.])]:
    _coord=np.linalg.solve(_B,_p)
    print('점:',_p,'새 좌표:',_coord)
    assert np.allclose(_B@_coord,_p)
print('기저 행렬의 랭크:',np.linalg.matrix_rank(_B))
''',
3:'''_x=np.arange(4.); _y=_x+10
_cos=_x@_y/(np.linalg.norm(_x)*np.linalg.norm(_y))
_r=np.corrcoef(_x,_y)[0,1]
print('상관:',_r,'코사인:',round(_cos,6))
assert np.isclose(_r,1) and _cos<1
_d=np.diff(np.r_[np.zeros(3),np.ones(3),np.zeros(3)])
print('계단 신호 차분:',_d)
assert np.array_equal(_d,[0,0,1,0,0,-1,0,0])
''',
4:'''_A=np.array([[1,2],[3,4]]); _B=np.array([[2,0],[1,2]])
print('원소별 곱:\\n',_A*_B); print('행렬 곱:\\n',_A@_B)
assert np.array_equal(_A@_B,[[4,4],[10,8]])
assert np.array_equal((_A@_B).T,_B.T@_A.T)
print('전치 곱 공식 검증: 통과')
''',
5:'''_A=np.array([[1.,2.],[3.,6.]]); _z=np.array([-2.,1.])
print('랭크:',np.linalg.matrix_rank(_A),'영공간 벡터의 출력:',_A@_z)
print('Frobenius 노름:',np.linalg.norm(_A,'fro'))
assert np.linalg.matrix_rank(_A)==1 and np.allclose(_A@_z,0)
assert np.allclose(np.linalg.norm(_A,'fro')**2,np.trace(_A.T@_A))
''',
6:'''_X=np.array([[1.,2.],[2.,4.],[3.,6.]])
_Xc=_X-_X.mean(axis=0); _C=_Xc.T@_Xc/(len(_X)-1)
print('공분산:\\n',_C)
assert np.allclose(_C,np.cov(_X,rowvar=False))
assert np.allclose(corrMat,corrMat_np)
print('원자료의 직접 계산 상관과 NumPy 최대 차이:',np.max(np.abs(corrMat-corrMat_np)))
assert np.allclose(convoutput,convoutput2)
print('대칭 커널의 수동 계산과 SciPy 합성곱 일치: 통과')
''',
7:'''_A=np.array([[1.,4.],[2.,7.]])
_Ai=np.linalg.inv(_A)
print('역행렬:\\n',_Ai)
assert np.allclose(_A@_Ai,np.eye(2))
_S=np.array([[1.,4.],[2.,8.]]); _P=np.linalg.pinv(_S)
print('AA+ (항등행렬이 아닌 투영):\\n',_S@_P)
assert np.allclose(_S@_P@_S,_S)
assert np.allclose((_S@_P).T,_S@_P)
''',
8:'''_A=np.array([[1.,1.],[1.,0.],[0.,1.]])
_Q,_R=np.linalg.qr(_A)
print('Q shape:',_Q.shape,'R shape:',_R.shape)
print('직교 오차:',np.linalg.norm(_Q.T@_Q-np.eye(2)))
print('재구성 오차:',np.linalg.norm(_A-_Q@_R))
assert np.allclose(_Q.T@_Q,np.eye(2)) and np.allclose(_A,_Q@_R)
''',
9:'''from scipy.linalg import lu
_A=np.array([[0.,2.],[3.,4.]])
_P,_L,_U=lu(_A)
print('P:\\n',_P,'\\nL:\\n',_L,'\\nU:\\n',_U)
print('행렬식:',np.linalg.det(_P)*np.prod(np.diag(_U)))
assert np.allclose(_A,_P@_L@_U)
assert np.allclose(np.linalg.det(_A),np.linalg.det(_P)*np.prod(np.diag(_U)))
''',
10:'''_x=np.arange(1.,6.); _y=np.array([0.,3.,2.,5.,5.])
_X=np.column_stack([np.ones(5),_x]); _b=np.linalg.lstsq(_X,_y,rcond=None)[0]
_e=_y-_X@_b
print('절편, 기울기:',_b,'SSE:',round(_e@_e,6))
print('X.T @ 잔차:',_X.T@_e)
assert np.allclose(_b,[-.6,1.2]) and np.allclose(_e@_e,3.6)
assert np.allclose(_X.T@_e,0)
''',
11:'''_y=np.array([1.,2.,3.,4.]); _pred=_y+100
_corr2=np.corrcoef(_y,_pred)[0,1]**2
_r2=1-np.sum((_y-_pred)**2)/np.sum((_y-_y.mean())**2)
print('100만큼 틀린 예측의 상관제곱:',_corr2)
print('같은 예측의 1-SSE/SST:',_r2)
assert np.isclose(_corr2,1) and _r2<0
_D=np.array([[1.,1.],[2.,2.],[3.,3.]])
_G=_D.T@_D+.1*np.eye(2)
print('정규화 전/후 랭크:',np.linalg.matrix_rank(_D.T@_D),np.linalg.matrix_rank(_G))
assert np.linalg.matrix_rank(_G)==2
''',
12:'''_A=np.array([[2.,1.],[1.,2.]])
_lam,_V=np.linalg.eigh(_A)
print('고윳값:',_lam)
print('고유방정식 잔차:',np.linalg.norm(_A@_V-_V@np.diag(_lam)))
assert np.allclose(_lam,[1,3]) and np.allclose(_A,_V@np.diag(_lam)@_V.T)
assert np.allclose(_V.T@_V,np.eye(2))
''',
13:'''_A=np.diag([3.,1.]); _U,_s,_Vt=np.linalg.svd(_A,full_matrices=False)
_Ak=(_U[:,:1]*_s[:1])@_Vt[:1]
_error=np.linalg.norm(_A-_Ak,'fro')
print('rank 1 재구성:\\n',_Ak)
print('오차:',_error,'보존 에너지:',_s[0]**2/np.sum(_s**2))
assert np.allclose(_error,1) and np.allclose(_error**2,np.sum(_s[1:]**2))
''',
14:'''_X0=data.to_numpy(); _Xc=_X0-_X0.mean(axis=0)
_U,_s,_Vt=np.linalg.svd(_Xc,full_matrices=False)
_eig=np.linalg.eigvalsh(_Xc.T@_Xc/(len(_Xc)-1))[::-1]
print('PCA 고윳값과 SVD 환산값의 최대 차이:',np.max(np.abs(_eig-_s**2/(len(_Xc)-1))))
assert np.allclose(_eig,_s**2/(len(_Xc)-1))
_theory=np.sqrt(np.array([np.sum(s[j:]**2) for j in range(1,len(s)+1)]))
print('실제 이미지 복원 오차와 이론식 차이:',np.max(np.abs(kError-_theory)))
assert np.allclose(kError,_theory,atol=1e-9)
# 잡음 추가 단계와 같은 범위에서 원본 목표를 정의한다.
_sum=strav+sinimg
_target=(strav-_sum.min())/(_sum.max()-_sum.min())
print('잡음 포함/성분 제거 후 목표 대비 오차:',np.linalg.norm(stravNoise-_target),np.linalg.norm(stravRecNoNoise-_target))
print('성분 제거는 신호도 바꿀 수 있으므로 제거 그림을 함께 확인합니다.')
'''
}
