_M='An error occurred, please try again'
_L='password_confirmation'
_K='password'
_J='jsonData'
_I='api_token_id'
_H='Invalid captcha'
_G='notLoggerAPI'
_F='is_created'
_E='utf-8'
_D='errorMsg'
_C=False
_B=True
_A='res'
import hashlib,re,uuid,json,requests,socket,base64,traceback
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout,login
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings as conf_settings
from django.urls import reverse
from project.models import UserProfile,GuestCode,GuestCodeGlobal,LocalApp,SpartaQubeCode
from project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 import sparta_132f4604cb
from project.sparta_b51bfafd7d.sparta_845022d64d import qube_d1e2f8e426 as qube_d1e2f8e426
from project.sparta_b51bfafd7d.sparta_aabe63ca59 import qube_33b8e11397 as qube_33b8e11397
from project.sparta_b51bfafd7d.sparta_de1d0c11e1.qube_6fce6398ea import Email as Email
def sparta_16b97658b3(function):
	def A(request,*E,**C):
		A=request;B=_B
		if not A.user.is_active:B=_C;logout(A)
		if not A.user.is_authenticated:B=_C;logout(A)
		if not B:
			D=C.get(_I)
			if D is not None:F=qube_33b8e11397.sparta_0e91b5489b(D);login(A,F)
		return function(A,*E,**C)
	return A
def sparta_9990890d7c(function):
	def A(request,*B,**C):
		A=request
		if not A.user.is_active:return HttpResponseRedirect(reverse(_G))
		if A.user.is_authenticated:return function(A,*B,**C)
		else:return HttpResponseRedirect(reverse(_G))
	return A
def sparta_de148b6a40(function):
	def A(request,*B,**C):
		try:return function(request,*B,**C)
		except Exception as A:
			if conf_settings.DEBUG:print('Try catch exception with error:');print(A);print('traceback:');print(traceback.format_exc())
			D={_A:-1,_D:str(A)};E=json.dumps(D);return HttpResponse(E)
	return A
def sparta_ec317299c7(function):
	def A(request,*D,**E):
		A=request;B=_C
		try:
			F=json.loads(A.body);G=json.loads(F[_J]);H=G[_I];C=qube_33b8e11397.sparta_0e91b5489b(H)
			if C is not None:B=_B;A.user=C
		except Exception as I:print('exception pip auth');print(I)
		if B:return function(A,*D,**E)
		else:return HttpResponseRedirect(reverse(_G))
	return A
def sparta_4ab5af4462(code):
	try:
		B=SpartaQubeCode.objects.all()
		if B.count()==0:return code=='admin'
		else:C=B[0].spartaqube_code;A=hashlib.md5(code.encode(_E)).hexdigest();A=base64.b64encode(A.encode(_E));A=A.decode(_E);return A==C
	except Exception as D:pass
	return _C
def sparta_ad8a7340d0():
	A=LocalApp.objects.all()
	if A.count()==0:B=str(uuid.uuid4());LocalApp.objects.create(app_id=B,date_created=datetime.now());return B
	else:return A[0].app_id
def sparta_3e96f66e8b():A=socket.gethostname();B=socket.gethostbyname(A);return B
def sparta_cf0fa669be(json_data):
	D='ip_addr';A=json_data;del A[_K];del A[_L]
	try:A[D]=sparta_3e96f66e8b()
	except:A[D]=-1
	C=dict();C[_J]=json.dumps(A);B=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/create-user",data=json.dumps(C))
	if B.status_code==200:
		try:
			A=json.loads(B.text)
			if A[_A]==1:return{_A:1,_F:_B}
			else:A[_F]=_C;return A
		except Exception as E:return{_A:-1,_F:_C,_D:str(E)}
	return{_A:1,_F:_C,_D:f"status code: {B.status_code}. Please check your internet connection"}
