from django.conf.urls import url
from .views import *

urlpatterns=[
		url(r'^Update_Payroll_Document/$',Update_Payroll_Document,name="Update_Payroll_Document"),
		url(r'^Send_Payroll/$',Send_Payroll,name="Send_Payroll"),
		url(r'^Send_Payroll/$',Send_Payroll,name="Send_Payroll"),
		url(r'^Recovery_Payroll/$',Recovery_Payroll,name="Recovery_Payroll"),
		url(r'^Generate_Payroll/$',Generate_Payroll,name="Generate_Payroll"),
		url(r'^Save_Payroll/$',Save_Payroll,name="Save_Payroll"),
	]