_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_f9709d41ac():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_8efaa06d07(objectToCrypt):A=objectToCrypt;C=sparta_f9709d41ac();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_fe9a1cd31e(apiAuth):A=apiAuth;B=sparta_f9709d41ac();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_ba438f23f5(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_dc4dcbc0c9(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_ba438f23f5(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_6ba9768024(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_ba438f23f5(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_c04b72ef0e(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_eaf7672378(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_c04b72ef0e(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_ef45043a27(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_c04b72ef0e(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_512c5c960c(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_71dc005427(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_512c5c960c(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_0e30d95929(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_512c5c960c(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)