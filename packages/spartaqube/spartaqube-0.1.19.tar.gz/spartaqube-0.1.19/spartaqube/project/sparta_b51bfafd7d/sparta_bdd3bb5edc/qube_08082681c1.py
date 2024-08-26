_C='json_api'
_B='postgres'
_A=None
import time,json,pandas as pd
from pandas.api.extensions import no_default
import project.sparta_b51bfafd7d.sparta_bdd3bb5edc.qube_f1bd2a17cc as qube_f1bd2a17cc
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_bc7704fb2f.qube_b8826cdf62 import ArcticConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_f8359a06b1.qube_27673fd687 import AerospikeConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_e7b7e444a2.qube_8b803f7583 import CassandraConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_377ce0c2c3.qube_c66435d196 import ClickhouseConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_19a6a4809e.qube_9e6c265b40 import CouchdbConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_c8d8c4b6c8.qube_e4bbed2eb0 import CsvConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_4f199bde11.qube_eb6067228b import DuckDBConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_6e3d227cc8.qube_f12d0270cb import JsonApiConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_3dbce009c2.qube_0e1af548ca import InfluxdbConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_73c462b50a.qube_bc66811d47 import MariadbConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_fc0b050082.qube_e9148bc45f import MongoConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_a15a1b591c.qube_90b64a4f96 import MssqlConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_c8066570ed.qube_61d11566d3 import MysqlConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_2a4442bf38.qube_11ddb6b286 import OracleConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_175aafd1a0.qube_2d9863360e import ParquetConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_9e221fb931.qube_fdf7da9477 import PostgresConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_c643779893.qube_a82bc920a0 import PythonConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_ecfe2923d5.qube_180a813c2f import QuestDBConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_cf13b044fc.qube_17a651d9dd import RedisConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_17f96f2f8c.qube_4780b51362 import ScylladbConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_71fa3bab2b.qube_e48accb981 import SqliteConnector
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.sparta_bf7026f0fa.qube_0330d1ecff import WssConnector
class Connector:
	def __init__(A,db_engine=_B):A.db_engine=db_engine
	def init_with_model(B,connector_obj):
		A=connector_obj;E=A.host;F=A.port;G=A.user;H=A.password_e
		try:C=qube_f1bd2a17cc.sparta_d609831953(H)
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
	def sparta_3520202e7f(A):return A.db_connector.preview_output_connector()
	def get_error_msg_test_connection(A):return A.db_connector.get_error_msg_test_connection()
	def get_available_tables(A):B=A.db_connector.get_available_tables();return B
	def get_table_columns(A,table_name):B=A.db_connector.get_table_columns(table_name);return B
	def get_data_table(A,table_name):
		if A.db_engine==_C:return A.db_connector.get_json_api_dataframe()
		else:B=A.db_connector.get_data_table(table_name);return pd.DataFrame(B)
	def get_data_table_query(A,sql,table_name=_A):return A.db_connector.get_data_table_query(sql,table_name=table_name)