_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_3aab2d7d60():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_b33d22b385(objectToCrypt):A=objectToCrypt;C=sparta_3aab2d7d60();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_8c87f15803(apiAuth):A=apiAuth;B=sparta_3aab2d7d60();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_f091b20852(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_a57367b556(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_f091b20852(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_94c73b8ded(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_f091b20852(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_015e693593(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_77759fa9a4(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_015e693593(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_1c1bc7c6e8(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_015e693593(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_8dee8490fd(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_64feff91c7(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_8dee8490fd(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_cab460ec79(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_8dee8490fd(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)