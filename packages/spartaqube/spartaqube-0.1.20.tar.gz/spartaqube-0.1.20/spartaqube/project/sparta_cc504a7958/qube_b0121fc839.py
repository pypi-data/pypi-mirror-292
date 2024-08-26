import time
def sparta_7fe50cdd33():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_7fe50cdd33()
def sparta_f44f5d571f(tempBool=True):
	A=next(TicToc)
	if tempBool:print('Elapsed time: %f seconds.\n'%A);return A
def sparta_ee6011ba79():sparta_f44f5d571f(False)