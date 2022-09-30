from django.http import HttpResponse
from django.shortcuts import render,redirect
from company.models import Company
from api.translator import Translator
from .models import *
from data.models import Type_Organization,Type_Regime,Municipality,Type_Document_Identification
from api.Create_Client import CreateClient
import sqlite3,json
from invoice.models import Invoice
from from_number_to_letters import Thousands_Separator

t = Translator()

def company(request):
	return Company.objects.get(documentIdentification = t.codificar(str((request.session['nit_company']))))


def List_Client(request):
	client = Client.objects.filter(company = company(request))
	_data = [
		{
			'pk':i.pk,
			'document':t.decodificar(str(i.identification_number)),
			'name':t.decodificar(str(i.name)),
			'phone':t.decodificar(str(i.phone)),
			'email':t.decodificar(str(i.email))
		}for i in client
	]
	return render(request,'client/list_client.html',{'c':_data})


def Profile_Client(request,pk):
	company = Company.objects.get(documentIdentification = t.codificar(str((request.session['nit_company']))))
	con = sqlite3.connect('db.sqlite3')
	cursor = con.cursor()
	cursor.execute("select DISTINCT number from invoice_invoice where client_id="+str(pk)+" and company_id="+str(company.pk))
	_data = []
	
	if request.is_ajax():
		invoice = Invoice.objects.filter(number = t.codificar(str(request.GET.get('number'))))
		_product = [
			{
				'code':t.decodificar(str(x.code)),
				'description':t.decodificar(str(x.description)),
				'base':x.Base_Product(),
				'tax':x.Tax_Value(),
				'SubTotal':x.Base_Product_WithOut_Discount(),
				'quanty':t.decodificar(str(x.quanty))
			}
			for x in invoice
		]
		return HttpResponse(json.dumps(_product))
	total_fe = 0 
	for i in cursor.fetchall():
		invoice = Invoice.objects.filter(number = i[0])
		total = 0
		for j in invoice:
			total += j.Totals()
			total_fe += j.Totals()

		_data.append({
			'number':t.decodificar(str(invoice.last().number)),
			'total':total,
			'name':t.decodificar(str(invoice.last().client.name)),
			'date':t.decodificar(str(invoice.last().date))
		})

	client = Client.objects.get(pk = pk,company = company)
	data = {
		'pk':client.pk,
		'img':client.img.url,
		'merchant_registration':t.decodificar(str(client.merchant_registration)),
		'name': t.decodificar(str(client.name)),
		'email':t.decodificar(str(client.email)),
		'phone':t.decodificar(str(client.phone)),
		'address':t.decodificar(str(client.address)),
	}
	return render(request,'client/patient-profile.html',{'i':data,'data':_data,'total_fe':Thousands_Separator(total_fe)})

def Add_Client(request):

	global company

	if request.is_ajax():
		data = request.GET
		_client = {
			"identification_number":data['identification_number'] ,
			"dv":data['dv'] ,
			"name":data['name'] ,
			"phone":data['phone'] ,
			"address":data['address'] ,
			"email":data['email'] ,
			"merchant_registration":data['merchant_registration'] ,
			"type_document_identification_id":data['type_document_identification_id'] ,
			"type_organization_id":data['type_organization'] ,
			"type_regime_id":data['type_regime'] ,
			"municipality_id":data['municipality'] ,
			"company":request.session['nit_company']
		}
		c = CreateClient(_client)
		message = c.Create()
		return HttpResponse(message)




	to = Type_Organization.objects.all()
	tr = Type_Regime.objects.all()
	muni = Municipality.objects.all().order_by('name')
	td = Type_Document_Identification.objects.all()
	return render(request,'client/add-patient.html',{'to':to,
		'tr':tr,'muni':muni,'td':td
	})



def Delete_Client(request,pk):
	Client.objects.get(pk = pk).delete()
	return redirect('List_Client')


def Edit_Client(request,pk):
	client = Client.objects.get(pk = pk)
	if request.is_ajax():
		data = request.GET

		to = Type_Organization.objects.get(pk = data['organization'])
		tr = Type_Regime.objects.get(pk = data['regime'])
		muni = Municipality.objects.get(pk = data['municipality'])
		td = Type_Document_Identification.objects.get(pk = data['documentI'])

		client.name = t.codificar(str(data['name']))
		client.address = t.codificar(str(data['address']))
		client.email = t.codificar(str(data['email']))
		client.phone = t.codificar(str(data['phone']))
		client.type_documentI = td
		client.type_organization = to
		client.type_regime = tr
		client.municipality = muni

		client.save()
		return HttpResponse("Exito")
	data_client ={
			'pk':client.pk,
			'name':t.decodificar(str(client.name)),
			'address':t.decodificar(str(client.address)),
			'email':t.decodificar(str(client.email)),
			'phone':t.decodificar(str(client.phone)),
			'document':client.type_documentI,
			'organization':client.type_organization,
			'regimen':client.type_regime,
			'municipality':client.municipality
		}
	
	to = Type_Organization.objects.all()
	tr = Type_Regime.objects.all()
	muni = Municipality.objects.all().order_by('name')
	td = Type_Document_Identification.objects.all()
	return render(request,'client/edit-patient.html',{'i':data_client,'to':to,
																		'tr':tr,'muni':muni,'td':td
		})



