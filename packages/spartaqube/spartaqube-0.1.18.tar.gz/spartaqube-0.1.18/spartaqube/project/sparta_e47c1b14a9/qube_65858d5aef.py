import time
def sparta_33e4af79dd():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_33e4af79dd()
def sparta_09149541d9(tempBool=True):
	A=next(TicToc)
	if tempBool:print('Elapsed time: %f seconds.\n'%A);return A
def sparta_76c13644fe():sparta_09149541d9(False)