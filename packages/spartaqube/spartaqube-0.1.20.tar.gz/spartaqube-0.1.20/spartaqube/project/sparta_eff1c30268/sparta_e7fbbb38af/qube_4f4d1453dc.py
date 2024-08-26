_O='Please send valid data'
_N='dist/project/auth/resetPasswordChange.html'
_M='captcha'
_L='password'
_K='POST'
_J=False
_I='login'
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_cc504a7958.sparta_154282b52b.qube_f629cfbf67 as qube_f629cfbf67
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_7190da8f89
from project.sparta_85717823e1.sparta_3811b5fb11 import qube_851830bece as qube_851830bece
from project.sparta_b71b9eb636.sparta_f2f729df99 import qube_205fd1954c as qube_205fd1954c
from project.models import LoginLocation,UserProfile
def sparta_c2bd655143():return{'bHasCompanyEE':-1}
def sparta_0f010a2798(request):B=request;A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=qube_f629cfbf67.sparta_675e3127ca();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_7190da8f89
def sparta_ea0f764115(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_60d89c66c0(C,A)
def sparta_2c18222e55(request,redirectUrl):return sparta_60d89c66c0(request,redirectUrl)
def sparta_60d89c66c0(request,redirectUrl):
	E=redirectUrl;A=request;print('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_851830bece.sparta_c05c71abee(F):return sparta_0f010a2798(A)
				login(A,F);K,L=qube_f629cfbf67.sparta_912c1df8b6();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_f629cfbf67.sparta_9d4e4e3477(A);B.update(qube_f629cfbf67.sparta_22f689eb97(A));B[_C]=qube_f629cfbf67.sparta_675e3127ca();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_c2bd655143());return render(A,'dist/project/auth/login.html',B)
def sparta_aa1b461b99(request):
	B='public@spartaqube.com';A=authenticate(username=B,password='public')
	if A:login(request,A)
	return redirect(_D)
@sparta_7190da8f89
def sparta_211443d8c9(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_851830bece.sparta_94e934342e()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_851830bece.sparta_8979b9f8df(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_851830bece.sparta_3cef5b388c(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_f629cfbf67.sparta_9d4e4e3477(A);C.update(qube_f629cfbf67.sparta_22f689eb97(A));C[_C]=qube_f629cfbf67.sparta_675e3127ca();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_c2bd655143());return render(A,'dist/project/auth/registration.html',C)
def sparta_2a23c213d3(request):A=request;B=qube_f629cfbf67.sparta_9d4e4e3477(A);B[_C]=qube_f629cfbf67.sparta_675e3127ca();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_b4ed356631(request,token):
	A=request;B=qube_851830bece.sparta_2b757f06ed(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_f629cfbf67.sparta_9d4e4e3477(A);D[_C]=qube_f629cfbf67.sparta_675e3127ca();return redirect(_I)
def sparta_adbda27c4a(request):logout(request);return redirect(_I)
def sparta_6fea87ec48(request):
	A=request
	if A.user.is_authenticated:
		if A.user.email=='cypress_tests@gmail.com':A.user.delete()
	logout(A);return redirect(_I)
def sparta_2d4f50bdc1(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_15ce6c4fd1(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_851830bece.sparta_15ce6c4fd1(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_f629cfbf67.sparta_9d4e4e3477(A);C.update(qube_f629cfbf67.sparta_22f689eb97(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_f629cfbf67.sparta_675e3127ca();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:print('exception ');print(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_f629cfbf67.sparta_9d4e4e3477(A);D.update(qube_f629cfbf67.sparta_22f689eb97(A));D[_C]=qube_f629cfbf67.sparta_675e3127ca();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_c2bd655143());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_2b4fe2e074(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_851830bece.sparta_2b4fe2e074(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_f629cfbf67.sparta_9d4e4e3477(D);A.update(qube_f629cfbf67.sparta_22f689eb97(D));A[_C]=qube_f629cfbf67.sparta_675e3127ca();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_c2bd655143());return render(D,_N,A)