_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_85717823e1.sparta_3811b5fb11 import qube_851830bece as qube_851830bece
from project.sparta_cc504a7958.sparta_154282b52b.qube_f629cfbf67 import sparta_988cda2896
@csrf_exempt
def sparta_3cef5b388c(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_851830bece.sparta_3cef5b388c(B)
@csrf_exempt
def sparta_875d6625c0(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_da3774beeb(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_5d2a5cd6f1(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)