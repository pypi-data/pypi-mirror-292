import json,base64,asyncio,subprocess,uuid,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_85717823e1.sparta_7a3d84ff6e import qube_fc7cdf5312 as qube_fc7cdf5312
from project.sparta_85717823e1.sparta_f9f52bd441 import qube_35a872c584
from project.sparta_85717823e1.sparta_2d9e52fff7 import qube_b69aa2c416 as qube_b69aa2c416
from project.sparta_85717823e1.sparta_f9f52bd441.qube_d06e1c5b09 import Connector as Connector
def sparta_33b91a2eab(json_data,user_obj):
	D='key';A=json_data;print('Call autocompelte api');print(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_1f7037c584(B)
	return{'res':1,'output':C,D:B}
def sparta_1f7037c584(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";C=requests.get(G)
	try:
		if int(C.status_code)==200:
			H=json.loads(C.text);D=H['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]