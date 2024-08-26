from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_cc504a7958.sparta_154282b52b.qube_f629cfbf67 as qube_f629cfbf67
from project.models import UserProfile
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_7190da8f89
from project.sparta_eff1c30268.sparta_e7fbbb38af.qube_4f4d1453dc import sparta_c2bd655143
@sparta_7190da8f89
@login_required(redirect_field_name='login')
def sparta_ab08859fb3(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_f629cfbf67.sparta_9d4e4e3477(B);A.update(qube_f629cfbf67.sparta_992714c8af(B.user));A.update(F);G='';A['accessKey']=G;A.update(sparta_c2bd655143());return render(B,'dist/project/auth/settings.html',A)