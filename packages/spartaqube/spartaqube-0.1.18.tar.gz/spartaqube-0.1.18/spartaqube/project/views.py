import os,json,base64,json
def sparta_aae601d0a4():A=os.path.dirname(__file__);B=os.path.dirname(A);return json.loads(open(B+'/platform.json').read())['PLATFORM']
def sparta_ac479fc6e0(b):return base64.b64decode(b).decode('utf-8')
def sparta_9b5ad3bc59(s):return base64.b64encode(s.encode('utf-8'))