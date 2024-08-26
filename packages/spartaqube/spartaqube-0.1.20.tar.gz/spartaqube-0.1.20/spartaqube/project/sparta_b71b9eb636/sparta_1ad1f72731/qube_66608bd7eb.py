_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_85717823e1.sparta_2355c9d4f8 import qube_8718dc3394 as qube_8718dc3394
from project.sparta_85717823e1.sparta_c6d7d469cb import qube_02002e0b09 as qube_02002e0b09
from project.sparta_85717823e1.sparta_3811b5fb11.qube_851830bece import sparta_3d3d3187e4
@csrf_exempt
@sparta_3d3d3187e4
def sparta_aa7beed32b(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_02002e0b09.sparta_eb0bd94d5f(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_8718dc3394.sparta_aa7beed32b(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_3d3d3187e4
def sparta_49173c9ba4(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8718dc3394.sparta_797c4a4be6(C,A.user);E=json.dumps(D);return HttpResponse(E)