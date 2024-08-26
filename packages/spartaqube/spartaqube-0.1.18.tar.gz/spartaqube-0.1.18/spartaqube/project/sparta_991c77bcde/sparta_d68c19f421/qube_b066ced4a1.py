_E='Path not found...'
_D='folders'
_C='typeexplorer'
_B='res'
_A='currentPath'
import os
from os import listdir
from os.path import isfile,join
def sparta_33f82ef23c(json_data,userObj):
	A=json_data
	try:D=A[_A];E=A[_C];B=os.path.dirname(D);F,G=sparta_286e048908(B,E);C={_B:1,'files':G,_D:F,_A:B}
	except:C={_B:-1,'msg':_E}
	return C
def sparta_8c321272c1(json_data,userObj):
	A=json_data
	try:B=A[_A];D=A[_C];E,F=sparta_286e048908(B,D);C={_B:1,'files':F,_D:E,_A:B}
	except:C={_B:-1,'msg':_E}
	return C
def sparta_286e048908(currentPath,typeexplorer=None):
	C=typeexplorer;A=currentPath;B=[B for B in listdir(A)if isfile(join(A,B))]
	if C is not None:
		if int(C)==2:D=['xls','xlsx','xlsm'];B=[A for A in B if A.split('.')[-1]in D]
	E=[B for B in os.listdir(A)if os.path.isdir(os.path.join(A,B))];return E,B
def sparta_f4e2c2fa40(currentPath):
	E='___sq___files___';D='___sq___show___';C='___sq___path___';B=currentPath
	def G(starting_path):
		F=starting_path;G={'':{}}
		for(B,H,K)in os.walk(F):
			A=G;I=B;B=B[len(F):]
			for J in B.split(os.sep):
				L=A;A=A[J]
				if len(A)>0:A[C]=I;A[D]=0
			if H:
				for M in H:A[M]={}
			else:L[J]={E:K,C:I,D:0}
		return G['']
	A=G(B)
	def F(tmp_dict,tmp_path):
		B=tmp_dict;A=tmp_path;B[E]=[B for B in listdir(A)if isfile(join(A,B))];B[C]=A
		for(G,D)in B.items():
			if isinstance(D,dict):F(D,os.path.join(A,G))
	if isinstance(A,dict):F(A,B);A[E]=[A for A in listdir(B)if isfile(join(B,A))];A[C]=B;A[D]=1
	else:A={E:A,C:B,D:1}
	return A