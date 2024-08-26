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
import project.sparta_e47c1b14a9.sparta_cc215461ed.qube_b4ac0415ab as qube_b4ac0415ab
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_c6659794ff
from project.sparta_991c77bcde.sparta_23c481f08b import qube_fe08016699 as qube_fe08016699
from project.sparta_d649a81462.sparta_d38b1d8b5e import qube_0161219fc1 as qube_0161219fc1
from project.models import LoginLocation,UserProfile
def sparta_9a4500f844():return{'bHasCompanyEE':-1}
def sparta_e4bcd2fa9c(request):B=request;A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_c6659794ff
def sparta_e622582157(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_47f986538d(C,A)
def sparta_b0e689c428(request,redirectUrl):return sparta_47f986538d(request,redirectUrl)
def sparta_47f986538d(request,redirectUrl):
	E=redirectUrl;A=request;print('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_fe08016699.sparta_fe351475dd(F):return sparta_e4bcd2fa9c(A)
				login(A,F);K,L=qube_b4ac0415ab.sparta_6255337f9d();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_b4ac0415ab.sparta_d199ed9e6b(A);B.update(qube_b4ac0415ab.sparta_5e13f331d1(A));B[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_9a4500f844());return render(A,'dist/project/auth/login.html',B)
def sparta_e6851f14cb(request):
	B='public@spartaqube.com';A=authenticate(username=B,password='public')
	if A:login(request,A)
	return redirect(_D)
@sparta_c6659794ff
def sparta_aa7aa483ae(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_fe08016699.sparta_460701ffee()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_fe08016699.sparta_86596412a9(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_fe08016699.sparta_e2deb9a692(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_b4ac0415ab.sparta_d199ed9e6b(A);C.update(qube_b4ac0415ab.sparta_5e13f331d1(A));C[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_9a4500f844());return render(A,'dist/project/auth/registration.html',C)
def sparta_9cf5bebe5b(request):A=request;B=qube_b4ac0415ab.sparta_d199ed9e6b(A);B[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_134c167b36(request,token):
	A=request;B=qube_fe08016699.sparta_8fbc615b8e(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_b4ac0415ab.sparta_d199ed9e6b(A);D[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();return redirect(_I)
def sparta_a8ad7c2f23(request):logout(request);return redirect(_I)
def sparta_f1c9ae6616(request):
	A=request
	if A.user.is_authenticated:
		if A.user.email=='cypress_tests@gmail.com':A.user.delete()
	logout(A);return redirect(_I)
def sparta_0700f36637(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_7c6e5af1d4(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_fe08016699.sparta_7c6e5af1d4(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_b4ac0415ab.sparta_d199ed9e6b(A);C.update(qube_b4ac0415ab.sparta_5e13f331d1(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:print('exception ');print(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_b4ac0415ab.sparta_d199ed9e6b(A);D.update(qube_b4ac0415ab.sparta_5e13f331d1(A));D[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_9a4500f844());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_1dd886adfe(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_fe08016699.sparta_1dd886adfe(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_b4ac0415ab.sparta_d199ed9e6b(D);A.update(qube_b4ac0415ab.sparta_5e13f331d1(D));A[_C]=qube_b4ac0415ab.sparta_67cfc2b6a5();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_9a4500f844());return render(D,_N,A)