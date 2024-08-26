from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_c6659794ff
from project.sparta_991c77bcde.sparta_a9c56d094f import qube_600b1b082c as qube_600b1b082c
from project.models import UserProfile
import project.sparta_e47c1b14a9.sparta_cc215461ed.qube_b4ac0415ab as qube_b4ac0415ab
@sparta_c6659794ff
@login_required(redirect_field_name='login')
def sparta_c7b3159e5f(request):
	E='avatarImg';B=request;A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A['menuBar']=-1;F=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_c6659794ff
@login_required(redirect_field_name='login')
def sparta_aebc7fabfa(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_c7b3159e5f(A)