def sparta_ef7f114302(json_data,hostname_url):
	P='emailExist';O='passwordConfirm';K='email';B=json_data;F={O:'The two passwords must be the same...',K:'Email address is not valid...','form':'The form you sent is not valid...',P:'This email is already registered...'};E=_C;Q=B['firstName'].capitalize();R=B['lastName'].capitalize();C=B[K].lower();L=B[_K];S=B[_L];T=B['code'];M=B['captcha'];B['app_id']=sparta_ad8a7340d0()
	if M=='cypress'and C=='cypress_tests@gmail.com':0
	else:
		U=sparta_132f4604cb(M)
		if U[_A]!=1:return{_A:-1,_D:_H}
	if not sparta_4ab5af4462(T):return{_A:-1,_D:'Invalid spartaqube code, please contact your administrator'}
	if L!=S:E=_B;G=F[O]
	if not re.match('[^@]+@[^@]+\\.[^@]+',C):E=_B;G=F[K]
	if User.objects.filter(username=C).exists():E=_B;G=F[P]
	if not E:
		V=sparta_cf0fa669be(B);N=_B;W=V[_F]
		if not W:N=_C
		A=User.objects.create_user(C,C,L);A.is_staff=_C;A.username=C;A.first_name=Q;A.last_name=R;A.is_active=_B;A.save();D=UserProfile(user=A);H=str(A.id)+'_'+str(A.email);H=H.encode(_E);I=hashlib.md5(H).hexdigest()+str(datetime.now());I=I.encode(_E);X=str(uuid.uuid4());D.user_profile_id=hashlib.sha256(I).hexdigest();D.email=C;D.api_key=str(uuid.uuid4());D.registration_token=X;D.b_created_website=N;D.save();J={_A:1,'userObj':A};return J
	J={_A:-1,_D:G};return J
def sparta_6c6fdc7035(user_obj,hostname_url,registration_token):C='Validate your account';B=user_obj;A=Email(B.username,[B.email],f"Welcome to {conf_settings.PROJECT_NAME}",C);A.addOneRow(C);A.addSpaceSeparator();A.addOneRow('Click on the link below to validate your account');D=f"{hostname_url.rstrip('/')}/registration-validation/{registration_token}";A.addOneCenteredButton('Validate',D);A.send()
def sparta_03ba611ffa(token):
	C=UserProfile.objects.filter(registration_token=token)
	if C.count()>0:A=C[0];A.registration_token='';A.is_account_validated=_B;A.save();B=A.user;B.is_active=_B;B.save();return{_A:1,'user':B}
	return{_A:-1,_D:'Invalid registration token'}
def sparta_cfd33c10de():return conf_settings.IS_GUEST_CODE_REQUIRED
def sparta_b234475650(guest_code):
	if GuestCodeGlobal.objects.filter(guest_id=guest_code,is_active=_B).count()>0:return _B
	return _C
def sparta_b3423ef571(guest_code,user_obj):
	D=user_obj;C=guest_code
	if GuestCodeGlobal.objects.filter(guest_id=C,is_active=_B).count()>0:return _B
	A=GuestCode.objects.filter(user=D)
	if A.count()>0:return _B
	else:
		A=GuestCode.objects.filter(guest_id=C,is_used=_C)
		if A.count()>0:B=A[0];B.user=D;B.is_used=_B;B.save();return _B
	return _C
def sparta_17995c11cd(user):
	A=UserProfile.objects.filter(user=user)
	if A.count()==1:return A[0].is_banned
	else:return _C
def sparta_c705792e8f(email,captcha):
	D=sparta_132f4604cb(captcha)
	if D[_A]!=1:return{_A:-1,_D:_H}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0];C=str(uuid.uuid4());A.token_reset_password=C;A.save();sparta_1e12ddc1d2(A.user,C);return{_A:1}
def sparta_1e12ddc1d2(user_obj,token_reset_password):B=user_obj;A=Email(B.username,[B.email],'Reset Password','Reset Password Message');A.addOneRow('Reset code','Copy the following code to reset your password');A.addSpaceSeparator();A.addOneRow(token_reset_password);A.send()
def sparta_7a0618ee8f(captcha,token,email,password):
	D=sparta_132f4604cb(captcha)
	if D[_A]!=1:return{_A:-1,_D:_H}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0]
	if not token==A.token_reset_password:return{_A:-1,_D:'Invalid token..., please try again'}
	A.token_reset_password='';A.save();C=A.user;C.set_password(password);C.save();return{_A:1}