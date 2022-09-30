from django.conf.urls import url
from .views import *

urlpatterns=[
		url(r'^Wallet_Elec/$',Wallet_Elec,name="Wallet_Elec"),
		url(r'^Report_Wallet_Elec/$',Report_Wallet_Elec,name="Report_Wallet_Elec"),
		url(r'^Electronic_Invoice_Docment_Wallet/(\d+)/$',Electronic_Invoice_Docment_Wallet,name="Electronic_Invoice_Docment_Wallet"),
		url(r'^Wallet_Elec_POS/$',Wallet_Elec_POS,name="Wallet_Elec_POS"),
		url(r'^Bill_To_Pay/$',Bill_To_Pay,name="Bill_To_Pay"),
		url(r'^CXP_General/$',CXP_General,name="CXP_General"),
	]