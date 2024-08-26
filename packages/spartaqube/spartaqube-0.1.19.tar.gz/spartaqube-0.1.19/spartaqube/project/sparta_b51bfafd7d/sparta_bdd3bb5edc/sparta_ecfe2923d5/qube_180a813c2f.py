_C='columns'
_B='dataset'
_A='query'
import time,requests,pandas as pd
from requests.auth import HTTPBasicAuth
from questdb.ingress import Sender,IngressError,TimestampNanos
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.qube_e41187c546 import EngineBuilder
from project.sparta_b51bfafd7d.sparta_b3fc7394e9.qube_7a8ddad505 import sparta_a7bc85aeac
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
	def get_data_table(A,table_name):E=f"{A.host}:{A.port}/exec";F=f"SELECT * FROM {table_name}";B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();C=B.json();G=[A['name']for A in C[_C]];D=sparta_a7bc85aeac(C[_B]);D.columns=G;return D
	def get_data_table_query(A,sql,table_name=None):E=f"{A.host}:{A.port}/exec";F=sql;B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password));B.raise_for_status();C=B.json();G=[A['name']for A in C[_C]];D=sparta_a7bc85aeac(C[_B]);D.columns=G;return D