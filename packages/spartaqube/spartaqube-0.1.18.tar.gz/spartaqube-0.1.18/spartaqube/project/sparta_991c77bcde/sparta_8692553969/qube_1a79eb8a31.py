_AX='yAxisDataArr'
_AW='xAxisDataArr'
_AV='override_options'
_AU='notebook_variables'
_AT='type_plot'
_AS='chart_type'
_AR='code_editor_notebook_cells'
_AQ='chart_config'
_AP='chart_params'
_AO='plot_library'
_AN='has_write_rights'
_AM='chartConfigDict'
_AL='chartParams'
_AK='dataSourceArr'
_AJ='typeChart'
_AI='Name desc'
_AH='Date desc'
_AG='shadedBackgroundArr'
_AF='radiusBubbleArr'
_AE='labelsArr'
_AD='labels'
_AC='has_access'
_AB='column'
_AA='datasets'
_A9='Invalid password'
_A8='data_source_list'
_A7='date_created'
_A6='last_update'
_A5='is_static_data'
_A4='is_expose_widget'
_A3='bExposeAsWidget'
_A2='plotDes'
_A1='bStaticDataPlot'
_A0='codeEditorNotebookCells'
_z='split'
_y='query_filter'
_x='is_owner'
_w='is_public_widget'
_v='has_widget_password'
_u='bPublicWidget'
_t='plotName'
_s='widgetPassword'
_r='columns'
_q='input'
_p='bApplyFilter'
_o='trusted_connection'
_n='driver'
_m='lib_dir'
_l='organization'
_k='token'
_j='password'
_i='Recently used'
_h='You do not have access to this connector'
_g='py_code_processing'
_f='redis_db'
_e='socket_url'
_d='json_url'
_c='read_only'
_b='csv_delimiter'
_a='csv_path'
_Z='database_path'
_Y='library_arctic'
_X='keyspace'
_W='oracle_service_name'
_V='database'
_U='user'
_T='port'
_S='host'
_R='options'
_Q='type_chart'
_P='%Y-%m-%d'
_O='table_name'
_N='db_engine'
_M='plot_db_chart_obj'
_L='bWidgetPassword'
_K='description'
_J='name'
_I='dynamic_inputs'
_H='connector_id'
_G='plot_chart_id'
_F='errorMsg'
_E='data'
_D=False
_C=True
_B=None
_A='res'
import re,os,json,io,sys,base64,asyncio,subprocess,traceback,tinykernel,cloudpickle,uuid,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from django.utils.text import slugify
from django.core.cache import cache
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared,CodeEditorNotebook,NewPlotApiVariables
from project.models import ShareRights
from project.sparta_991c77bcde.sparta_f80cb4d5dd import qube_f83aea7c4c as qube_f83aea7c4c
from project.sparta_991c77bcde.sparta_ca58c8d226 import qube_82fcaeb071
from project.sparta_991c77bcde.sparta_8692553969 import qube_75d494717b as qube_75d494717b
from project.sparta_991c77bcde.sparta_ca58c8d226.qube_a7e266daae import Connector as Connector
from project.sparta_991c77bcde.sparta_3b03ddaeb5.qube_908d5bb7ea import sparta_564086d850,sparta_4d69bb5a40
from project.sparta_991c77bcde.sparta_8692553969 import qube_26ceb4d0cd as qube_26ceb4d0cd
from project.sparta_991c77bcde.sparta_3b03ddaeb5.qube_ec43c1cddb import sparta_cb3ac886ca
INPUTS_KEYS=['xAxisArr','yAxisArr',_AE,_AF,'rangesAxisArr','measuresAxisArr','markersAxisArr','ohlcvArr',_AG]
def sparta_bc48da31e8(user_obj):
	A=qube_f83aea7c4c.sparta_0306567289(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_b607c5dc2e(json_data,user_obj):
	D=user_obj;E=sparta_bc48da31e8(D)
	if len(E)>0:B=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=E,db_connector__is_delete=0)|Q(is_delete=0,user=D,db_connector__is_delete=0))
	else:B=DBConnectorUserShared.objects.filter(is_delete=0,user=D,db_connector__is_delete=0)
	F=[]
	if B.count()>0:
		C=json_data.get('orderBy',_i)
		if C==_i:B=B.order_by('-db_connector__last_date_used')
		elif C==_AH:B=B.order_by('-db_connector__last_update')
		elif C=='Date asc':B=B.order_by('db_connector__last_update')
		elif C==_AI:B=B.order_by('-db_connector__name')
		elif C=='Name asc':B=B.order_by('db_connector__name')
		elif C=='Type':B=B.order_by('db_connector__db_engine')
		for G in B:
			A=G.db_connector;H=[]
			try:H=json.loads(A.dynamic_inputs)
			except:pass
			F.append({_H:A.connector_id,_S:A.host,_T:A.port,_U:A.user,_V:A.database,_W:A.oracle_service_name,_X:A.keyspace,_Y:A.library_arctic,_Z:A.database_path,_a:A.csv_path,_b:A.csv_delimiter,_c:A.read_only,_d:A.json_url,_e:A.socket_url,_f:A.redis_db,_I:H,_g:A.py_code_processing,_N:A.db_engine,_J:A.name,_K:A.description,_x:G.is_owner})
	return{_A:1,'db_connectors':F}
