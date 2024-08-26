_D='utf-8'
_C=True
_B=None
_A=False
import json,io,os,base64,pandas as pd,quantstats as qs,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
def sparta_4663b17bda(df):
	A=df
	if pd.api.types.is_datetime64_any_dtype(A.index):
		if A.index.tz is not _B:A.index=A.index.tz_localize(_B)
	return A
def sparta_0ec667eba2(series):
	A=series
	if(A>=0).all():
		if A.max()>1.:return _A
	return _C
def sparta_fdd9ea5ac7(fig):A=io.BytesIO();fig.savefig(A,format='png');A.seek(0);B=base64.b64encode(A.getvalue()).decode(_D);A.close();return B
def sparta_849b88c8d5(fig):A=BytesIO();fig.savefig(A,format='png');B=base64.b64encode(A.getvalue()).decode(_D);return B
def sparta_3ee122834a(json_data,user_obj):
	h='basic';g='res';f='Portfolio';e='title';d='benchmark_title';c='strategyTitle';b='riskFreeRate';a='reportType';V='split';U='Benchmark';P='date';N=json_data;A=json.loads(N['opts']);K=int(A[a]);W=json.loads(N['xAxisDataArr'])[0];C=json.loads(N['yAxisDataArr']);O=0
	if b in A:O=float(A[b])
	G=U;E='Strategy'
	if c in A:
		Q=A[c]
		if Q is not _B:
			if len(Q)>0:E=Q
	if d in A:
		R=A[d]
		if R is not _B:
			if len(R)>0:G=R
	X='Strategy Tearsheet'
	if e in A:
		Y=A[e]
		if len(Y)>0:X=Y
	H=pd.DataFrame(C[0]);H[P]=pd.to_datetime(W);H.set_index(P,inplace=_C);H.columns=[f];H=sparta_4663b17bda(H);B=H[f]
	if not sparta_0ec667eba2(B):B=B.pct_change().dropna()
	D=_B
	if len(C)==2:
		I=pd.DataFrame(C[1]);I[P]=pd.to_datetime(W);I.set_index(P,inplace=_C);I.columns=[U];I=sparta_4663b17bda(I);D=I[U]
		if not sparta_0ec667eba2(D):D=D.pct_change().dropna()
	if'bHtmlReport'in list(N.keys()):
		i=os.path.dirname(os.path.abspath(__file__));S=os.path.join(i,'quantstats/quantstats-tearsheet.html')
		with open(S,mode='a')as j:j.close()
		qs.reports.html(B,benchmark=D,rf=O,mode='full',match_dates=_C,output=S,title=X,strategy_title=E,benchmark_title=G)
		with open(S,'rb')as k:l=k.read()
		return{g:1,'file_content':l.decode(_D),'b_downloader':_C}
	if K==0:
		def L(data,benchmark=_B):
			C=benchmark;A=[];D=qs.plots.snapshot(data,show=_A,strategy_title=E,benchmark_title=G);A.append(sparta_849b88c8d5(D));B=qs.plots.monthly_heatmap(data,show=_A,ylabel=_A,returns_label=E);A.append(sparta_849b88c8d5(B))
			if C is not _B:B=qs.plots.monthly_heatmap(C,show=_A,ylabel=_A,returns_label=G);A.append(sparta_849b88c8d5(B))
			return A
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==1:
		if len(C)==1:Z=qs.reports.metrics(B,rf=O,mode=h,display=_A,strategy_title=E,benchmark_title=G)
		elif len(C)==2:Z=qs.reports.metrics(B,benchmark=D,rf=O,mode=h,display=_A,strategy_title=E,benchmark_title=G)
		J=Z.to_json(orient=V)
	elif K==2:
		def L(data,benchmark=_B):
			D=benchmark;C=data;B=[]
			if A['returns']:F=qs.plots.returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(F))
			if A['logReturns']:G=qs.plots.log_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(G))
			if A['yearlyReturns']:H=qs.plots.yearly_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(H))
			if A['dailyReturns']:I=qs.plots.daily_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(I))
			if A['histogram']:J=qs.plots.histogram(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(J))
			if A['rollingVol']:K=qs.plots.rolling_volatility(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(K))
			if A['rollingSharpe']:L=qs.plots.rolling_sharpe(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(L))
			if A['rollingSortino']:M=qs.plots.rolling_sortino(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(M))
			if A['rollingBeta']:
				if D is not _B:N=qs.plots.rolling_beta(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(N))
			if A['distribution']:O=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(O))
			if A['heatmap']:P=qs.plots.monthly_heatmap(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(P))
			if A['drawdowns']:Q=qs.plots.drawdown(C,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(Q))
			if A['drawdownsPeriod']:R=qs.plots.drawdowns_periods(C,show=_A,ylabel=_A,title=E);B.append(sparta_849b88c8d5(R))
			if A['returnQuantiles']:S=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_849b88c8d5(S))
			return B
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==3:m=[E];M=B;M.columns=m;n=qs.reports._calc_dd(M);o=qs.stats.drawdown_details(M).sort_values(by='max drawdown',ascending=_C)[:10];T=[];p=qs.plots.drawdown(M,show=_A,ylabel=_A);T.append(sparta_849b88c8d5(p));q=qs.plots.drawdowns_periods(M,show=_A,ylabel=_A,title=E);T.append(sparta_849b88c8d5(q));J=[n.to_json(orient=V),o.to_json(orient=V),T]
	return{g:1,a:K,'output':J}