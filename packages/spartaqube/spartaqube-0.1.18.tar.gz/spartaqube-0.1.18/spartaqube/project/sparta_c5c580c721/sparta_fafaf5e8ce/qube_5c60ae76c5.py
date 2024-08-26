_K='has_access'
_J='session'
_I='plot_name'
_H='plot_chart_id'
_G=False
_F='login'
_E='plot_db_chart_obj'
_D='bCodeMirror'
_C='menuBar'
_B=None
_A=True
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_e47c1b14a9.sparta_cc215461ed.qube_b4ac0415ab as qube_b4ac0415ab
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_c6659794ff
from project.sparta_991c77bcde.sparta_8692553969 import qube_1a79eb8a31 as qube_1a79eb8a31
@csrf_exempt
@sparta_c6659794ff
@login_required(redirect_field_name=_F)
def sparta_1c46f0b049(request):
	B=request;C=B.GET.get('edit')
	if C is _B:C='-1'
	A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=7;D=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(D);A[_D]=_A;A['edit_chart_id']=C;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_c6659794ff
@login_required(redirect_field_name=_F)
def sparta_4316fa410f(request):
	A=request;C=A.GET.get('id');D=_G
	if C is _B:D=_A
	else:E=qube_1a79eb8a31.sparta_cd7362c99e(C,A.user);D=not E[_K]
	if D:return sparta_1c46f0b049(A)
	B=qube_b4ac0415ab.sparta_d199ed9e6b(A);B[_C]=7;F=qube_b4ac0415ab.sparta_af61424cdf(A.user);B.update(F);B[_D]=_A;B[_H]=C;G=E[_E];B[_I]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_c6659794ff
def sparta_b423cef839(request,id,api_token_id=_B):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	return sparta_f25b077c9e(A,B)
@csrf_exempt
@sparta_c6659794ff
def sparta_b2b2f0c429(request,widget_id,session_id,api_token_id):return sparta_f25b077c9e(request,widget_id,session_id)
def sparta_f25b077c9e(request,plot_chart_id,session='-1'):
	G='res';E=plot_chart_id;B=request;C=_G
	if E is _B:C=_A
	else:
		D=qube_1a79eb8a31.sparta_5fcccaf16b(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_1c46f0b049(B)
	A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=7;I=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(I);A[_D]=_A;F=D[_E];A['b_require_password']=0 if D[G]==1 else 1;A[_H]=F.plot_chart_id;A[_I]=F.name;A[_J]=str(session);return render(B,'dist/project/plot-db/widgets.html',A)
@csrf_exempt
@sparta_c6659794ff
def sparta_53f587f654(request,session_id,api_token_id):B=request;A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=7;C=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;return render(B,'dist/project/plot-db/plotGUI.html',A)
@csrf_exempt
@sparta_c6659794ff
@login_required(redirect_field_name=_F)
def sparta_d5c6feca59(request):
	J=',\n    ';B=request;C=B.GET.get('id');F=_G
	if C is _B:F=_A
	else:G=qube_1a79eb8a31.sparta_cd7362c99e(C,B.user);F=not G[_K]
	if F:return sparta_1c46f0b049(B)
	K=qube_1a79eb8a31.sparta_cfc538b122(G[_E]);D='';H=0
	for(E,I)in K.items():
		if H>0:D+=J
		if I==1:D+=f"{E}=input_{E}"
		else:L=str(J.join([f"input_{E}_{A}"for A in range(I)]));D+=f"{E}=[{L}]"
		H+=1
	M=f'Spartaqube().get_widget(\n    "{C}"\n)';N=f'Spartaqube().plot_(\n    "{C}",\n    {D}\n)';A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=7;O=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(O);A[_D]=_A;A[_H]=C;P=G[_E];A[_I]=P.name;A['plot_data_cmd']=M;A['plot_data_cmd_inputs']=N;return render(B,'dist/project/plot-db/plotGUISaved.html',A)
@csrf_exempt
@sparta_c6659794ff
def sparta_542becddb0(request,session_id,api_token_id,json_vars_html):B=request;A=qube_b4ac0415ab.sparta_d199ed9e6b(B);A[_C]=7;C=qube_b4ac0415ab.sparta_af61424cdf(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;A.update(json.loads(json_vars_html));return render(B,'dist/project/plot-db/plotAPI.html',A)