def sparta_eace5fb8f8():return{_A:1,'available_engines':qube_82fcaeb071.sparta_eace5fb8f8()}
def sparta_89f9b9a072(json_data,user_obj):
	C=json_data[_H];A=DBConnector.objects.filter(connector_id=C,is_delete=_D).all()
	if A.count()>0:B=A[A.count()-1];D=datetime.now().astimezone(UTC);B.last_date_used=D;B.save()
	return{_A:1}
def sparta_8f023c27e6(json_data):
	A=json_data;print('test connection');print(A);B=''
	try:
		C=Connector(db_engine=A[_N]);C.init_with_params(host=A[_S],port=A[_T],user=A[_U],password=A[_j],database=A[_V],oracle_service_name=A[_W],csv_path=A[_a],csv_delimiter=A[_b],keyspace=A[_X],library_arctic=A[_Y],database_path=A[_Z],read_only=A[_c],json_url=A[_d],socket_url=A[_e],redis_db=A.get(_f,_B),token=A.get(_k,_B),organization=A.get(_l,_B),lib_dir=A.get(_m,_B),driver=A.get(_n,_B),trusted_connection=A.get(_o,_B),dynamic_inputs=A[_I],py_code_processing=A[_g]);D=C.test_connection()
		if not D:B=C.get_error_msg_test_connection()
	except Exception as E:D=_D;B=str(E)
	return{_A:1,'is_connector_working':D,_F:B}
def sparta_f2872c7e68(json_data):
	A=json_data;B=1;C='';D='';E=_B
	try:F=Connector(db_engine=A[_N]);F.init_with_params(host=A[_S],port=A[_T],user=A[_U],password=A[_j],database=A[_V],oracle_service_name=A[_W],csv_path=A[_a],csv_delimiter=A[_b],keyspace=A[_X],library_arctic=A[_Y],database_path=A[_Z],read_only=A[_c],json_url=A[_d],socket_url=A[_e],redis_db=A[_f],token=A.get(_k,''),organization=A.get(_l,''),lib_dir=A.get(_m,''),driver=A.get(_n,''),trusted_connection=A.get(_o,_C),dynamic_inputs=A[_I],py_code_processing=A[_g]);H,D=F.preview_output_connector();G=io.StringIO();sys.stdout=G;print(H);E=G.getvalue();sys.stdout=sys.__stdout__
	except Exception as I:C=str(I);B=-1
	return{_A:B,'preview_json':E,'print_buffer_content':D,_F:C}
def sparta_c965f6b458(json_data,user_obj):A=json_data;B=datetime.now().astimezone(UTC);C=str(uuid.uuid4());D=DBConnector.objects.create(connector_id=C,host=A[_S],port=A[_T],user=A[_U],password_e=qube_82fcaeb071.sparta_140fa69bb2(A[_j]),database=A[_V],oracle_service_name=A[_W],keyspace=A[_X],library_arctic=A[_Y],database_path=A[_Z],csv_path=A[_a],csv_delimiter=A[_b],read_only=A[_c],json_url=A[_d],socket_url=A[_e],redis_db=A[_f],token=A[_k],organization=A[_l],lib_dir=A[_m],driver=A[_n],trusted_connection=A[_o],dynamic_inputs=json.dumps(A[_I]),py_code_processing=A[_g],db_engine=A[_N],name=A[_J],description=A[_K],date_created=B,last_update=B,last_date_used=B);E=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=B);DBConnectorUserShared.objects.create(db_connector=D,user=user_obj,date_created=B,share_rights=E,is_owner=_C);return{_A:1}
def sparta_bdd0e863ad(json_data,user_obj):
	C=user_obj;B=json_data;print('update connector');print(B);I=B[_H];D=DBConnector.objects.filter(connector_id=I,is_delete=_D).all()
	if D.count()>0:
		A=D[D.count()-1];F=sparta_bc48da31e8(C)
		if len(F)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=F,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:
			J=E[0];G=J.share_rights
			if G.is_admin or G.has_write_rights:H=datetime.now().astimezone(UTC);A.host=B[_S];A.port=B[_T];A.user=B[_U];A.password_e=qube_82fcaeb071.sparta_140fa69bb2(B[_j]);A.database=B[_V];A.oracle_service_name=B[_W];A.keyspace=B[_X];A.library_arctic=B[_Y];A.database_path=B[_Z];A.csv_path=B[_a];A.csv_delimiter=B[_b];A.read_only=B[_c];A.json_url=B[_d];A.socket_url=B[_e];A.redis_db=B[_f];A.token=B.get(_k,'');A.organization=B.get(_l,'');A.lib_dir=B.get(_m,'');A.driver=B.get(_n,'');A.trusted_connection=B.get(_o,_C);A.dynamic_inputs=json.dumps(B[_I]);A.py_code_processing=B[_g];A.db_engine=B[_N];A.name=B[_J];A.description=B[_K];A.last_update=H;A.last_date_used=H;A.save()
	return{_A:1}
