from django.conf.urls import url
from .views import *

urlpatterns=[
		url(r'^List_Notifications/$',List_Notifications,name="List_Notifications"),
		url(r'^Read/$',Read,name="Read"),
	]