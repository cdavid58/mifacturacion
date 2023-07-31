from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^List_Invoice/$',List_Invoice,name="List_Invoice"),
	url(r'^Create_Invoice/$',Create_Invoice,name="Create_Invoice"),
	url(r'^GetProducts/$',GetProducts,name="GetProducts"),
	url(r'^Save_Invoice_FE/$',Save_Invoice_FE,name="Save_Invoice_FE"),
	url(r'^Payment_Forms/$',Payment_Forms,name="Payment_Forms"),
	url(r'^Vence/$',Vence,name="Vence"),
	url(r'^Print_Invoice/$',Print_Invoice,name="Print_Invoice"),
	url(r'^Send_Dian/(\d+)/$',Send_Dian,name="Send_Dian"),
	url(r'^Credit_Notes/(\d+)/$',Credit_Notes,name="Credit_Notes"),
	url(r'^NoteCreditProduct/$',NoteCreditProduct,name="NoteCreditProduct"),
	url(r'^List_Credit_Note/$',List_Credit_Note,name="List_Credit_Note"),
	url(r'^NoteCredit_From_JS/$',NoteCredit_From_JS,name="NoteCredit_From_JS"),
	url(r'^GetPDF/(\d+)/$',GetPDF,name="GetPDF"),
	url(r'^Send_Email/$',Send_Email,name="Send_Email"),
	url(r'^acceptance/(\w+)/(\w+)/(\w+)/$',acceptance,name="acceptance"),
	url(r'^rejection/(\w+)/(\w+)/(\w+)/$',rejection,name="rejection"),
]