def sparta_915d61232b(json_data,user_obj):
	B=user_obj;F=json_data[_H];C=DBConnector.objects.filter(connector_id=F,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_bc48da31e8(B)
		if len(E)>0:D=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=E,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:D=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if D.count()>0:
			G=D[0];H=G.share_rights
			if H.is_admin:A.is_delete=_C;A.save()
	return{_A:1}
def sparta_60e4c54f5e(connector_id,user_obj):
	B=user_obj;C=DBConnector.objects.filter(connector_id__startswith=connector_id,is_delete=_D).all()
	if C.count()==1:
		A=C[0];D=sparta_bc48da31e8(B)
		if len(D)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=D,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:return A
def sparta_4827942eac(json_data,user_obj):
	C=json_data[_H];A=sparta_60e4c54f5e(C,user_obj)
	if A is _B:return{_A:-1,_F:_h}
	B=Connector(db_engine=A.db_engine);B.init_with_model(A);D=B.get_available_tables();return{_A:1,'tables_explorer':D}
def sparta_934127def5(json_data,user_obj):
	A=json_data;H=A[_H];C=A[_O];G=A[_p];D=[];E=sparta_60e4c54f5e(H,user_obj)
	if E is _B:return{_A:-1,_F:_h}
	B=Connector(db_engine=E.db_engine);B.init_with_model(E)
	if G:
		if G:
			I=A[_y]
			try:F=B.get_data_table_query(I,C)
			except Exception as J:print(traceback.format_exc());return{_A:-1,_F:str(J)}
		else:F=B.get_data_table(C)
		K=list(K.columns)
		for(L,M)in zip(F.columns,F.dtypes):N={_J:L,'type':str(M)};D.append(N)
	else:D=B.get_table_columns(C)
	return{_A:1,'table_columns':D}
def sparta_f4ad5e744a(json_data,db_connector_obj):
	C=db_connector_obj;B=json_data;D=B.get(_N,_B)
	if D is not _B:
		if D in['json_api','python','wss_api']:
			A=C.dynamic_inputs
			if A is not _B:
				try:A=json.loads(A)
				except:A=[]
			E=B.get(_I,[]);G=[A[_q]for A in A]
			for F in A:
				if F[_q]not in G:E.append(F)
			C.dynamic_inputs=json.dumps(E)
def sparta_9ba0dffc72(json_data,user_obj):
	A=json_data;G=A[_H];D=A.get(_O,_B);F=int(A.get(_p,'0'))==1;B=sparta_60e4c54f5e(G,user_obj)
	if B is _B:return{_A:-1,_F:_h}
	sparta_f4ad5e744a(A,B);C=Connector(db_engine=B.db_engine);C.init_with_model(B)
	if F:
		if F:
			H=A[_y]
			try:E=C.get_data_table_query(H,D)
			except Exception as I:print(traceback.format_exc());return{_A:-1,_F:str(I)}
		else:E=C.get_data_table(D)
	else:E=C.get_data_table(D)
	return{_A:1,_E:sparta_4d69bb5a40(E)}
def sparta_11324fd0d0(json_data,user_obj):
	A=json_data;G=A[_H];D=A.get(_O,'');F=A.get(_p,_D);K=A.get(_N,_B);B=sparta_60e4c54f5e(G,user_obj)
	if B is _B:return{_A:-1,_F:_h}
	sparta_f4ad5e744a(A,B);C=Connector(db_engine=B.db_engine);C.init_with_model(B)
	if F:
		if F:
			H=A[_y]
			try:E=C.get_data_table_query(H,D)
			except Exception as I:print(traceback.format_exc());return{_A:-1,_F:str(I)}
		else:E=C.get_data_table(D)
	else:E=C.get_data_table(D)
	J=E.describe();return{_A:1,_E:J.to_json(orient=_z)}
def sparta_4430997fd0(json_data,user_obj):
	C=json_data
	def E(df):A=df;return pd.DataFrame({_J:A.columns,'non-nulls':len(A)-A.isnull().sum().values,'nulls':A.isnull().sum().values,'type':A.dtypes.values})
	A=json.loads(C[_E]);F=int(C['mode']);D=pd.DataFrame(data=A[_E],columns=A[_r],index=A['index']);B=''
	if F==1:G=E(D);B=G.to_html()
	else:H=D.describe();B=H.to_html()
	return{_A:1,'table':B}
def sparta_95c0885e55(json_data,user_obj):
	A=json_data;print('json_data load_table_preview_explorer');print(A);D=A[_H];F=A.get(_O,_B);G=int(A.get(_p,'0'))==1;B=sparta_60e4c54f5e(D,user_obj)
	if B is _B:return{_A:-1,_F:_h}
	sparta_f4ad5e744a(A,B);C=Connector(db_engine=B.db_engine);C.init_with_model(B);E=C.get_db_connector().get_wss_structure();return{_A:1,_E:sparta_4d69bb5a40(E)}
def sparta_3749cfefa7(json_data,user_obj):
	A=json_data;J=A[_L];D=_B
	if J:D=A[_s];D=qube_75d494717b.sparta_b58b3bf5df(D)
	K=A[_A0];L=str(uuid.uuid4());B=datetime.now().astimezone(UTC);M=CodeEditorNotebook.objects.create(notebook_id=L,cells=K,date_created=B,last_update=B);E=str(uuid.uuid4());F=A[_A1];G=A['is_gui_plot']
	if G:F=_C
	C=A['plotSlug']
	if len(C)==0:C=A[_t]
	H=slugify(C);C=H;I=1
	while PlotDBChart.objects.filter(slug=C).exists():C=f"{H}-{I}";I+=1
	N=PlotDBChart.objects.create(plot_chart_id=E,type_chart=A[_AJ],name=A[_t],slug=C,description=A[_A2],is_expose_widget=A[_A3],is_public_widget=A[_u],is_static_data=F,has_widget_password=A[_L],widget_password_e=D,data_source_list=A[_AK],chart_params=A[_AL],chart_config=A[_AM],code_editor_notebook=M,is_created_from_api=G,date_created=B,last_update=B,last_date_used=B);O=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=B);PlotDBChartShared.objects.create(plot_db_chart=N,user=user_obj,share_rights=O,is_owner=_C,date_created=B);return{_A:1,_G:E}
