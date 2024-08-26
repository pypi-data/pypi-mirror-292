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
from project.sparta_85717823e1.sparta_8b295a482a import qube_715b8fc2da as qube_715b8fc2da
from project.sparta_85717823e1.sparta_8b295a482a import qube_52f15729d5 as qube_52f15729d5
from project.sparta_85717823e1.sparta_c648d09df3 import qube_f514117b98 as qube_f514117b98
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_3d3d3187e4
@csrf_exempt
@sparta_3d3d3187e4
def sparta_98126de152(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_715b8fc2da.sparta_4e049ea40d(E,A.user,B[D])
	else:C={_C:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_2331f76eb1(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_4c2af28da0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_c7c05bb08b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_b08a94a46a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_588191972b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_c9d839e23a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_9a793a8bef(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_52f15729d5.sparta_b7cf16e947(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_fcb59e4ec3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_cf604fb719(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_0f18ec3c2c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_597c061b61(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_7461a2117c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_512728f508(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_8214df2183(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_715b8fc2da.sparta_fcb1eb8e7e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_ee59dac42f(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_715b8fc2da.sparta_227103bdc2(J,A.user)
	if C[_C]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_D]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_3d3d3187e4
def sparta_a27594ae65(request):
	E='folderName';C=request;F=C.GET[_B];D=C.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};B=qube_715b8fc2da.sparta_4458462019(G,C.user);print(_C);print(B)
	if B[_C]==1:H=B['zip'];I=B[_H];A=HttpResponse();A.write(H.getvalue());A[_D]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_D]=_F.format(K)
	return A
@csrf_exempt
@sparta_3d3d3187e4
def sparta_d30da8008d(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_715b8fc2da.sparta_3ce8a6bfb3(F,B.user)
	if C[_C]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_D]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_D]=_F.format(J)
	return A