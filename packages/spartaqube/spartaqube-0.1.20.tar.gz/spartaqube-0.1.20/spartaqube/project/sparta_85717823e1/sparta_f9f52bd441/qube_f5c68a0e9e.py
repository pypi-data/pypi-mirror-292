_B=':memory:'
_A=None
import os,time,pandas as pd,psycopg2,mysql.connector,pyodbc,cx_Oracle,redis,duckdb,sqlite3,couchdb,aerospike,arcticdb as adb,clickhouse_connect
from pymongo import MongoClient
from questdb.ingress import Sender,IngressError
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from influxdb_client import InfluxDBClient
from sqlalchemy import create_engine,MetaData,Table,select,inspect,text
from multiprocessing import Pool
class EngineBuilder:
	def __init__(A,host,port,user=_A,password=_A,database=_A,engine_name='postgresql'):C=database;B=password;A.host=host;A.port=port;A.user=user;A.password=B;A.database=C;A.url_engine=f"{engine_name}://{user}:{B}@{host}:{port}/{C}";A.error_msg_test_connection=''
	def get_error_msg_test_connection(A):return A.error_msg_test_connection
	def set_url_engine(A,url_engine):A.url_engine=url_engine
	def set_database(A,database):A.database=database
	def set_file_path(A,file_path):A.file_path=file_path
	def set_keyspace_cassandra(A,keyspace_cassandra):A.keyspace_cassandra=keyspace_cassandra
	def set_redis_db(A,redis_db):A.redis_db=redis_db
	def set_database_path(A,database_path):A.database_path=database_path
	def set_socket_url(A,socket_url):A.socket_url=socket_url
	def set_json_url(A,json_url):A.json_url=json_url
	def set_dynamic_inputs(A,dynamic_inputs):A.dynamic_inputs=dynamic_inputs
	def set_py_code_processing(A,py_code_processing):A.py_code_processing=py_code_processing
	def set_library_arctic(A,database_path,library_arctic):A.database_path=database_path;A.library_arctic=library_arctic
	def build_postgres(A):B=psycopg2.connect(user=A.user,password=A.password,host=A.host,port=A.port,database=A.database);return B
	def build_mysql(A):B=mysql.connector.connect(host=A.host,user=A.user,passwd=A.password,port=A.port,database=A.database);return B
	def build_mariadb(A):print(A.host);print(A.user);print(A.password);print(A.port);print(A.database);B=mysql.connector.connect(host=A.host,user=A.user,passwd=A.password,port=A.port,database=A.database);return B
	def build_mssql(A,trusted_connection,driver):
		B=driver
		if trusted_connection:C=pyodbc.connect(f"DRIVER={B};SERVER={A.host},{A.port};DATABASE={A.database};Trusted_Connection=yes")
		else:C=pyodbc.connect(f"DRIVER={B};SERVER={A.host},{A.port};DATABASE={A.database};UID={A.user};PWD={A.password}")
		return C
	def build_oracle(A,lib_dir=_A,oracle_service_name='orcl'):
		B=lib_dir
		if B is not _A:
			try:cx_Oracle.init_oracle_client(lib_dir=B)
			except:pass
		C=cx_Oracle.makedsn(A.host,A.port,service_name=oracle_service_name);D=cx_Oracle.connect(user=A.user,password=A.password,dsn=C,mode=cx_Oracle.SYSDBA);return D
	def build_arctic(B,database_path,library_arctic):
		A=database_path;B.set_library_arctic(A,library_arctic)
		if A is not _A:
			if len(A)>0:print('database_path > '+str(A));C=adb.Arctic(A);return C
	def build_cassandra(A,keyspace):A.set_keyspace_cassandra(keyspace);B=[A.host];C=PlainTextAuthProvider(username=A.user,password=A.password)if A.user and A.password else _A;D=Cluster(contact_points=B,port=A.port,auth_provider=C);return D
	def build_scylladb(A,keyspace):return A.build_cassandra(keyspace)
	def build_clickhouse(A):
		try:B=clickhouse_connect.get_client(host=A.host,port=A.port,user=A.user,password=A.password,database=A.database);return B
		except:pass
	def build_couchdb(A):
		try:C=f"{A.host}:{A.port}";B=couchdb.Server(C);B.resource.credentials=A.user,A.password;return B
		except:return
	def build_aerospike(A):
		B={'hosts':[(A.host,A.port)]}
		if A.user and A.password:
			if len(A.user)>0:B['user']=A.user
			if len(A.password)>0:B['password']=A.password
		try:C=aerospike.client(B).connect();return C
		except:pass
	def build_redis(A,db=0):A.set_redis_db(db);B=redis.StrictRedis(host=A.host,port=A.port,password=A.password,username=A.user,db=db);return B
	def build_duckdb(B,database_path,read_only=False):
		A=database_path
		if A is _A:return
		if not os.path.exists(A)and A!=_B:return
		B.set_database_path(A);C=duckdb.connect(A,read_only=read_only);return C
	def build_parquet(B,database_path,read_only=False):
		A=database_path
		if A is _A:return
		if not os.path.exists(A)and A!=_B:return
		B.set_database_path(A);C=duckdb.connect();return C
	def build_sqlite(B,database_path):A=database_path;B.set_database_path(A);C=sqlite3.connect(A);return C
	def build_questdb(A):
		B=f"http::addr={A.host}:{A.port};"
		if A.user is not _A:
			if len(A.user)>0:B+=f"username={A.user};"
		if A.password is not _A:
			if len(A.password)>0:B+=f"password={A.password};"
		return B
	def build_mongo(A):B=MongoClient(host=A.host,port=A.port,username=A.user,password=A.password);return B
	def build_influxdb(D,token,organization,user,password):
		E=organization;C=user;B=token;F=f"{D.host}:{D.port}";A=_A
		if B is not _A:
			if len(B)>0:A=InfluxDBClient(url=F,token=B,org=E)
		if A is _A:
			if C is not _A:
				if len(C)>0:A=InfluxDBClient(url=F,username=C,password=password,org=E)
		return A
	def build_csv(A,file_path):A.set_file_path(file_path);return A
	def build_xls(A,file_path):A.set_file_path(file_path);return A
	def build_json_api(A,json_url,dynamic_inputs=_A,py_code_processing=_A):A.set_json_url(json_url);A.set_dynamic_inputs(dynamic_inputs);A.set_py_code_processing(py_code_processing)
	def build_python(A,py_code_processing=_A,dynamic_inputs=_A):A.set_py_code_processing(py_code_processing);A.set_dynamic_inputs(dynamic_inputs)
	def build_wss(A,socket_url,dynamic_inputs=_A,py_code_processing=_A):A.set_socket_url(socket_url);A.set_dynamic_inputs(dynamic_inputs);A.set_py_code_processing(py_code_processing)
	def get_sqlachemy_engine(A):return create_engine(A.url_engine)
	def get_available_tables(A):
		try:B=A.get_sqlachemy_engine();C=inspect(B);D=C.get_table_names();return sorted(D)
		except Exception as E:print('Exception get available tables metadata');print(E);return[]
	def get_table_columns(C,table_name):
		B='type'
		try:
			D=C.get_sqlachemy_engine();E=inspect(D);A=E.get_columns(table_name)
			if A:return[{'column':A['name'],B:str(A[B])}for A in A]
		except Exception as F:print('Exception get table columuns metadata');print(F)
		return[]
	def get_data_table(B,table_name):
		A=table_name
		try:
			C=B.get_sqlachemy_engine();D=text(f"SELECT * FROM {A}")
			with C.connect()as E:F=E.execute(D);G=F.fetchall();return G
		except Exception as H:print(f"Exception while loading data from table '{A}'");print(H)
		return[]
	def get_data_table_query(B,sql,table_name=_A):
		A=sql
		if A is not _A:
			if len(A)>0:return B.read_sql_query(A)
		return pd.DataFrame()
	def read_sql_query(A,sql,index_col=_A,coerce_float=True,params=_A,parse_dates=_A,chunksize=_A,dtype=_A):return pd.read_sql_query(sql,con=A.connector,index_col=index_col,coerce_float=coerce_float,params=params,parse_dates=parse_dates,chunksize=chunksize,dtype=dtype)