def sparta_9a72254ca6(json_data,user_obj):
	E=user_obj;B=json_data;K=B[_G];F=PlotDBChart.objects.filter(plot_chart_id=K,is_delete=_D).all()
	if F.count()>0:
		A=F[F.count()-1];I=sparta_bc48da31e8(E)
		if len(I)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=I,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			L=G[0];J=L.share_rights
			if J.is_admin or J.has_write_rights:
				M=B[_L];C=_B
				if M:C=B[_s];C=qube_75d494717b.sparta_b58b3bf5df(C)
				H=datetime.now().astimezone(UTC);A.type_chart=B[_AJ];A.name=B[_t];A.description=B[_A2];A.is_expose_widget=B[_A3];A.is_static_data=B[_A1];A.has_widget_password=B[_L];A.is_public_widget=B[_u];A.widget_password_e=C;A.data_source_list=B[_AK];A.chart_params=B[_AL];A.chart_config=B[_AM];A.last_update=H;A.last_date_used=H;A.save();D=A.code_editor_notebook
				if D is not _B:D.cells=B[_A0];D.last_update=H;D.save()
	return{_A:1}
def sparta_b2e55e3029(json_data,user_obj):0
def sparta_42f9c7820f(json_data,user_obj):
	D=user_obj;F=sparta_bc48da31e8(D)
	if len(F)>0:A=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=F,plot_db_chart__is_delete=0,plot_db_chart=B)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0))
	else:A=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0)
	if A.count()>0:
		C=json_data.get('orderBy',_i)
		if C==_i:A=A.order_by('-plot_db_chart__last_date_used')
		elif C==_AH:A=A.order_by('-plot_db_chart__last_update')
		elif C=='Date asc':A=A.order_by('plot_db_chart__last_update')
		elif C==_AI:A=A.order_by('-plot_db_chart__name')
		elif C=='Name asc':A=A.order_by('plot_db_chart__name')
		elif C=='Type':A=A.order_by('plot_db_chart__type_chart')
	G=[]
	for E in A:
		B=E.plot_db_chart;J=E.share_rights;H=_B
		try:H=str(B.last_update.strftime(_P))
		except:pass
		I=_B
		try:I=str(B.date_created.strftime(_P))
		except Exception as K:print(K)
		G.append({_G:B.plot_chart_id,_Q:B.type_chart,_J:B.name,'slug':B.slug,_K:B.description,_A4:B.is_expose_widget,_A5:B.is_static_data,_v:B.has_widget_password,_w:B.is_public_widget,_x:E.is_owner,_AN:J.has_write_rights,_A6:H,_A7:I})
	return{_A:1,_AO:G}
