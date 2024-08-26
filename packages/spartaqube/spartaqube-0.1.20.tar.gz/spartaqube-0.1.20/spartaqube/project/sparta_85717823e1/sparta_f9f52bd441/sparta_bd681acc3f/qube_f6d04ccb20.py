_C='columns'
_B='dataset'
_A='query'
import time,requests,pandas as pd
from requests.auth import HTTPBasicAuth
from questdb.ingress import Sender,IngressError,TimestampNanos
from project.sparta_85717823e1.sparta_f9f52bd441.qube_f5c68a0e9e import EngineBuilder
from project.sparta_85717823e1.sparta_c648d09df3.qube_f514117b98 import sparta_9d9c760226
class QuestDBConnector(EngineBuilder):
	def __init__(B,host,port,user,password,database):
		A=host
		if A.startswith('localhost'):A='http://localhost'
		super().__init__(host=A,port=port,user=user,password=password,database=database,engine_name='questdb');B.conf=B.build_questdb()
	def test_connection(A):
		try:
			with Sender.from_conf(A.conf)as B:B.flush()
			return True
		except IngressError as C:A.error_msg_test_connection=str(C);return False
	def get_available_tables(A):
		C=f"{A.host}:{A.port}/exec";D='SHOW TABLES'
		try:B=requests.get(C,params={_A:D},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();E=B.json();F=[A[0]for A in E[_B]];return sorted(F)
		except requests.RequestException as G:A.error_msg_test_connection=str(G);return[]
	def get_table_columns(A,table_name):
		C=f"{A.host}:{A.port}/exec";D=f"SHOW COLUMNS FROM {table_name}"
		try:B=requests.get(C,params={_A:D},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();E=B.json();F=[A['table']for A in E[_B]];return F
		except requests.RequestException as G:A.error_msg_test_connection=str(G);return[]
	def get_data_table(A,table_name):E=f"{A.host}:{A.port}/exec";F=f"SELECT * FROM {table_name}";B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();C=B.json();G=[A['name']for A in C[_C]];D=sparta_9d9c760226(C[_B]);D.columns=G;return D
	def get_data_table_query(A,sql,table_name=None):E=f"{A.host}:{A.port}/exec";F=sql;B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();C=B.json();G=[A['name']for A in C[_C]];D=sparta_9d9c760226(C[_B]);D.columns=G;return D