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
import project.sparta_cc504a7958.sparta_154282b52b.qube_f629cfbf67 as qube_f629cfbf67
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_7190da8f89
from project.sparta_85717823e1.sparta_2d9e52fff7 import qube_96c9a18415 as qube_96c9a18415
@csrf_exempt
@sparta_7190da8f89
@login_required(redirect_field_name=_F)
def sparta_5597df2259(request):
	B=request;C=B.GET.get('edit')
	if C is _B:C='-1'
	A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=7;D=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(D);A[_D]=_A;A['edit_chart_id']=C;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_7190da8f89
@login_required(redirect_field_name=_F)
def sparta_2249496e60(request):
	A=request;C=A.GET.get('id');D=_G
	if C is _B:D=_A
	else:E=qube_96c9a18415.sparta_db9f806d6d(C,A.user);D=not E[_K]
	if D:return sparta_5597df2259(A)
	B=qube_f629cfbf67.sparta_9d4e4e3477(A);B[_C]=7;F=qube_f629cfbf67.sparta_992714c8af(A.user);B.update(F);B[_D]=_A;B[_H]=C;G=E[_E];B[_I]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_7190da8f89
def sparta_874db7e17b(request,id,api_token_id=_B):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	return sparta_56e11e496d(A,B)
@csrf_exempt
@sparta_7190da8f89
def sparta_e5fd405c33(request,widget_id,session_id,api_token_id):return sparta_56e11e496d(request,widget_id,session_id)
def sparta_56e11e496d(request,plot_chart_id,session='-1'):
	G='res';E=plot_chart_id;B=request;C=_G
	if E is _B:C=_A
	else:
		D=qube_96c9a18415.sparta_36993de8df(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_5597df2259(B)
	A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=7;I=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(I);A[_D]=_A;F=D[_E];A['b_require_password']=0 if D[G]==1 else 1;A[_H]=F.plot_chart_id;A[_I]=F.name;A[_J]=str(session);return render(B,'dist/project/plot-db/widgets.html',A)
@csrf_exempt
@sparta_7190da8f89
def sparta_a8e575962f(request,session_id,api_token_id):B=request;A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=7;C=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;return render(B,'dist/project/plot-db/plotGUI.html',A)
@csrf_exempt
@sparta_7190da8f89
@login_required(redirect_field_name=_F)
def sparta_fdba01ac0d(request):
	J=',\n    ';B=request;C=B.GET.get('id');F=_G
	if C is _B:F=_A
	else:G=qube_96c9a18415.sparta_db9f806d6d(C,B.user);F=not G[_K]
	if F:return sparta_5597df2259(B)
	K=qube_96c9a18415.sparta_c635cf83c4(G[_E]);D='';H=0
	for(E,I)in K.items():
		if H>0:D+=J
		if I==1:D+=f"{E}=input_{E}"
		else:L=str(J.join([f"input_{E}_{A}"for A in range(I)]));D+=f"{E}=[{L}]"
		H+=1
	M=f'Spartaqube().get_widget(\n    "{C}"\n)';N=f'Spartaqube().plot_(\n    "{C}",\n    {D}\n)';A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=7;O=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(O);A[_D]=_A;A[_H]=C;P=G[_E];A[_I]=P.name;A['plot_data_cmd']=M;A['plot_data_cmd_inputs']=N;return render(B,'dist/project/plot-db/plotGUISaved.html',A)
@csrf_exempt
@sparta_7190da8f89
def sparta_bd0f46e67b(request,session_id,api_token_id,json_vars_html):B=request;A=qube_f629cfbf67.sparta_9d4e4e3477(B);A[_C]=7;C=qube_f629cfbf67.sparta_992714c8af(B.user);A.update(C);A[_D]=_A;A[_J]=session_id;A.update(json.loads(json_vars_html));return render(B,'dist/project/plot-db/plotAPI.html',A)