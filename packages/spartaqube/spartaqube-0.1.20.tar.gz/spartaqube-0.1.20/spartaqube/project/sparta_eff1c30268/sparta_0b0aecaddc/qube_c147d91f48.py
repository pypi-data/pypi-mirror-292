from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_7190da8f89
from project.sparta_85717823e1.sparta_c6d7d469cb import qube_02002e0b09 as qube_02002e0b09
from project.models import UserProfile
import project.sparta_cc504a7958.sparta_154282b52b.qube_f629cfbf67 as qube_f629cfbf67
@sparta_7190da8f89
@login_required(redirect_field_name='login')
def sparta_57be02ba1c(request):
	E='avatarImg';B=request;A=qube_f629cfbf67.sparta_9d4e4e3477(B);A['menuBar']=-1;F=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_7190da8f89
@login_required(redirect_field_name='login')
def sparta_36d04d0592(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_57be02ba1c(A)