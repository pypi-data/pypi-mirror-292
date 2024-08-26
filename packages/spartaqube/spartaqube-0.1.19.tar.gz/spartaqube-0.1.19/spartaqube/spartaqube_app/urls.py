from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_1187fa7ef2.sparta_9a27af9178.qube_22a6d18d8b.sparta_f22b5aa634'
handler500='project.sparta_1187fa7ef2.sparta_9a27af9178.qube_22a6d18d8b.sparta_7fd068284e'
handler403='project.sparta_1187fa7ef2.sparta_9a27af9178.qube_22a6d18d8b.sparta_36e2994e97'
handler400='project.sparta_1187fa7ef2.sparta_9a27af9178.qube_22a6d18d8b.sparta_af734ef2ab'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]