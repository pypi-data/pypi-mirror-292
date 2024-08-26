_M='Error Final'
_L='zipName'
_K='Except2'
_J='file > '
_I='rmdir /S /Q "{}"'
_H='folderPath2MoveArr'
_G='filesPath2MoveArr'
_F='filePath'
_E='path'
_D='fileName'
_C='errorMsg'
_B='projectPath'
_A='res'
import os,shutil,zipfile,io,uuid
from distutils.dir_util import copy_tree
from project.sparta_b51bfafd7d.sparta_8e98a7e274 import qube_5b0b590e98 as qube_5b0b590e98
from project.sparta_b51bfafd7d.sparta_b3fc7394e9 import qube_7a8ddad505 as qube_7a8ddad505
from project.sparta_b51bfafd7d.sparta_eb344707e9 import qube_3e20830412 as qube_3e20830412
def sparta_736d50629e():return str(uuid.uuid4())
def sparta_bd78669f58(app_id):
	B=coreApps.get_app_folder_default_path();A=os.path.join(B,app_id)
	if not os.path.exists(A):os.makedirs(A)
	return A
def sparta_3485643343(project_path):
	A=project_path
	try:
		if not os.path.exists(A):os.makedirs(A)
		return{_A:1}
	except Exception as B:return{_A:-1,_C:str(B)}
def sparta_af89d38051(path):
	with open(path,'a'):os.utime(path,None)
def sparta_26f5b0cf2e(json_data,userObj):
	A=json_data;print('CREATE RESOURCE');print(A);C=A[_B];D=sparta_3485643343(C)
	if D[_A]==-1:return D
	F=A['createResourceName'];G=A['createType']
	try:
		B=os.path.join(C,F)
		if int(G)==1:
			if not os.path.exists(B):os.makedirs(B)
		elif not os.path.exists(B):sparta_af89d38051(B)
		else:return{_A:-1,_C:'A file with this name already exists'}
	except Exception as E:print('Exception create new resource');print(E);return{_A:-1,_C:str(E)}
	return{_A:1}
def sparta_deb448fc67(json_data,userObj):
	A=json_data;E=A[_B];C=A['folder_location'];H=A[_G];I=A[_H]
	for B in H:
		J=B[_E];F=B[_D];G=os.path.join(J,F);D=os.path.join(C,F)
		if E in D:
			try:print(f"Move from\n{G}\nto\n{D}");shutil.move(G,D)
			except Exception as K:print('Exception move 1');print(K)
	for B in I:
		L=B[_E]
		if E in C:
			try:shutil.move(L,C)
			except:pass
	return{_A:1}
def sparta_e7c5203867(json_data,user_obj,file_obj_to_upload):
	D=file_obj_to_upload;B=json_data;A=B[_B];E=sparta_3485643343(A)
	if E[_A]==-1:return E
	F=B[_E];C=B['dragoverElem'];print('dragover_elem ');print(C)
	if len(C)>0:J=C
	if len(F)>0:
		A=os.path.join(A,F)
		if not os.path.exists(A):os.makedirs(A)
	G=os.path.join(A,D.name)
	with open(G,'wb')as H:H.write(D.read())
	I={_A:1};return I
def sparta_bec654f31a(json_data,userObj):A=json_data[_B];B=qube_3e20830412.sparta_f9ab15769d(A);C={_A:1,'folderStructure':B};return C
def sparta_93daa14819(json_data,userObj):
	A=json_data
	try:
		C=A[_B];D=A[_D];B=A[_F];E=A['sourceCode']
		if C in B:
			B=os.path.join(B,D)
			with open(B,'w')as F:F.write(E)
		return{_A:1}
	except Exception as G:return{_A:-1,_C:str(G)}
def sparta_bb86bf5318(json_data,userObj):
	A=json_data;I=A[_B];F=A[_D];B=A[_F];G=A['editName'];J=int(A['renameType'])
	if I in B:
		if J==1:
			H=os.path.dirname(B);C=os.path.join(H,F);D=os.path.join(H,G)
			try:os.rename(C,D)
			except Exception as E:return{_A:-1,_C:str(E)}
		else:
			C=os.path.join(B,F);D=os.path.join(B,G)
			try:os.rename(C,D)
			except Exception as E:return{_A:-1,_C:str(E)}
	return{_A:1}
def sparta_b135b732d7(json_data,userObj):
	B=json_data;D=B[_B];E=B[_D];A=B[_F];F=int(B['typeDelete'])
	if D in A:
		if F==1:
			try:os.rmdir(A)
			except:
				try:os.system(_I.format(A))
				except:
					try:shutil.rmtree(A)
					except Exception as C:return{_A:-1,_C:str(C)}
		else:
			A=os.path.join(A,E)
			try:os.remove(A)
			except Exception as C:return{_A:-1,_C:str(C)}
	return{_A:1}
def sparta_840bbc1d74(json_data,userObj):
	B=json_data;F=B[_G];G=B[_H];H=B[_B]
	for A in F:
		I=A[_D];E=A[_E]
		if H in E:
			J=os.path.join(E,I)
			try:os.remove(J)
			except Exception as C:return{_A:-1,_C:str(C)}
	for A in G:
		D=A[_E];print(f"Delete folder {D}")
		try:os.system(_I.format(D))
		except:
			try:shutil.rmtree(D)
			except Exception as C:return{_A:-1,_C:str(C)}
	return{_A:1}
def sparta_37d69f3403(json_data,userObj):
	A=json_data;C=A[_B];D=A[_D];B=A[_F]
	if C in B:E=os.path.join(B,D);return{_A:1,'fullPath':E}
	return{_A:-1}
def sparta_a37d6dc0a6(json_data,userObj):
	A=json_data;print('DOWNLOAD FOLDER DEBUG');print(A);B=A[_B];E=A['folderName']
	def C(zf,folder):
		D=folder
		for E in os.listdir(D):
			print(_J+str(E));A=os.path.join(D,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:C(zf,A)
				except Exception as F:print(_K);print(F)
		return zf
	try:
		D=io.BytesIO()
		with zipfile.ZipFile(D,mode='w',compression=zipfile.ZIP_DEFLATED)as F:C(F,B)
		return{_A:1,'zip':D,_L:E}
	except Exception as G:print(_M);print(G)
	return{_A:-1}
def sparta_7f94773b9c(json_data,userObj):
	B=json_data[_B];D='app'
	def C(zf,folder):
		D=folder
		for E in os.listdir(D):
			print(_J+str(E));A=os.path.join(D,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:C(zf,A)
				except Exception as F:print(_K);print(F)
		return zf
	try:
		A=io.BytesIO()
		with zipfile.ZipFile(A,mode='w',compression=zipfile.ZIP_DEFLATED)as E:C(E,B)
		return{_A:1,'zip':A,_L:D}
	except Exception as F:print(_M);print(F)
	return{_A:-1}