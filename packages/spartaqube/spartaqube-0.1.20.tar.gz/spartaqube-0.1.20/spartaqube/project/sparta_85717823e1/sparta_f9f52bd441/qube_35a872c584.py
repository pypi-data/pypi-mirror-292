_A='utf-8'
import base64,hashlib
from cryptography.fernet import Fernet
def sparta_115cdff2ec():B='db-conn';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_e2554bdb04(password_to_encrypt):A=password_to_encrypt;A=A.encode(_A);C=Fernet(sparta_115cdff2ec().encode(_A));B=C.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_c406ce405a(password_e):B=Fernet(sparta_115cdff2ec().encode(_A));A=base64.b64decode(password_e);A=B.decrypt(A).decode(_A);return A
def sparta_76236a9aad():return sorted(['aerospike','arctic','cassandra','clickhouse','couchdb','csv','duckdb','influxdb','json_api','mariadb','mongo','mssql','mysql','oracle','parquet','postgres','python','questdb','redis','scylladb','sqlite','wss'])