def exec_notebook_and_get_workspace_variables(full_code,data_source_variables,workspace_variables):
	B=dict();A=tinykernel.TinyKernel()
	for(D,E)in data_source_variables.items():A.glb[D]=E
	A(full_code)
	for C in workspace_variables:B[C]=A(C)
	return B
def sparta_ea47184970(json_data,user_obj):
	Z='kernelVariableName';Y='isNotebook';X='password_widget';C=json_data;F=C[_G];M=_B
	if X in C:M=C[X]
	a=C.get('dataSourceListOverride',[]);G=PlotDBChart.objects.filter(plot_chart_id__startswith=F,is_delete=_D).all()
	if G.count()==1:
		A=G[G.count()-1];F=A.plot_chart_id
		if has_permission_widget_or_shared_rights(A,user_obj,password_widget=M):
			N=PlotDBChartShared.objects.filter(is_delete=0,plot_db_chart__is_delete=0,plot_db_chart=A)
			if N.count()>0:
				O=N[0];P=O.user;H=[];A=O.plot_db_chart;b=A.is_static_data
				if b:0
				else:
					for B in A.data_source_list:
						I=B[Y]
						if I:H.append(B[Z])
						else:
							if _I in B:
								c=B[_H];Q=sparta_60e4c54f5e(c,P);R=[]
								if Q.dynamic_inputs is not _B:
									try:R=json.loads(Q.dynamic_inputs)
									except:pass
								J=B[_I];d=[A[_q]for A in J]
								for S in R:
									e=S[_q]
									if e not in d:J.append(S)
								B[_I]=J
								for D in a:
									if D[_H]==B[_H]:
										if D[_O]==B[_O]:print("overridden_input_dict['dynamic_inputs']");print(D[_I]);B[_I]=D[_I]
							T=sparta_9ba0dffc72(B,P)
							if T[_A]==1:f=T[_E];B[_E]=f
				U=A.code_editor_notebook
				if U is not _B:E=U.cells
				else:E=_B
				if len(H)>0:
					if E is not _B:
						g='\n'.join([A['code']for A in json.loads(E)]);V=dict()
						for K in A.data_source_list:
							if K['isDataSource']:L=json.loads(K[_E]);V[K['table_name_workspace']]=pd.DataFrame(L[_E],index=L['index'],columns=L[_r])
						h=exec_notebook_and_get_workspace_variables(g,V,H)
						for B in A.data_source_list:
							I=B[Y]
							if I:W=B[Z];i=h[W];B[_E]=sparta_4d69bb5a40(sparta_564086d850(i,variable_name=W))
				def j(s):s=s.lower();A='-_.() %s%s'%(re.escape('/'),re.escape('\\'));B=re.sub('[^A-Za-z0-9%s]'%A,'_',s);return B
				return{_A:1,_G:F,_Q:A.type_chart,_J:A.name,'slug':A.slug,'name_file':j(A.name),_K:A.description,_A4:A.is_expose_widget,_A5:A.is_static_data,_v:A.has_widget_password,_w:A.is_public_widget,_A8:A.data_source_list,_AP:A.chart_params,_AQ:A.chart_config,_AR:E}
		else:return{_A:-1,_F:_A9}
	return{_A:-1,_F:'Unexpected error, please try again'}
def sparta_bec5fb1e68(json_data,user_obj):
	B=json_data;print('json_data');print(B);D=B[_G];A=PlotDBChart.objects.filter(plot_chart_id=D,is_delete=_D).all()
	if A.count()>0:C=A[A.count()-1];E=datetime.now().astimezone(UTC);C.last_date_used=E;C.save()
	return{_A:1}
