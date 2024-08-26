from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_c5c580c721.sparta_8e1bcdc07b.qube_ba94c6a3a5.sparta_8fa54d0cfc'
handler500='project.sparta_c5c580c721.sparta_8e1bcdc07b.qube_ba94c6a3a5.sparta_5a78de7c73'
handler403='project.sparta_c5c580c721.sparta_8e1bcdc07b.qube_ba94c6a3a5.sparta_e4d369b797'
handler400='project.sparta_c5c580c721.sparta_8e1bcdc07b.qube_ba94c6a3a5.sparta_ae9f43a342'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]