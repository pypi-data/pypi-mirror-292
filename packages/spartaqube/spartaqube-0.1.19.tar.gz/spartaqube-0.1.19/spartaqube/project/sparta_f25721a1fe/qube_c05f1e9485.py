import time
def sparta_3eb6ccb1ef():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_3eb6ccb1ef()
def sparta_066970897b(tempBool=True):
	A=next(TicToc)
	if tempBool:print('Elapsed time: %f seconds.\n'%A);return A
def sparta_da6425323b():sparta_066970897b(False)