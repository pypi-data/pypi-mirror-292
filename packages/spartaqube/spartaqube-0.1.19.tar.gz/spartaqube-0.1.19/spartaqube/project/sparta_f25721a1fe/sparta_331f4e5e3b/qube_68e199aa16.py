import os
from project.sparta_f25721a1fe.sparta_331f4e5e3b.qube_b31b27c829 import qube_b31b27c829
from project.sparta_f25721a1fe.sparta_331f4e5e3b.qube_4884ca6050 import qube_4884ca6050
from project.sparta_f25721a1fe.sparta_331f4e5e3b.qube_cbb0cac23a import qube_cbb0cac23a
from project.sparta_f25721a1fe.sparta_331f4e5e3b.qube_b1e82e769b import qube_b1e82e769b
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_b31b27c829()
		elif A.dbType==1:A.dbCon=qube_4884ca6050()
		elif A.dbType==2:A.dbCon=qube_cbb0cac23a()
		elif A.dbType==4:A.dbCon=qube_b1e82e769b()
		return A.dbCon