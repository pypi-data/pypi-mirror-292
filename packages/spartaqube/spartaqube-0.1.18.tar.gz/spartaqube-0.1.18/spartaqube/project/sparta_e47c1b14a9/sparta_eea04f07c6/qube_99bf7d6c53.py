import os
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_a725fbe9d8 import qube_a725fbe9d8
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_c43a65d628 import qube_c43a65d628
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_bac5fac59e import qube_bac5fac59e
from project.sparta_e47c1b14a9.sparta_eea04f07c6.qube_10482d6c14 import qube_10482d6c14
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_a725fbe9d8()
		elif A.dbType==1:A.dbCon=qube_c43a65d628()
		elif A.dbType==2:A.dbCon=qube_bac5fac59e()
		elif A.dbType==4:A.dbCon=qube_10482d6c14()
		return A.dbCon