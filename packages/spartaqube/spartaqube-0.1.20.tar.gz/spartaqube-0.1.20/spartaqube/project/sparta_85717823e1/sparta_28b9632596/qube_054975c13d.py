_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_1a043102bc():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_b8124f0888(objectToCrypt):A=objectToCrypt;C=sparta_1a043102bc();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_b5659ac77f(apiAuth):A=apiAuth;B=sparta_1a043102bc();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_8a5470c7bd(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_692e2d4981(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_8a5470c7bd(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_bf141103ba(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_8a5470c7bd(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_6fef38eb5b(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_2e6b831a4f(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_6fef38eb5b(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_214755a341(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_6fef38eb5b(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_9c97c5439d(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_1dcc3f91a4(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_9c97c5439d(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_024d717d30(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_9c97c5439d(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)