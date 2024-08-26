_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='Content-Disposition'
_C='res'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_991c77bcde.sparta_843f7933ba import qube_72bc350137 as qube_72bc350137
from project.sparta_991c77bcde.sparta_843f7933ba import qube_d22f818725 as qube_d22f818725
from project.sparta_991c77bcde.sparta_3b03ddaeb5 import qube_908d5bb7ea as qube_908d5bb7ea
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_8e7f45378d
@csrf_exempt
@sparta_8e7f45378d
def sparta_71b6bd551d(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_72bc350137.sparta_19b929817a(E,A.user,B[D])
	else:C={_C:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_8e7f45378d
def sparta_27e3a4e129(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_a6267e7ff5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_1bc8da4d69(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_2a9085d8cf(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_a055e0aec2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_f846dfaf2f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_3bd4339eaf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d22f818725.sparta_997bb7d1e1(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_830fdeda83(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_987e9ca859(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_8b2f03d231(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_2b3f2f2be0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_af4e00c6d2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_45532c9820(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_95dfe0a6f6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_72bc350137.sparta_63783eb574(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_e04856e536(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_72bc350137.sparta_87e762f8ef(J,A.user)
	if C[_C]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_D]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_8e7f45378d
def sparta_a1a709b184(request):
	E='folderName';C=request;F=C.GET[_B];D=C.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};B=qube_72bc350137.sparta_63a9dfcf51(G,C.user);print(_C);print(B)
	if B[_C]==1:H=B['zip'];I=B[_H];A=HttpResponse();A.write(H.getvalue());A[_D]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_D]=_F.format(K)
	return A
@csrf_exempt
@sparta_8e7f45378d
def sparta_b9ccb0c7e1(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_72bc350137.sparta_e395f3975a(F,B.user)
	if C[_C]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_D]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_D]=_F.format(J)
	return A