from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_eff1c30268.sparta_d5e77a07dc.qube_c05a8bc2f7.sparta_a32a65c669'
handler500='project.sparta_eff1c30268.sparta_d5e77a07dc.qube_c05a8bc2f7.sparta_0881aa6ce9'
handler403='project.sparta_eff1c30268.sparta_d5e77a07dc.qube_c05a8bc2f7.sparta_2f840eb388'
handler400='project.sparta_eff1c30268.sparta_d5e77a07dc.qube_c05a8bc2f7.sparta_4b7789551b'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]