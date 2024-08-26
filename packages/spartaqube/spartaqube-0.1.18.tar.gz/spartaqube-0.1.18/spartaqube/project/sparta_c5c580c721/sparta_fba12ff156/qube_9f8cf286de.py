from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_e47c1b14a9.sparta_cc215461ed.qube_b4ac0415ab as qube_b4ac0415ab
from project.models import UserProfile
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_c6659794ff
from project.sparta_c5c580c721.sparta_082db61041.qube_d6faa12141 import sparta_9a4500f844
@sparta_c6659794ff
@login_required(redirect_field_name='login')
def sparta_f98f778608(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A.update(qube_b4ac0415ab.sparta_af61424cdf(B.user));A.update(F);G='';A['accessKey']=G;A.update(sparta_9a4500f844());return render(B,'dist/project/auth/settings.html',A)