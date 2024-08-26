import json,base64,asyncio,subprocess,uuid,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_b51bfafd7d.sparta_8e98a7e274 import qube_5b0b590e98 as qube_5b0b590e98
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc import qube_f1bd2a17cc
from project.sparta_b51bfafd7d.sparta_b1d0c97516 import qube_6640f264c5 as qube_6640f264c5
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.qube_08082681c1 import Connector as Connector
def sparta_7ec808968e(json_data,user_obj):
	D='key';A=json_data;print('Call autocompelte api');print(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_122200e41d(B)
	return{'res':1,'output':C,D:B}
def sparta_122200e41d(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";C=requests.get(G)
	try:
		if int(C.status_code)==200:
			H=json.loads(C.text);D=H['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]