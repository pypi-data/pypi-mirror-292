import os,json,base64,json
def sparta_2136ac3c43():A=os.path.dirname(__file__);B=os.path.dirname(A);return json.loads(open(B+'/platform.json').read())['PLATFORM']
def sparta_74eeb5c2a8(b):return base64.b64decode(b).decode('utf-8')
def sparta_c7a501111a(s):return base64.b64encode(s.encode('utf-8'))