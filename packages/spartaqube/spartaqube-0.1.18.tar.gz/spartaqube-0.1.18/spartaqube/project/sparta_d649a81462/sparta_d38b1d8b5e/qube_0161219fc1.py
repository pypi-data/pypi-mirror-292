_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_991c77bcde.sparta_23c481f08b import qube_fe08016699 as qube_fe08016699
from project.sparta_e47c1b14a9.sparta_cc215461ed.qube_b4ac0415ab import sparta_04b342a08a
@csrf_exempt
def sparta_e2deb9a692(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_fe08016699.sparta_e2deb9a692(B)
@csrf_exempt
def sparta_0f5d477790(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_d40c115937(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_885aa0f69d(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)