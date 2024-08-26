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
from project.sparta_b51bfafd7d.sparta_ddf1f2e53e import qube_9f247b80ca as qube_9f247b80ca
from project.sparta_b51bfafd7d.sparta_ddf1f2e53e import qube_6c7fda7f0b as qube_6c7fda7f0b
from project.sparta_b51bfafd7d.sparta_b3fc7394e9 import qube_7a8ddad505 as qube_7a8ddad505
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_9990890d7c
@csrf_exempt
@sparta_9990890d7c
def sparta_e4a8b6dcd9(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_9f247b80ca.sparta_e7c5203867(E,A.user,B[D])
	else:C={_C:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_9990890d7c
def sparta_8cb8c76d6c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_26f5b0cf2e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_213d94b08e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_deb448fc67(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_850f43b6fa(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_bec654f31a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_a9d00a86ab(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6c7fda7f0b.sparta_217a43ac14(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_434abc80b1(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_93daa14819(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_e191c6bb5a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_bb86bf5318(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_09cb9eb6ee(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_b135b732d7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_0f3a6b9994(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9f247b80ca.sparta_840bbc1d74(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_d2d62ccdfe(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_9f247b80ca.sparta_37d69f3403(J,A.user)
	if C[_C]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_D]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_9990890d7c
def sparta_1a32bb27bc(request):
	E='folderName';C=request;F=C.GET[_B];D=C.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};B=qube_9f247b80ca.sparta_a37d6dc0a6(G,C.user);print(_C);print(B)
	if B[_C]==1:H=B['zip'];I=B[_H];A=HttpResponse();A.write(H.getvalue());A[_D]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_D]=_F.format(K)
	return A
@csrf_exempt
@sparta_9990890d7c
def sparta_0c27dfb048(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_9f247b80ca.sparta_7f94773b9c(F,B.user)
	if C[_C]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_D]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_D]=_F.format(J)
	return A