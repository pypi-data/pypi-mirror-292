_A=None
import os,shutil,requests,simplejson as json,datetime,copy,pandas as pd,numpy as np
from decimal import Decimal
from datetime import datetime,date,time,timedelta
def sparta_a3673d4db4(textOutputArr):
	A=textOutputArr
	try:A=[A for A in A if len(A)>0];A=[A for A in A if A!='Welcome to SpartaQuant API'];A=[A for A in A if A!="<span style='color:#0ab70a'>You are logged</span>"];A=[A for A in A if A!='You are logged']
	except Exception as B:pass
	return A
def sparta_7d35653b1c(input2JsonEncode,dateFormat=_A):
	C=dateFormat;import numpy as B
	class D(json.JSONEncoder):
		def default(E,obj):
			A=obj
			if isinstance(A,B.integer):return int(A)
			if isinstance(A,B.floating):return float(A)
			if isinstance(A,B.ndarray):return A.tolist()
			if isinstance(A,datetime.datetime):
				if C is not _A:return A.strftime(C)
				else:return str(A)
			return super(D,E).default(A)
	A=json.dumps(input2JsonEncode,ignore_nan=True,cls=D);return A
def sparta_d16b106ead(path):
	A=path
	try:os.rmdir(A)
	except:
		try:os.system('rmdir /S /Q "{}"'.format(A))
		except:
			try:shutil.rmtree(A)
			except:
				try:os.remove(A)
				except:pass
def sparta_16884f167d(file_path):
	A=file_path
	try:os.remove(A);print(f"File '{A}' has been deleted.")
	except Exception as B:
		try:os.unlink(A);print(f"File '{A}' has been forcefully deleted.")
		except Exception as B:print(f"An error occurred while deleting the file: {B}")
def sparta_2fe9b689db(df):
	D='iso';C='split';A=df
	if len(A)==0:return pd.DataFrame().to_json(orient=C,date_format=D)
	try:E=A.to_json(orient=C,date_format=D)
	except Exception as G:
		F=[]
		for B in A.columns:
			try:A[[B]].to_json(orient=C,date_format=D)
			except:F.append(B)
		for B in F:A[B]=A[B].apply(lambda x:str(x)if not pd.isnull(x)else x)
		E=A.to_json(orient=C,date_format=D)
	return E
def sparta_5b3f451ffa(data_df):return sparta_2fe9b689db(data_df)
def sparta_9d9c760226(input_data,variable_name=_A):
	B=variable_name;A=sparta_468f973937(input_data)
	if A is not _A:
		if len(list(A.columns))==1:
			if len(str(A.columns[0]))<=1:
				if B is not _A:A.columns=[B]
	else:A=pd.DataFrame()
	return A
def sparta_9d0dcdc9fd(input):A={int,str,float,bool,complex,type(_A),bytes,bytearray,pd.Timestamp,pd.Timedelta,pd.Period,pd.Interval,pd.Categorical,pd.IntervalDtype,pd.CategoricalDtype,pd.SparseDtype,pd.Int8Dtype,pd.Int16Dtype,pd.Int32Dtype,pd.Int64Dtype,pd.UInt8Dtype,pd.UInt16Dtype,pd.UInt32Dtype,pd.UInt64Dtype,pd.Float32Dtype,pd.Float64Dtype,pd.BooleanDtype,pd.StringDtype,pd.offsets.DateOffset,np.int8,np.int16,np.int32,np.int64,np.uint8,np.uint16,np.uint32,np.uint64,np.float16,np.float32,np.float64,np.complex64,np.complex128,np.bool_,np.bytes_,np.str_,datetime,date,time,timedelta,Decimal};return isinstance(input,tuple(A))
def sparta_633d585dbc(df):
	D=df.columns.tolist();B={};C=[]
	for A in D:
		if A in B:B[A]+=1;C.append(f"{A}_{B[A]}")
		else:B[A]=0;C.append(A)
	df.columns=C;return df
def sparta_468f973937(input_data):
	A=input_data
	try:
		if isinstance(A,pd.DataFrame):return A
		if isinstance(A,pd.Series):return A.to_frame()
		if isinstance(A,pd.DatetimeIndex):return pd.DataFrame(A.to_list())
		if isinstance(A,dict):
			B=copy.deepcopy(A)
			for D in B:
				if not isinstance(B[D],(list,pd.Series)):B[D]=[B[D]]
			return pd.DataFrame(B)
		if isinstance(A,(list,tuple)):
			if len(A)>0:
				if not sparta_9d0dcdc9fd(A[0]):
					A=[sparta_468f973937(A)for A in A];C=pd.concat(A,axis=1)
					if len(C.columns)!=len(set(C.columns)):C=sparta_633d585dbc(C)
					return C
			return pd.DataFrame(A)
		if A.__class__.__name__.lower()=='ndarray':return pd.DataFrame(A)
		if sparta_9d0dcdc9fd(A):return pd.DataFrame([A])
		try:return pd.DataFrame([A])
		except Exception as E:print('Except convert to dataframe');print(E);return
	except Exception as E:print(f"Error: {E}");return