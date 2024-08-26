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
from project.sparta_991c77bcde.sparta_bddc675c8b import qube_ef8d2aba58 as qube_ef8d2aba58
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_8e7f45378d
@csrf_exempt
@sparta_8e7f45378d
def sparta_dce7a5fd66(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.sparta_dce7a5fd66(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_66de3cb5de(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_ef8d2aba58.sparta_66de3cb5de(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_8e7f45378d
def sparta_52b29e20a7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_ef8d2aba58.sparta_52b29e20a7(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_8e7f45378d
def sparta_0bc8829a39(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.sparta_0bc8829a39(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_b79f9e21fb(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.sparta_b79f9e21fb(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_8e7f45378d
def sparta_8167800967(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.sparta_8167800967(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_71009b7074(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_ef8d2aba58.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_8e7f45378d
def sparta_f590cdf9c3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_82d5f7ae8e(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_ef8d2aba58.sparta_82d5f7ae8e(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_8ba1e4fec2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_ef8d2aba58.sparta_8ba1e4fec2(A,C);E=json.dumps(D);return HttpResponse(E)