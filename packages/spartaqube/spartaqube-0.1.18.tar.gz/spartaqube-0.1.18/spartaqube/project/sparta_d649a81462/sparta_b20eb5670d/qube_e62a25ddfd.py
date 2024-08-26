_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_991c77bcde.sparta_3882652566 import qube_5f319a0fff as qube_5f319a0fff
from project.sparta_991c77bcde.sparta_a9c56d094f import qube_600b1b082c as qube_600b1b082c
from project.sparta_991c77bcde.sparta_23c481f08b.qube_fe08016699 import sparta_8e7f45378d
@csrf_exempt
@sparta_8e7f45378d
def sparta_b435f576ff(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_600b1b082c.sparta_0535c4f863(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_5f319a0fff.sparta_b435f576ff(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_8e7f45378d
def sparta_a318848a39(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_5f319a0fff.sparta_8bad31b5e8(C,A.user);E=json.dumps(D);return HttpResponse(E)