def sparta_ecefc828d1(session_id):
	E=cache.get(session_id);B=dict()
	for(A,F)in E.items():
		C=cache.get(F)
		if C is not _B:
			D=cloudpickle.loads(C.encode('latin1'))
			if A==_R:B[A]=D
			else:B[A]=sparta_4d69bb5a40(sparta_564086d850(D,variable_name=A))
	return B
def sparta_109a112de5(session_id):A=sparta_ecefc828d1(session_id);B=sparta_cb3ac886ca(b_return_type_id=_C);C=json.loads(A[_AS])[_E][0][0];D=[A for A in B if A['ID']==C][0][_AT];return{_A:1,_AU:A,_AV:A.get(_R,dict()),_Q:D}
def sparta_c6b83c84ba(user_obj,session_id,widget_id):
	D=user_obj;C=_D;E=PlotDBChart.objects.filter(plot_chart_id__startswith=widget_id,is_delete=_D).all()
	if E.count()>0:
		A=E[E.count()-1]
		if A.is_expose_widget:
			if A.is_public_widget:C=_C
		if not C:
			G=sparta_bc48da31e8(D)
			if len(G)>0:H=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A))
			else:H=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A)
			if H.count()>0:C=_C
	if C:B=A.chart_params;B[_R]=json.loads(B[_R]);B[_AA]=json.loads(B[_E])[_AA];F=sparta_ecefc828d1(session_id);I=sparta_cb3ac886ca(b_return_type_id=_C);J=json.loads(F[_AS])[_E][0][0];K=[A for A in I if A['ID']==J][0][_AT];L=F.get(_R,dict());B[_R].update(L);return{_A:1,_AU:F,_AV:B,_Q:K}
	else:return{_A:-1,_F:'You do not have access to this template'}
def sparta_40f1456451(json_data,user_obj):
	X='is_index';R=json_data;K=user_obj;J='uuid'
	try:
		S=R[_G];Y=R['session_id'];L=PlotDBChart.objects.filter(plot_chart_id=S,is_delete=_D).all()
		if L.count()>0:
			A=L[L.count()-1];T=sparta_bc48da31e8(K)
			if len(T)>0:M=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=T,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=K,plot_db_chart__is_delete=0,plot_db_chart=A))
			else:M=PlotDBChartShared.objects.filter(is_delete=0,user=K,plot_db_chart__is_delete=0,plot_db_chart=A)
			if M.count()>0:
				Z=M[0];A=Z.plot_db_chart;U=NewPlotApiVariables.objects.filter(session_id=Y).all()
				if U.count()>0:
					a=U[0];b=a.pickled_variables;E=cloudpickle.loads(b.encode('latin1'));F=dict()
					for G in A.data_source_list:C=G[J];F[C]=pd.DataFrame()
					H=json.loads(A.chart_config)
					for B in H.keys():
						if B in INPUTS_KEYS:
							if B=='xAxis':
								N=H[B];C=N[J];O=N[X];P=N[_AB];D=F[C]
								if O:D.index=E[B]
								else:D[P]=E[B]
							elif H[B]is not _B:
								c=H[B]
								for(V,I)in enumerate(c):
									if I is not _B:
										C=I[J];O=I[X];P=I[_AB];D=F[C]
										if O:D.index=E[B][V]
										else:D[P]=E[B][V]
					for G in A.data_source_list:C=G[J];G[_E]=F[C].to_json(orient=_z)
				return{_A:1,_G:S,_Q:A.type_chart,_J:A.name,_K:A.description,_A4:A.is_expose_widget,_A5:A.is_static_data,_v:A.has_widget_password,_w:A.is_public_widget,_A8:A.data_source_list,_AP:A.chart_params,_AQ:A.chart_config,_AR:_B}
	except Exception as W:print('Error exception > '+str(W));return{_A:-1,_F:str(W)}
def sparta_3b3b4d1126(json_data,user_obj):
	A=user_obj;G=json_data[_G];B=PlotDBChart.objects.filter(plot_chart_id=G,is_delete=_D).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_bc48da31e8(A)
		if len(E)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart=C)|Q(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C)
		if D.count()>0:F=D[0];F.is_delete=_C;F.save()
	return{_A:1}
