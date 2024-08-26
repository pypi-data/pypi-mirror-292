_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_85717823e1.sparta_1b64ac3912 import qube_d2db12ede5 as qube_d2db12ede5
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_3d3d3187e4
@csrf_exempt
@sparta_3d3d3187e4
def sparta_55d6b48d22(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.sparta_55d6b48d22(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_560ea065b6(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_d2db12ede5.sparta_560ea065b6(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_9e3e02f683(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_d2db12ede5.sparta_9e3e02f683(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_1b38df748c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.sparta_1b38df748c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_ff68be8656(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.sparta_ff68be8656(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_a8b8b64713(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.sparta_a8b8b64713(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_f89c69358a(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_d2db12ede5.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_78102e2422(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_1d68025523(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_d2db12ede5.sparta_1d68025523(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_feb36c64ea(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d2db12ede5.sparta_feb36c64ea(A,C);E=json.dumps(D);return HttpResponse(E)