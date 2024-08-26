_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_b51bfafd7d.sparta_ba59edf337 import qube_eaa8b6f778 as qube_eaa8b6f778
from project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 import sparta_132f4604cb
@csrf_exempt
def sparta_ef7f114302(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_eaa8b6f778.sparta_ef7f114302(B)
@csrf_exempt
def sparta_8474fbde98(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_533e3c19fe(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_5f2ef73053(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)