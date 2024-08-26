import os
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_c43a65d628 import qube_c43a65d628
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_a725fbe9d8 import qube_a725fbe9d8
class db_custom_connection:
	def __init__(A):A.dbCon=None;A.dbIdManager='';A.spartAppId=''
	def setSettingsSqlite(B,dbId,dbLocalPath,dbFileNameWithExtension):G='spartApp';E=dbLocalPath;C=dbId;from bqm import settings as F,settingsLocalDesktop as H;B.dbType=0;B.spartAppId=C;A={};A['id']=C;A['ENGINE']='django.db.backends.sqlite3';A['NAME']=str(E)+'/'+str(dbFileNameWithExtension);A['USER']='';A['PASSWORD']='2change';A['HOST']='';A['PORT']='';F.DATABASES[C]=A;H.DATABASES[C]=A;D=qube_a725fbe9d8();D.setPath(E);D.setDbName(G);B.dbCon=D;B.dbIdManager=G;print(F.DATABASES)
	def getConnection(A):return A.dbCon
	def setAuthDB(A,authDB):A.dbType=authDB.dbType