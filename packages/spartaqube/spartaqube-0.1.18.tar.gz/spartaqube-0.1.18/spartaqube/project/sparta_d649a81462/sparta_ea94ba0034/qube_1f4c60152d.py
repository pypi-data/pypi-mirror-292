import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_991c77bcde.sparta_5636f8140a import qube_ec499dab50 as qube_ec499dab50
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_8e7f45378d
@csrf_exempt
@sparta_8e7f45378d
def sparta_b1c192ba2b(request):G='api_func';F='key';E='utf-8';A=request;C=A.body.decode(E);C=A.POST.get(F);D=A.body.decode(E);D=A.POST.get(G);B=dict();B[F]=C;B[G]=D;H=qube_ec499dab50.sparta_b1c192ba2b(B,A.user);I=json.dumps(H);return HttpResponse(I)