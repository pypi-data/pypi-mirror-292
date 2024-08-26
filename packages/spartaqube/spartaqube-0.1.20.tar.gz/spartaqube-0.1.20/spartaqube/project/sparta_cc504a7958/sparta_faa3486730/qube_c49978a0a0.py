import os
from project.sparta_cc504a7958.sparta_faa3486730.qube_fe038791e5 import qube_fe038791e5
from project.sparta_cc504a7958.sparta_faa3486730.qube_a285dcf742 import qube_a285dcf742
from project.sparta_cc504a7958.sparta_faa3486730.qube_b0e60472f0 import qube_b0e60472f0
from project.sparta_cc504a7958.sparta_faa3486730.qube_1d08fa7c1a import qube_1d08fa7c1a
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_fe038791e5()
		elif A.dbType==1:A.dbCon=qube_a285dcf742()
		elif A.dbType==2:A.dbCon=qube_b0e60472f0()
		elif A.dbType==4:A.dbCon=qube_1d08fa7c1a()
		return A.dbCon