from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 as qube_780496a161
from project.models import UserProfile
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_16b97658b3
from project.sparta_1187fa7ef2.sparta_5529e284ac.qube_86437ae694 import sparta_628782f3b7
@sparta_16b97658b3
@login_required(redirect_field_name='login')
def sparta_ab18cf651e(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_780496a161.sparta_9d84973003(B);A.update(qube_780496a161.sparta_c9380a8e8b(B.user));A.update(F);G='';A['accessKey']=G;A.update(sparta_628782f3b7());return render(B,'dist/project/auth/settings.html',A)