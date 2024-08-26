_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_b51bfafd7d.sparta_23300cab99 import qube_07dfb9198f as qube_07dfb9198f
from project.sparta_b51bfafd7d.sparta_79921c2dcd import qube_0d1ce61c4b as qube_0d1ce61c4b
from project.sparta_b51bfafd7d.sparta_ba59edf337.qube_eaa8b6f778 import sparta_9990890d7c
@csrf_exempt
@sparta_9990890d7c
def sparta_724bd6d7ef(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_0d1ce61c4b.sparta_832d72dea6(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_07dfb9198f.sparta_724bd6d7ef(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_9990890d7c
def sparta_9dac9345cf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_07dfb9198f.sparta_915f689e26(C,A.user);E=json.dumps(D);return HttpResponse(E)