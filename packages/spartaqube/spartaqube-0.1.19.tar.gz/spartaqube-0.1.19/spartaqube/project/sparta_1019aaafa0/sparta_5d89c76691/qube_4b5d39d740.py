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
from project.sparta_b51bfafd7d.sparta_4e48b0df81 import qube_65fb0fb110 as qube_65fb0fb110
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_9990890d7c
@csrf_exempt
@sparta_9990890d7c
def sparta_3b0331cb09(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.sparta_3b0331cb09(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_cf05d50beb(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_65fb0fb110.sparta_cf05d50beb(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_9990890d7c
def sparta_976eb49081(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_65fb0fb110.sparta_976eb49081(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_9990890d7c
def sparta_500be823a6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.sparta_500be823a6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_e0ca069cb4(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.sparta_e0ca069cb4(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9990890d7c
def sparta_4f1458d6ee(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.sparta_4f1458d6ee(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_9388fae23d(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_65fb0fb110.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_9990890d7c
def sparta_24f3fb805d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_955eb7d796(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_65fb0fb110.sparta_955eb7d796(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_2461308a90(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_65fb0fb110.sparta_2461308a90(A,C);E=json.dumps(D);return HttpResponse(E)