def has_permission_widget_or_shared_rights(plot_db_chart_obj,user_obj,password_widget=_B):
	B=user_obj;A=plot_db_chart_obj;F=A.has_widget_password;C=_D
	if B.is_authenticated:
		D=sparta_bc48da31e8(B)
		if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A)
		if E.count()>0:C=_C
	if C:return _C
	if A.is_expose_widget:
		if A.is_public_widget:
			if not F:return _C
			else:
				try:
					if qube_75d494717b.sparta_55637845d6(A.widget_password_e)==password_widget:return _C
					else:return _D
				except:return _D
		else:return _D
	return _D
def sparta_5fcccaf16b(plot_chart_id,user_obj,password_widget=_B):
	F=password_widget;E=plot_chart_id;C=user_obj;B=PlotDBChart.objects.filter(plot_chart_id__startswith=E,is_delete=_D).all();D=_D
	if B.count()==1:D=_C
	else:
		I=E;B=PlotDBChart.objects.filter(slug__startswith=I,is_delete=_D).all()
		if B.count()==1:D=_C
	if D:
		A=B[B.count()-1];J=A.has_widget_password
		if A.is_expose_widget:
			if A.is_public_widget:
				if not J:return{_A:1,_M:A}
				elif F is _B:return{_A:2,_F:'Require password',_M:A}
				else:
					try:
						if qube_75d494717b.sparta_b58b3bf5df(F)==A.widget_password_e:return{_A:1,_M:A}
						else:return{_A:3,_F:_A9,_M:A}
					except:return{_A:3,_F:_A9,_M:A}
			elif C.is_authenticated:
				G=sparta_bc48da31e8(C)
				if len(G)>0:H=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A))
				else:H=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A)
				if H.count()>0:return{_A:1,_M:A}
			else:return{_A:-1}
	return{_A:-1}
def sparta_cd7362c99e(plot_chart_id,user_obj):
	F=plot_chart_id;C=user_obj;A=PlotDBChart.objects.filter(plot_chart_id__startswith=F,is_delete=_D).all();D=_D
	if A.count()==1:D=_C
	else:
		H=F;A=PlotDBChart.objects.filter(slug__startswith=H,is_delete=_D).all()
		if A.count()==1:D=_C
	if D:
		B=A[A.count()-1];G=sparta_bc48da31e8(C)
		if len(G)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=B)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B))
		else:E=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B)
		if E.count()>0:I=E[0];B=I.plot_db_chart;return{_A:1,_AC:_C,_M:B}
	return{_A:1,_AC:_D}
def sparta_cfc538b122(plot_db_chart_obj):
	B=json.loads(plot_db_chart_obj.chart_config);C=dict();E={'xAxisArr':'x','yAxisArr':'y',_AF:'r',_AE:_AD,'ohlcvArr':'ohlcv',_AG:'shaded_background'}
	for A in B.keys():
		if A in INPUTS_KEYS:
			try:
				F=E[A]
				if B[A]is not _B:
					D=len([A for A in B[A]if A is not _B])
					if D>0:C[F]=D
			except Exception as G:print('Except input struct');print(G)
	return C
def sparta_5bec9854c0(json_data,user_obj):
	B=user_obj;D=sparta_bc48da31e8(B)
	if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	F=[]
	for C in E:
		A=C.plot_db_chart;I=C.share_rights;G=_B
		try:G=str(A.last_update.strftime(_P))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_P))
		except Exception as J:print(J)
		F.append({_G:A.plot_chart_id,_Q:A.type_chart,_v:A.has_widget_password,_w:A.is_public_widget,_J:A.name,'slug':A.slug,_K:A.description,_x:C.is_owner,_AN:I.has_write_rights,_A6:G,_A7:H})
	return{_A:1,_AO:F}
def sparta_f3d10f869e(json_data,user_obj):
	E=user_obj;B=json_data;K=B[_G];L=B['isCalledFromLibrary'];F=PlotDBChart.objects.filter(plot_chart_id=K,is_delete=_D).all()
	if F.count()>0:
		A=F[F.count()-1];H=sparta_bc48da31e8(E)
		if len(H)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=H,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			M=G[0];I=M.share_rights
			if I.is_admin or I.has_write_rights:
				N=B[_L];C=_B
				if N:C=B[_s];C=qube_75d494717b.sparta_b58b3bf5df(C)
				J=datetime.now().astimezone(UTC);A.has_widget_password=B[_L];A.widget_password_e=C;A.name=B[_t];A.plotDes=B[_A2];A.is_expose_widget=B[_A3];A.is_public_widget=B[_u];A.is_static_data=B[_A1];A.last_update=J;A.save()
				if L:0
				else:
					D=A.code_editor_notebook
					if D is not _B:D.cells=B[_A0];D.last_update=J;D.save()
	return{_A:1}
