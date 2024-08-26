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
import project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 as qube_780496a161
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_16b97658b3
from project.sparta_b51bfafd7d.sparta_ba59edf337 import qube_eaa8b6f778 as qube_eaa8b6f778
from project.sparta_1019aaafa0.sparta_0cb64139f6 import qube_920506a7ea as qube_920506a7ea
from project.models import LoginLocation,UserProfile
def sparta_628782f3b7():return{'bHasCompanyEE':-1}
def sparta_9b873e5674(request):B=request;A=qube_780496a161.sparta_9d84973003(B);A[_C]=qube_780496a161.sparta_cd466d20aa();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_16b97658b3
def sparta_fd10b1290f(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_2c82df2593(C,A)
def sparta_1aa45b7ec4(request,redirectUrl):return sparta_2c82df2593(request,redirectUrl)
def sparta_2c82df2593(request,redirectUrl):
	E=redirectUrl;A=request;print('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_eaa8b6f778.sparta_17995c11cd(F):return sparta_9b873e5674(A)
				login(A,F);K,L=qube_780496a161.sparta_86799690df();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_780496a161.sparta_9d84973003(A);B.update(qube_780496a161.sparta_44c3df292c(A));B[_C]=qube_780496a161.sparta_cd466d20aa();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_628782f3b7());return render(A,'dist/project/auth/login.html',B)
def sparta_62f93d4c32(request):
	B='public@spartaqube.com';A=authenticate(username=B,password='public')
	if A:login(request,A)
	return redirect(_D)
@sparta_16b97658b3
def sparta_33a8ad4540(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_eaa8b6f778.sparta_cfd33c10de()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_eaa8b6f778.sparta_b234475650(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_eaa8b6f778.sparta_ef7f114302(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_780496a161.sparta_9d84973003(A);C.update(qube_780496a161.sparta_44c3df292c(A));C[_C]=qube_780496a161.sparta_cd466d20aa();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_628782f3b7());return render(A,'dist/project/auth/registration.html',C)
def sparta_090b60003e(request):A=request;B=qube_780496a161.sparta_9d84973003(A);B[_C]=qube_780496a161.sparta_cd466d20aa();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_69809956a2(request,token):
	A=request;B=qube_eaa8b6f778.sparta_03ba611ffa(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_780496a161.sparta_9d84973003(A);D[_C]=qube_780496a161.sparta_cd466d20aa();return redirect(_I)
def sparta_c8bd259c91(request):logout(request);return redirect(_I)
def sparta_7f14e54df7(request):
	A=request
	if A.user.is_authenticated:
		if A.user.email=='cypress_tests@gmail.com':A.user.delete()
	logout(A);return redirect(_I)
def sparta_807321d953(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_c705792e8f(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_eaa8b6f778.sparta_c705792e8f(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_780496a161.sparta_9d84973003(A);C.update(qube_780496a161.sparta_44c3df292c(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_780496a161.sparta_cd466d20aa();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:print('exception ');print(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_780496a161.sparta_9d84973003(A);D.update(qube_780496a161.sparta_44c3df292c(A));D[_C]=qube_780496a161.sparta_cd466d20aa();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_628782f3b7());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_7a0618ee8f(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_eaa8b6f778.sparta_7a0618ee8f(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_780496a161.sparta_9d84973003(D);A.update(qube_780496a161.sparta_44c3df292c(D));A[_C]=qube_780496a161.sparta_cd466d20aa();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_628782f3b7());return render(D,_N,A)