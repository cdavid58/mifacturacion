from django.http import HttpResponse
from django.shortcuts import render
from invoice.models import *
from company.models import Company
from client.models import Client
from api.translator import Translator
from datetime import date
from pos.models import *
from inventory.models import Inventory
import time
from from_number_to_letters import numero_a_letras,Thousands_Separator
t = Translator()

def Electronic_Invoice_List(request):
	company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(company = company)
	return HttpResponse("Bien")

def Electronic_Invoice_Docment(request,pk):
	request.session['number_invoice'] = pk
	invoice= Invoice.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))),type = "FE",number = t.codificar(str(pk)))
	_invoice = Invoice.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))),type = "FE",number = t.codificar(str(pk))).last()
	total = 0 
	subtotal = 0
	tax = 0
	discount = 0
	neto = 0
	ico = 0
	for i in invoice:
		tax += round(i.Tax_Value())
		total += round(float(i.Neto()))
		subtotal += round(float(i.Base_Product_WithOut_Discount()))
		discount += round(float(t.decodificar(str(i.discount))))
		neto += round(float(t.decodificar(str(Inventory.objects.get(code = i.code).price))))
		ico += round(float(t.decodificar(str(i.ipo))) * float(t.decodificar(str(i.quanty)))) 

	data = [
		{
			'code':t.decodificar(str(i.code)),
			'description':t.decodificar(str(i.description)),
			'quanty':Thousands_Separator(round(float(t.decodificar(str(i.quanty))))),
			'price':Thousands_Separator(round(float(t.decodificar(str(i.price))))),
			'tax_value':Thousands_Separator(round(Inventory.objects.get(code = i.code).Tax_Value())),
			'ICO':Thousands_Separator(round(float(t.decodificar(str(i.ipo))))),
			'discount':Thousands_Separator(round(float(t.decodificar(str(i.discount))))),
			'subtotal':Thousands_Separator(round(float(i.Base_Product_WithOut_Discount()))),
			'totals':round(i.Totals()),
			'neto':Thousands_Separator(round(float(t.decodificar(str(Inventory.objects.get(code = i.code).price))))),
			'tax_prduct':t.decodificar(str(Inventory.objects.get(code = i.code).tax)),
			'discount':t.decodificar(str(Inventory.objects.get(code = i.code).discount)),
			'discount_value':Thousands_Separator(float(t.decodificar(str(i.discount)))),
		}
		for i in invoice
	]
	client = {
			'name':t.decodificar(str(_invoice.client.name)),
			'address':t.decodificar(str(_invoice.client.address)),
			'phone':t.decodificar(str(_invoice.client.phone)),
			'email':t.decodificar(str(_invoice.client.email))
		}
	company = {
			'name':t.decodificar(str(_invoice.company.business_name)),
			'address':t.decodificar(str(_invoice.company.address)),
			'phone':t.decodificar(str(_invoice.company.phone)),
			'email':t.decodificar(str(_invoice.company.email))
		}

	pf = Payment_Form_Invoice.objects.get(invoice = _invoice)
	_data_pf = {
		'payment_due_date':pf.payment_due_date,
		'duration_measure':pf.duration_measure
	}

	_date = {
		'fg':t.decodificar(str(_invoice.date)),
		'today': date.today(),
		'state':t.decodificar(str(_invoice.state))
	}
	return render(request,'document_payment/invoice_fe.html',{
																'invoice':data,'client':client,'company':company,
																'totals':Thousands_Separator(total),'subtotal':Thousands_Separator(subtotal),'tax':Thousands_Separator(tax),'date':_date,'pf':pf,'number_invoice':pk,
																'data_pf':_data_pf,'discount':Thousands_Separator(discount),'neto':Thousands_Separator(neto),'ico':Thousands_Separator(ico)
															 }
				)

def Electronic_Invoice_Docment_POS(request,pk):
	invoice= POS.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))),number = t.codificar(str(pk)))
	_invoice = POS.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))),number = t.codificar(str(pk))).last()
	total = 0 
	subtotal = 0
	tax = 0
	for i in invoice:
		tax += round(i.Tax_Value(),2)
		total += round(float(i.Totals()),2)
		subtotal += round(float(i.Base_Product_WithOut_Discount()),2)
	data = [
		{
			'code':t.decodificar(str(i.code)),
			'description':t.decodificar(str(i.description)),
			'quanty':t.decodificar(str(i.quanty)),
			'price':i.Base_Product_WithOut_Discount(),
			'tax':t.decodificar(str(i.tax)),
			'tax_value':i.Tax_Value(),
			'ICO':t.decodificar(str(i.ipo)),
			'discount':0,
			'subtotal':round(float(i.Base_Product_WithOut_Discount()) * float(t.decodificar(str(i.quanty))),2),
			'totals':i.Totals()
		}
		for i in invoice
	]
	client = {
			'name':t.decodificar(str(_invoice.client.name)),
			'address':t.decodificar(str(_invoice.client.address)),
			'phone':t.decodificar(str(_invoice.client.phone)),
			'email':t.decodificar(str(_invoice.client.email))
		}
	company = {
			'name':t.decodificar(str(_invoice.company.business_name)),
			'address':t.decodificar(str(_invoice.company.address)),
			'phone':t.decodificar(str(_invoice.company.phone)),
			'email':t.decodificar(str(_invoice.company.email))
		}

	pf = Payment_Form_Invoice_POS.objects.get(pos = _invoice)
	_data_pf = {
		'payment_due_date':pf.payment_due_date,
		'duration_measure':pf.duration_measure
	}

	_date = {
		'fg':t.decodificar(str(_invoice.date)),
		'today': date.today(),
		'state':t.decodificar(str(_invoice.state))
	}
	return render(request,'document_payment/pos_list.html',{
																'invoice':data,'client':client,'company':company,
																'totals':total,'subtotal':subtotal,'tax':tax,'date':_date,'pf':pf,'number_invoice':pk,
																'data_pf':_data_pf
															 }
				)
