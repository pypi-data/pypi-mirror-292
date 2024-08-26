_C='json_api'
_B='postgres'
_A=None
import time,json,pandas as pd
from pandas.api.extensions import no_default
import project.sparta_991c77bcde.sparta_ca58c8d226.qube_82fcaeb071 as qube_82fcaeb071
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_5b1ba979be.qube_ad40b3f5c5 import ArcticConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_b1575e840a.qube_b61ac50168 import AerospikeConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_d8670873e6.qube_09fb379b39 import CassandraConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_75c215bc83.qube_a898134f19 import ClickhouseConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_aa4ac18ce7.qube_17bbaefd5c import CouchdbConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_73ddf72f6d.qube_b235ff27a8 import CsvConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_fc78aca0cd.qube_5358992d02 import DuckDBConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_db0f793570.qube_29936cc769 import JsonApiConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_61081ac872.qube_54abcf4c95 import InfluxdbConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_f1bb3936cf.qube_0ab2009ddf import MariadbConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_8efc97a518.qube_4640562c19 import MongoConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_97a80d0334.qube_28e612ada4 import MssqlConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_956f652c81.qube_2baf977cc5 import MysqlConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_a00c432663.qube_f55c419638 import OracleConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_1aaae97689.qube_5e02d0c663 import ParquetConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_878c1f9ca6.qube_4e62928a2a import PostgresConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_49771e4609.qube_54f184c835 import PythonConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_3bbcc4bf6b.qube_2f9accaff4 import QuestDBConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_3c14ccb617.qube_40d05feb16 import RedisConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_2338710f01.qube_d25b57c70c import ScylladbConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_994d6ea317.qube_11ec71773d import SqliteConnector
from project.sparta_991c77bcde.sparta_ca58c8d226.sparta_31a89f569d.qube_ad0d3bda5e import WssConnector
class Connector:
	def __init__(A,db_engine=_B):A.db_engine=db_engine
	def init_with_model(B,connector_obj):
		A=connector_obj;E=A.host;F=A.port;G=A.user;H=A.password_e
		try:C=qube_82fcaeb071.sparta_0701ea356c(H)
		except:C=_A
		I=A.database;J=A.oracle_service_name;K=A.keyspace;L=A.library_arctic;M=A.database_path;N=A.read_only;O=A.json_url;P=A.socket_url;Q=A.db_engine;R=A.csv_path;S=A.csv_delimiter;T=A.token;U=A.organization;V=A.lib_dir;W=A.driver;X=A.trusted_connection;D=[]
		if A.dynamic_inputs is not _A:
			try:D=json.loads(A.dynamic_inputs)
			except:pass
		Y=A.py_code_processing;B.db_engine=Q;B.init_with_params(host=E,port=F,user=G,password=C,database=I,oracle_service_name=J,csv_path=R,csv_delimiter=S,keyspace=K,library_arctic=L,database_path=M,read_only=N,json_url=O,socket_url=P,dynamic_inputs=D,py_code_processing=Y,token=T,organization=U,lib_dir=V,driver=W,trusted_connection=X)
	def init_with_params(A,host,port,user=_A,password=_A,database=_A,oracle_service_name='orcl',csv_path=_A,csv_delimiter=_A,keyspace=_A,library_arctic=_A,database_path=_A,read_only=False,json_url=_A,socket_url=_A,redis_db=0,token=_A,organization=_A,lib_dir=_A,driver=_A,trusted_connection=True,dynamic_inputs=_A,py_code_processing=_A):
		J=keyspace;I=py_code_processing;H=dynamic_inputs;G=database_path;F=database;E=password;D=user;C=port;B=host;print('self.db_engine > '+str(A.db_engine))
		if A.db_engine=='aerospike':A.db_connector=AerospikeConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='arctic':A.db_connector=ArcticConnector(database_path=G,library_arctic=library_arctic)
		if A.db_engine=='cassandra':A.db_connector=CassandraConnector(host=B,port=C,user=D,password=E,keyspace=J)
		if A.db_engine=='clickhouse':A.db_connector=ClickhouseConnector(host=B,port=C,database=F,user=D,password=E)
		if A.db_engine=='couchdb':A.db_connector=CouchdbConnector(host=B,port=C,user=D,password=E)
		if A.db_engine=='csv':A.db_connector=CsvConnector(csv_path=csv_path,csv_delimiter=csv_delimiter)
		if A.db_engine=='duckdb':A.db_connector=DuckDBConnector(database_path=G,read_only=read_only)
		if A.db_engine=='influxdb':A.db_connector=InfluxdbConnector(host=B,port=C,token=token,organization=organization,bucket=F,user=D,password=E)
		if A.db_engine==_C:A.db_connector=JsonApiConnector(json_url=json_url,dynamic_inputs=H,py_code_processing=I)
		if A.db_engine=='mariadb':A.db_connector=MariadbConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='mongo':A.db_connector=MongoConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='mssql':A.db_connector=MssqlConnector(host=B,port=C,trusted_connection=trusted_connection,driver=driver,user=D,password=E,database=F)
		if A.db_engine=='mysql':A.db_connector=MysqlConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='oracle':A.db_connector=OracleConnector(host=B,port=C,user=D,password=E,database=F,lib_dir=lib_dir,oracle_service_name=oracle_service_name)
		if A.db_engine=='parquet':A.db_connector=ParquetConnector(database_path=G)
		if A.db_engine==_B:A.db_connector=PostgresConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='python':A.db_connector=PythonConnector(py_code_processing=I,dynamic_inputs=H)
		if A.db_engine=='questdb':A.db_connector=QuestDBConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='redis':A.db_connector=RedisConnector(host=B,port=C,user=D,password=E,db=redis_db)
		if A.db_engine=='scylladb':A.db_connector=ScylladbConnector(host=B,port=C,user=D,password=E,keyspace=J)
		if A.db_engine=='sqlite':A.db_connector=SqliteConnector(database_path=G)
		if A.db_engine=='wss':A.db_connector=WssConnector(socket_url=socket_url,dynamic_inputs=H,py_code_processing=I)
	def get_db_connector(A):return A.db_connector
	def test_connection(A):return A.db_connector.test_connection()
	def sparta_f2872c7e68(A):return A.db_connector.preview_output_connector()
	def get_error_msg_test_connection(A):return A.db_connector.get_error_msg_test_connection()
	def get_available_tables(A):B=A.db_connector.get_available_tables();return B
	def get_table_columns(A,table_name):B=A.db_connector.get_table_columns(table_name);return B
	def get_data_table(A,table_name):
		if A.db_engine==_C:return A.db_connector.get_json_api_dataframe()
		else:B=A.db_connector.get_data_table(table_name);return pd.DataFrame(B)
	def get_data_table_query(A,sql,table_name=_A):return A.db_connector.get_data_table_query(sql,table_name=table_name)