def sparta_db1e0dfe52(json_data,user_obj):
	D=user_obj;B=json_data;I=B[_G];E=PlotDBChart.objects.filter(plot_chart_id=I,is_delete=_D).all()
	if E.count()>0:
		A=E[E.count()-1];G=sparta_bc48da31e8(D)
		if len(G)>0:F=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:F=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A)
		if F.count()>0:
			J=F[0];H=J.share_rights
			if H.is_admin or H.has_write_rights:
				K=B[_L];C=_B
				if K:C=B[_s];C=qube_75d494717b.sparta_b58b3bf5df(C)
				L=datetime.now().astimezone(UTC);A.has_widget_password=B[_L];A.is_public_widget=B[_u];A.widget_password_e=C;A.last_update=L;A.save()
	return{_A:1}
def sparta_6f2cfee095(json_data,user_obj):
	B=user_obj;G=json_data[_G];C=PlotDBChart.objects.filter(plot_chart_id=G,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_bc48da31e8(B)
		if len(E)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A)
		if D.count()>0:
			H=D[0];F=H.share_rights
			if F.is_admin or F.has_write_rights:I=datetime.now().astimezone(UTC);A.is_expose_widget=_D;A.last_update=I;A.save()
	return{_A:1}
def sparta_90beea6bba(user_obj):
	B=user_obj;C=sparta_bc48da31e8(B)
	if len(C)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=C,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	E=[]
	for F in D:
		A=F.plot_db_chart;J=F.share_rights;G=_B
		try:G=str(A.last_update.strftime(_P))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_P))
		except Exception as I:print(I)
		E.append({'id':A.plot_chart_id,_J:A.name,_K:A.description,_A6:G,_A7:H})
	return E
def sparta_42cc518382(json_data,user_obj):
	B=user_obj;A=json_data;C=sparta_cd7362c99e(A['widget_id'],B);D=C[_AC]
	if D:E=C[_M];A[_G]=E.plot_chart_id;F=sparta_ea47184970(A,B);return{_A:1,_E:[A[_E]for A in F[_A8]]}
	return{_A:-1}
def sparta_7cf9f449fe(json_data,user_obj):
	B='Error quantstats';A=json_data;C=A['service']
	if C=='quantstats':
		try:return qube_26ceb4d0cd.sparta_7439868dfa(A,user_obj)
		except Exception as D:print(B);print(traceback.format_exc());print(B);return{_A:-1,_F:str(D)}
	return{_A:1}
def sparta_12daf230c3(json_data,user_obj):
	B=json_data;import quantstats as K;B=B[_E];G=B[_AW];L=B[_AX];H=B['columnsX'];I=B[_r];F=L;C=I
	if len(H)>1:C=H[1:]+I;F=G[1:]+F
	A=pd.DataFrame(F).T;A.index=pd.to_datetime(G[0]);A.columns=C
	try:A.index=A.index.tz_localize('UTC')
	except:pass
	for E in C:
		try:A[E]=A[E].astype(float)
		except:pass
	M=A.pct_change();D=pd.DataFrame()
	for(N,E)in enumerate(C):
		J=K.reports.metrics(M[E],mode='basic',display=_D)
		if N==0:D=J
		else:D=pd.concat([D,J],axis=1)
	D.columns=C;return{_A:1,'metrics':D.to_json(orient=_z)}
def sparta_f24cb35354(json_data,user_obj):
	N='Salary';A=json_data;A=A[_E];O=A[_AW];P=A[_AX];G=A['columnsX'];H=A[_r];C=P;I=H
	if len(G)>1:I=G+H;C=O+C
	D=pd.DataFrame(C).T;D.columns=I;E=['Country','City'];J=[N,'Rent'];J=[N];D.set_index(E,inplace=_C);B=D.groupby(E).mean();print('res_group_by_df');print(B);Q=E;F=len(B.index[0]);K=sorted(list(set(B.index.get_level_values(F-2))));L=[]
	def M(this_df,level=0,previous_index_list=_B):
		D=previous_index_list;C=this_df;A=level
		if A==F-1:
			for H in J:L.append({_E:[0]*len(K),_E:C[H].tolist(),_AD:list(C.index.get_level_values(A)),'hierarchy':D,_AB:H,'label':D[-1]})
		elif A<F-1:
			I=sorted(list(set(B.index.get_level_values(A))))
			for E in I:
				if D is _B:G=[E]
				else:G=D.copy();G.append(E)
				M(C[C.index.get_level_values(A)==E],A+1,G)
	M(B);print('chart_data');return{_A:1,_AA:L,_AD:K}