import json,base64,asyncio,subprocess,uuid,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_991c77bcde.sparta_f80cb4d5dd import qube_f83aea7c4c as qube_f83aea7c4c
from project.sparta_991c77bcde.sparta_ca58c8d226 import qube_82fcaeb071
from project.sparta_991c77bcde.sparta_8692553969 import qube_75d494717b as qube_75d494717b
from project.sparta_991c77bcde.sparta_ca58c8d226.qube_a7e266daae import Connector as Connector
def sparta_b1c192ba2b(json_data,user_obj):
	D='key';A=json_data;print('Call autocompelte api');print(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_d9e737ebde(B)
	return{'res':1,'output':C,D:B}
def sparta_d9e737ebde(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";C=requests.get(G)
	try:
		if int(C.status_code)==200:
			H=json.loads(C.text);D=H['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]