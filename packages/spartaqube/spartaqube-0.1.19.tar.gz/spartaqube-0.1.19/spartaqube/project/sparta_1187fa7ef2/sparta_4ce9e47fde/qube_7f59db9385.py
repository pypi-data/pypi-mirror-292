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
import project.sparta_f25721a1fe.sparta_f8f3ec6af7.qube_780496a161 as qube_780496a161
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_16b97658b3
from project.sparta_b51bfafd7d.sparta_b1d0c97516 import qube_ec6dbe572c as qube_ec6dbe572c
@csrf_exempt
@sparta_16b97658b3
@login_required(redirect_field_name=_F)
def sparta_dd8f7fd881(request):
	B=request;C=B.GET.get('edit')
	if C is _B:C='-1'
	A=qube_780496a161.sparta_9d84973003(B);A[_C]=7;D=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(D);A[_D]=_A;A['edit_chart_id']=C;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_16b97658b3
@login_required(redirect_field_name=_F)
def sparta_1c7b7fa3d6(request):
	A=request;C=A.GET.get('id');D=_G
	if C is _B:D=_A
	else:E=qube_ec6dbe572c.sparta_fde8f47e5c(C,A.user);D=not E[_K]
	if D:return sparta_dd8f7fd881(A)
	B=qube_780496a161.sparta_9d84973003(A);B[_C]=7;F=qube_780496a161.sparta_c9380a8e8b(A.user);B.update(F);B[_D]=_A;B[_H]=C;G=E[_E];B[_I]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_16b97658b3
def sparta_1196984cfa(request,id,api_token_id=_B):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	return sparta_80ee2bb245(A,B)
@csrf_exempt
@sparta_16b97658b3
def sparta_6409b22226(request,widget_id,session_id,api_token_id):return sparta_80ee2bb245(request,widget_id,session_id)
def sparta_80ee2bb245(request,plot_chart_id,session='-1'):
	G='res';E=plot_chart_id;B=request;C=_G
	if E is _B:C=_A
	else:
		D=qube_ec6dbe572c.sparta_2c9d62109d(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_dd8f7fd881(B)
	A=qube_780496a161.sparta_9d84973003(B);A[_C]=7;I=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(I);A[_D]=_A;F=D[_E];A['b_require_password']=0 if D[G]==1 else 1;A[_H]=F.plot_chart_id;A[_I]=F.name;A[_J]=str(session);return render(B,'dist/project/plot-db/widgets.html',A)
@csrf_exempt
@sparta_16b97658b3
def sparta_4bcf5d2184(request,session_id,api_token_id):B=request;A=qube_780496a161.sparta_9d84973003(B);A[_C]=7;C=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;return render(B,'dist/project/plot-db/plotGUI.html',A)
@csrf_exempt
@sparta_16b97658b3
@login_required(redirect_field_name=_F)
def sparta_b20758ce19(request):
	J=',\n    ';B=request;C=B.GET.get('id');F=_G
	if C is _B:F=_A
	else:G=qube_ec6dbe572c.sparta_fde8f47e5c(C,B.user);F=not G[_K]
	if F:return sparta_dd8f7fd881(B)
	K=qube_ec6dbe572c.sparta_b41fa7b98b(G[_E]);D='';H=0
	for(E,I)in K.items():
		if H>0:D+=J
		if I==1:D+=f"{E}=input_{E}"
		else:L=str(J.join([f"input_{E}_{A}"for A in range(I)]));D+=f"{E}=[{L}]"
		H+=1
	M=f'Spartaqube().get_widget(\n    "{C}"\n)';N=f'Spartaqube().plot_(\n    "{C}",\n    {D}\n)';A=qube_780496a161.sparta_9d84973003(B);A[_C]=7;O=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(O);A[_D]=_A;A[_H]=C;P=G[_E];A[_I]=P.name;A['plot_data_cmd']=M;A['plot_data_cmd_inputs']=N;return render(B,'dist/project/plot-db/plotGUISaved.html',A)
@csrf_exempt
@sparta_16b97658b3
def sparta_9fb8878d11(request,session_id,api_token_id,json_vars_html):B=request;A=qube_780496a161.sparta_9d84973003(B);A[_C]=7;C=qube_780496a161.sparta_c9380a8e8b(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;A.update(json.loads(json_vars_html));return render(B,'dist/project/plot-db/plotAPI.html',A)