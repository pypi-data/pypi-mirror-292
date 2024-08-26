from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_16b97658b3
from project.sparta_b51bfafd7d.sparta_79921c2dcd import qube_0d1ce61c4b as qube_0d1ce61c4b
from project.models import UserProfile
import project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 as qube_780496a161
@sparta_16b97658b3
@login_required(redirect_field_name='login')
def sparta_8c63579113(request):
	E='avatarImg';B=request;A=qube_780496a161.sparta_9d84973003(B);A['menuBar']=-1;F=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_16b97658b3
@login_required(redirect_field_name='login')
def sparta_8578b584a7(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_8c63579113(A)