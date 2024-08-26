import couchdb,pandas as pd
from project.sparta_85717823e1.sparta_f9f52bd441.qube_f5c68a0e9e import EngineBuilder
from project.sparta_85717823e1.sparta_c648d09df3.qube_f514117b98 import sparta_9d9c760226
class CouchdbConnector(EngineBuilder):
	def __init__(self,host,port,user,password):
		if host.startswith('localhost'):host='http://localhost'
		super().__init__(host=host,port=port,user=user,password=password,engine_name='couchdb');self.connector=self.build_couchdb()
	def test_connection(self):
		A=False
		try:
			url=f"{self.host}:{self.port}";couch=couchdb.Server(url);couch.resource.credentials=self.user,self.password
			try:
				if self.database in couch:db=couch[self.database];return True
				else:self.error_msg_test_connection='Invalid database';return A
			except Exception as e:self.error_msg_test_connection='Invalid user/password'
		except Exception as e:self.error_msg_test_connection=str(e);return A
	def get_available_tables(self):
		try:db=self.connector;databases=list(db);return databases
		except Exception as e:print(e);return[]
	def get_table_columns(self,table_name):
		try:db=self.connector;database=table_name;doc_id=table_name;doc=db[doc_id];fields=list(doc.keys());return fields
		except Exception as e:return[]
	def get_data_table(self,table_name):
		documents=[];db=self.connector[table_name];documents=[]
		for row in db.view('_all_docs',include_docs=True):documents.append(row.doc)
		return sparta_9d9c760226(pd.DataFrame(documents))
	def get_data_table_query(self,sql,table_name=None):A='selector';exec(sql,globals(),locals());selector_to_apply=eval(A);query={A:selector_to_apply};documents=[];db=self.connector[table_name];result=db.find(query);documents=[doc for doc in result];return sparta_9d9c760226(pd.DataFrame(documents))