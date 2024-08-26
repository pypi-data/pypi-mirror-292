import pandas as pd,clickhouse_connect
from project.sparta_85717823e1.sparta_f9f52bd441.qube_f5c68a0e9e import EngineBuilder
from project.sparta_85717823e1.sparta_c648d09df3.qube_f514117b98 import sparta_9d9c760226
class ClickhouseConnector(EngineBuilder):
	def __init__(A,host,port,database,user='default',password=''):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='clickhouse');A.connector=A.build_clickhouse()
	def test_connection(A):
		C=False
		try:
			B=clickhouse_connect.get_client(host=A.host,port=A.port,user=A.user,password=A.password,database=A.database);D=f"SELECT name FROM system.databases WHERE name = '{A.database}'";E=B.query(D)
			if E.result_rows:C=True
			else:A.error_msg_test_connection='Invalid database'
		except Exception as F:A.error_msg_test_connection=str(F)
		finally:
			if B:B.close()
		return C
	def get_available_tables(A):
		B=[]
		try:C=A.connector;D=f"SHOW TABLES FROM {A.database}";E=C.query(D);B=[A[0]for A in E.result_rows]
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_table_columns(A,table_name):
		B=[]
		try:C=A.connector;D=f"\n                SELECT name, type FROM system.columns \n                WHERE database = '{A.database}' AND table = '{table_name}'\n                ";E=C.query(D);B=[A[1]for A in E.result_rows]
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_data_table(E,table_name):
		try:
			A=E.connector;C=f"SELECT * FROM {table_name}";B=A.query(C);D=B.result_columns;B=A.query(C);D=B.column_names;F=B.result_rows;G=sparta_9d9c760226(pd.DataFrame(F,columns=D))
			if A:A.close()
			return G
		except Exception as H:
			if A:A.close()
			raise Exception(H)
	def get_data_table_query(E,sql,table_name=None):
		try:
			A=E.connector;C=sql;B=A.query(C);D=B.result_columns;B=A.query(C);D=B.column_names;F=B.result_rows;G=sparta_9d9c760226(pd.DataFrame(F,columns=D))
			if A:A.close()
			return G
		except Exception as H:
			if A:A.close()
			raise Exception(H)