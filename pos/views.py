from django.http import HttpResponse,FileResponse
from django.shortcuts import render
from api.translator import Translator
import time, threading, queue,json
from company.models import Company
from client.models import Client
from .models import *
from inventory.models import Inventory
from data.models import *
from invoice.models import Consecutive_POS
from datetime import date
from date import Count_Days
from inventory.models import Inventory,Discount_Inventory
from from_number_to_letters import numero_a_letras,Thousands_Separator

t = Translator()
my_queue = queue.Queue()
count = 0

def storeInQueue(f):
  def wrapper(*args):
  	global my_queue
  	my_queue.put(f(*args))
  return wrapper

def Create_POS(request):
	company = Company.objects.get(documentIdentification=t.codificar(str(request.session['nit_company'])))
	client = Client.objects.filter(company = company)
	inventory = Inventory.objects.filter(company = company)
	request.session['client'] = Client.objects.get(name = t.codificar('CLIENTE GENERAL')).pk
	if request.is_ajax():
		request.session['client'] = request.GET.get("pk")
		return HttpResponse(request.GET.get("pk"))
	data_client = [{'name':t.decodificar(str(i.name)),'code':i.pk}for i in client]
	data_inventory = [{'code':t.decodificar(str(i.code)),'name':t.decodificar(str(i.name))} for i in inventory]
	pf = Payment_Form.objects.all()
	ce = Consecutive_POS.objects.get(company = company).number
	return render(request,'pos/create_invoice.html',{'client':data_client,'inventory':data_inventory,'cod_bars':company.cod_bars,'pf':pf,'ce':ce})

def a(sms):
	return t.decodificar(str(sms))

def GetProducts_POS(request):
	global count
	if request.is_ajax():
		try:
			_id = Inventory.objects.get(code = t.codificar(str(request.GET.get("pk"))))
			try:
				consult_shopping = Shopping_Inventory.objects.filter(code = _id, used = False).first()
				if int(t.decodificar(str(_id.quanty))) <= 0:
					_id.quanty = consult_shopping.quanty
					_id.price = consult_shopping.price
					_id.save()
					consult_shopping.used = True
					consult_shopping.save()
			except Exception as e:
				pass

			products = [
				{
					'pk':count,
					'code':a(_id.code),
					"name":a(_id.name),
					'cost':_id.BaseWithOutDiscount(),
					'tax':a(_id.tax),
					'discount':a(_id.discount),
					'quanty':a(_id.quanty),
					'tax_value':_id.Tax_Value(),
					'price_discount':_id.PriceDiscount(),
					'neto':t.decodificar(str(_id.price)),
					'ico':t.decodificar(str(_id.ico))
				}
			]


			products = json.dumps(products)
			count += 1
			return HttpResponse(products)
		except Inventory.DoesNotExist:
			return HttpResponse("Error")

def Vence_Pos(request):
	if request.is_ajax():
		print(request.GET.get('date'))
		request.session['date_vence'] = request.GET.get('date')
		request.session['days'] = request.GET.get('days')
		return HttpResponse("")

def Save_Invoice_Pos(request):
	if request.is_ajax():
		data = request.GET
		try:
			success = False
			for i in data:
				_data = json.loads(i)
				if len(_data) == 0:
					break
				di = Discount_Inventory()
				company = Company.objects.get(documentIdentification=t.codificar(str(request.session['nit_company'])))
				consecutive = Consecutive_POS.objects.get(company = company)
				pm = 0
				price = 0
				for j in _data:
					n = 0
					POS(
						number = t.codificar(str(consecutive.number)),
						prefix = t.codificar("FE"),
						code = t.codificar(str(j['Código'])),
						quanty = t.codificar(str(j['Cantidad'])),
						description = t.codificar(str(j['Descripción'])),
						price = t.codificar(str(j['Costo'])),
						tax = t.codificar(str(j['Iva Val'])),
						notes = t.codificar(str("No Hay")),
						date = t.codificar(str(date.today())),
						ipo = t.codificar(str(j['ICO'])),
						discount = t.codificar(str(j['Desc. Val'])),
						client = Client.objects.get(pk = request.session['client']),
						company = company,
						empleoyee = Empleoyee.objects.get(pk=request.session['empleoyee_pk']),
						state = t.codificar("Facturado al contado") if int(request.session['payment_form']) == 1 else t.codificar("Facturado a credito")
					).save()
					price += float(j['Costo'])
					if n == 0:
						pm = 10 if int(request.session['payment_form']) == 1 else 30
						if pm == 30:
							date_ = request.session['date_vence']
							_date = date_.split('-')
							dates = list(map(int, _date))
							days = Count_Days(dates)
						print(pm)
						Payment_Form_Invoice_POS(
							payment_form_id = Payment_Form.objects.get(pk = request.session['payment_form']),
							payment_method_id = Payment_Method.objects.get(_id = pm),
							payment_due_date = date.today() if pm == 10 else request.session['date_vence'],
							duration_measure = 0 if pm == 10 else days,
							pos = POS.objects.filter(number = t.codificar(str(consecutive.number)),company = company).last()
						).save()
				# di.Discount(str(j['Código']),int(j['Cantidad']))
				if pm == 30:
					Wallet_POS(
						pos = POS.objects.filter(number = t.codificar(str(consecutive.number)),company = company).last(),
						client = Client.objects.get(pk = request.session['client']),
						price = t.codificar(str(price)),
						date = t.codificar(str(date.today())),
						company = company,
					).save()
					n += 1
					request.session['client']
				n = consecutive.number + 1
				consecutive.number = n
				consecutive.save()
				success = True
			return HttpResponse(success)
		except Exception as e:
			print(e)
			return HttpResponse(e)

def Payment_Forms_POS(request):
	if request.is_ajax():
		print(request.GET.get("pk"))
		request.session['payment_form'] = request.GET.get("pk")
		return HttpResponse(request.session['payment_form'])

import sqlite3

@storeInQueue
def Invoice_Data(request):
	company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
# 	conn = sqlite3.connet('/home/sistemadministrativo/mifacturacion/db.sqlite3')
# 	c = conn.cursor()
# 	c.execute("select DISTINCT(number) from pos_pos LIMIT 10")
	_invoice = POS.objects.filter(company = company).values_list('number', flat=True).distinct()

	data = []
	for j in _invoice:
		if j not in data:
			data.append(j)
	_data = []
	for i in data:
		_i = POS.objects.filter(company=company,number = i).last()
		_data.append(
				{
				'pk': t.decodificar(str(_i.number)),
				'number':t.decodificar(str(_i.number)),
				'date': t.decodificar(str(_i.date)),
				'client':t.decodificar(str(_i.client.name)),
				'state':t.decodificar(str(_i.state)),
				'totals':round(_i.Totals())
			}
		)
	return _data

def List_Invoice_POS(request):
	u = threading.Thread(target=Invoice_Data,args=(request,), name='PDF')
	u.start()
	data = my_queue.get()
	return render(request,'pos/list_invoice.html',{'invoice':data})

def Print_Invoice(request,number):
    invoice= POS.objects.filter(number = t.codificar(str(number)))
    _invoice = POS.objects.filter(number = t.codificar(str(number))).last()
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
            'price':i.Base_Product_WithOut_Discount() / float(t.decodificar(str(i.quanty))),
            'tax':t.decodificar(str(i.tax)),
            'tax_value':i.Tax_Value(),
            'ICO':t.decodificar(str(i.ipo)),
            'discount':0,
            'subtotal':round(float(i.Base_Product_WithOut_Discount()),2),
            'totals':i.Totals()
        }
        for i in invoice
    ]
    client = {
        'document':t.decodificar(str(_invoice.client.identification_number)),
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
    if request.is_ajax():
        return HttpResponse(json.dumps(data))
    return render(request,'invoice.html', {
											'invoice':data,'client':client,'company':company,
											'totals':total,'subtotal':subtotal,'tax':tax,'date':_date,'pf':pf,'number_invoice':number,
											'data_pf':_data_pf
										 })


def Credit_Notes(request):
	if request.is_ajax:
		company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
		invoice = POS.objects.filter(number = t.codificar(str(request.GET.get("pk"))), company = company)
		print(invoice)
		Credit_Note_POS(
			pos = invoice.last(),
			company = company,
			date = date.today()
		).save()
		for i in invoice:
			inv = Inventory.objects.get(code = i.code,company = company)
			n = int(t.decodificar(str(inv.quanty))) + int(t.decodificar(str(i.quanty)))
			inv.quanty = t.codificar(str(n))
			inv.save()
			if int(t.decodificar(str(inv.quanty))) > 0:
				inv.exhausted = False
				inv.save()
			i.state = t.codificar(str("Se aplico nota crédito"))
			i.save()
		return HttpResponse(1)


def List_Credit_Note_POS(request):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	cn = Credit_Note_POS.objects.filter(company = company)
	_data = [
			{
				'pk':i.pk,
				'number':t.decodificar(str(i.pos.number)),
				'date':i.date,
				'client':t.decodificar(str(i.pos.client.name)),
				'state':t.decodificar(str(i.pos.state)),
				'invoice':t.decodificar(str(i.pos.number))
			}
			for i in cn
		]


	return render(request,'pos/credit_note_pos.html',{'invoice':_data})





from jinja2 import Environment, FileSystemLoader
from template.make_pdf import *
import os,constants

def Create_PDF_Invoice(request,pk):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	invoice = POS.objects.filter(number = t.codificar(str(pk)), company = company )
	env = Environment(loader=FileSystemLoader("/home/sistemadministrativo/mifacturacion/template"))
	template = env.get_template("credit_note_sample.html")
	name_doc = "POS-"+str(company.prefix)+str(pk)
	print(invoice.last().ipo,'Ipo')

	_data = [
		{
			'code':t.decodificar(str(i.code)),
			"name":t.decodificar(str(i.description)),
			"quanty":Thousands_Separator(round(float(t.decodificar(str(i.quanty))))),
			"price":Thousands_Separator(round(float(t.decodificar(str(i.price))),2)),
			'tax':'0',
			'tax_value':Thousands_Separator(round(float(t.decodificar(str(i.tax))),2)),
			'ico':t.decodificar(str(i.ipo)),
			'discount':Thousands_Separator(i.Totals_Discount()),
			'totals_tax':Thousands_Separator(i.Tax_Value()),
			'totals':Thousands_Separator(i.Base_Product_WithOut_Discount())
		}
		for i in invoice
	]


	subtotal = 0
	tax = 0
	ico = 0
	for i in invoice:
		subtotal += i.Base_Product_WithOut_Discount()
		tax += round(i.Tax_Value()) + round(float(t.decodificar(str(i.ipo))))
		ico += round(float(t.decodificar(str(i.ipo))))
	subtotal_ = Thousands_Separator(round(subtotal))

	_payment_form = Payment_Form_Invoice_POS.objects.get(pos = invoice.last())

	data = {
		'name_client':t.decodificar(str(invoice.last().client.name)),
		"email_client":t.decodificar(str(invoice.last().client.email)),
		"address_client":t.decodificar(str(invoice.last().client.address)),
		'phone_client':t.decodificar(str(invoice.last().client.phone)),
		"data": _data,
		'subtotal_invoice':subtotal_,
		'total_invoice':Thousands_Separator(round((subtotal + tax))),
		'title':name_doc,
		'name_company':t.decodificar(str(invoice.last().empleoyee.company.business_name)),
		'address_company':t.decodificar(str(invoice.last().empleoyee.company.address)),
		'email_company':t.decodificar(str(invoice.last().empleoyee.company.email)),
		'phone_company':t.decodificar(str(invoice.last().empleoyee.company.phone)),
		'resolution_number':invoice.last().empleoyee.company.resolution_number,
		'type_organization':invoice.last().empleoyee.company.type_organization.name,
		'payment_form':str(_payment_form.payment_method_id.name).replace('é','e'),
		'duration_measure':_payment_form.payment_due_date,
		'days_measure':_payment_form.duration_measure,
		'date':t.decodificar(str(i.date)),
		'total_letters': numero_a_letras(subtotal + tax).upper(),
		'type_invoice':"Factura POS",
		'consecutive':t.decodificar(str(invoice.last().number)),
		'logo':'https://c2.staticflickr.com/4/3123/2710432413_9f8aedce5f.jpg',
		'ico':ico,
		'note':t.decodificar(str(invoice.last().notes))
	}

	tax = {}
	tax_0 = 0
	tax_5 = 0
	tax_19 = 0
# 	for i in invoice:
# 		inventory = Inventory.objects.get(code = i.code)
# 		tax_product = t.decodificar(str(inventory.tax))
# 		if int(tax_product) == 0:
# 			tax_0 += round(float(t.decodificar(str(inventory.price))))
# 		if int(tax_product) == 5:
# 			tax_5 += round(i.Tax_Value())
# 		if int(tax_product) == 19:
# 			tax_19 += round(i.Tax_Value())

# 	if tax_19 > 0:
# 		data['tax_19'] = Thousands_Separator(tax_19)
# 	if tax_5 > 5:
# 		data['tax_5'] = Thousands_Separator(tax_5)
# 	if tax_0 > 0:
# 		data['tax_0'] = Thousands_Separator(tax_0)

	html = template.render(data)
	file = open("/home/sistemadministrativo/mifacturacion/template/pdfs/"+name_doc+".html",'w')
	file.write(html)
	file.close()
	path = "/home/sistemadministrativo/mifacturacion/media/company/2"
	GeneratePDF(name_doc,path)
	os.remove('/home/sistemadministrativo/mifacturacion/template/pdfs/'+name_doc+'.html')


def GetPDF_POS(request,pk):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	name_doc = "POS-"+str(company.prefix)+str(pk)
	path_dir = "/home/sistemadministrativo/mifacturacion/media/company/2/"+name_doc+'.pdf'
	Create_PDF_Invoice(request,pk)
	return FileResponse(open(path_dir,'rb'),content_type='application/pdf')



def Send_Email(request):
	if request.is_ajax():
		u = threading.Thread(target=Send_Email_PDF,args=(request,request.GET.get('value')), name='PDF')
		u.start()
		data = my_queue.get()
		return HttpResponse(data)
	return redirect('/')




@storeInQueue
def Send_Email_PDF(request,pk):
	Create_PDF_Invoice(request,pk)
	import smtplib
	import requests
	import json
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.base import MIMEBase
	from email import encoders
	token = get_random_string(length=96)
	Token(
		token = token
	).save()
	company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	client = Invoice.objects.filter(number = t.codificar(str(pk)),company = company).last()
	remitente = 'evansoftservices@gmail.com'
	destinatarios = ["carlosdelaguila917@gmail.com",str(company.email),str(client.email)]
	asunto = 'Aceptación de factura N° '#+str(factura.prefijo)+str(factura.numero)
	html = """
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
		<html xmlns="http://www.w3.org/1999/xhtml">

		<head>
		  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		  <title>Factura electronica</title>
		  <style type="text/css">
		  body {margin: 0; padding: 0; min-width: 100%!important;}
		  img {height: auto;}
		  .content {width: 100%; max-width: 600px;}
		  .header {padding: 40px 30px 20px 30px;}
		  .innerpadding {padding: 30px 30px 30px 30px;}
		  .borderbottom {border-bottom: 1px solid #f2eeed;}
		  .subhead {font-size: 15px; color: #ffffff; font-family: sans-serif; letter-spacing: 10px;}
		  .h1, .h2, .bodycopy {color: #153643; font-family: sans-serif;}
		  .h1 {font-size: 33px; line-height: 38px; font-weight: bold;}
		  .h2 {padding: 0 0 15px 0; font-size: 24px; line-height: 28px; font-weight: bold;}
		  .bodycopy {font-size: 16px; line-height: 22px;}
		  .button {text-align: center; font-size: 18px; font-family: sans-serif; font-weight: bold; padding: 0 30px 0 30px;}
		  .button a {color: #ffffff; text-decoration: none;}
		  .footer {padding: 20px 30px 15px 30px;}
		  .footercopy {font-family: sans-serif; font-size: 14px; color: #ffffff;}
		  .footercopy a {color: #ffffff; text-decoration: underline;}

		  @media only screen and (max-width: 550px), screen and (max-device-width: 550px) {
		  body[yahoo] .hide {display: none!important;}
		  body[yahoo] .buttonwrapper {background-color: transparent!important;}
		  body[yahoo] .button {padding: 0px!important;}
		  body[yahoo] .button a {background-color: #e05443; padding: 15px 15px 13px!important;}
		  body[yahoo] .unsubscribe {display: block; margin-top: 20px; padding: 10px 50px; background: #2f3942; border-radius: 5px; text-decoration: none!important; font-weight: bold;}
		  }

		  </style>
		</head>

		<body yahoo bgcolor="#f6f8f1">
		<table width="100%" bgcolor="#f6f8f1" border="0" cellpadding="0" cellspacing="0">
		<tr>
		  <td>
		    <!--[if (gte mso 9)|(IE)]>
		      <table width="600" align="center" cellpadding="0" cellspacing="0" border="0">
		        <tr>
		          <td>
		    <![endif]-->
		    <table bgcolor="#ffffff" class="content" align="center" cellpadding="0" cellspacing="0" border="0">
		      <tr>
		        <td style=" background-image: linear-gradient(to left top, #0db9f8, #0790be, #0c6988, #0f4456, #0c222a);" class="header">
		          <table width="70" align="left" border="0" cellpadding="0" cellspacing="0">
		            <tr>
		              <td height="70" style="padding: 0 20px 20px 0;">
		                <img class="fix" src="https://scontent.feoh1-1.fna.fbcdn.net/v/t39.30808-6/236831317_373363691048746_6124884787829342845_n.jpg?_nc_cat=109&ccb=1-5&_nc_sid=09cbfe&_nc_eui2=AeHC2pd9PxQIaMrlI6hGR7_KM4Mr_Q2yPQkzgyv9DbI9CTyKT7YfoHSHHmKHZ07ufKLotsaDLkQ49Do25yRYbBsP&_nc_ohc=s0gnbPs5NWcAX-vebaw&_nc_ht=scontent.feoh1-1.fna&oh=00_AT9FfGCvn1UA0mqFqunFbxN3WqHc0WaGX5k2U8ysTk3lxw&oe=62509A4E" width="70" height="70" border="0" alt="" />
		              </td>
		            </tr>
		          </table>
		          <!--[if (gte mso 9)|(IE)]>
		            <table width="425" align="left" cellpadding="0" cellspacing="0" border="0">
		              <tr>
		                <td>
		          <![endif]-->
		          <table class="col425" align="left" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 425px;">
		            <tr>
		              <td height="70">
		                <table width="100%" border="0" cellspacing="0" cellpadding="0">
		                  <!-- <tr>
		                    <td class="subhead" style="padding: 0 0 0 3px;">
		                      <span style="color: white;">$(company_name)</span>
		                    </td>
		                  </tr> -->
		                  <tr>
		                    <td class="h1" style="padding: 5px 0 0 0;">
		                     <span style="color: white;">$(company_name)</span>
		                    </td>
		                  </tr>
		                </table>
		              </td>
		            </tr>
		          </table>
		          <!--[if (gte mso 9)|(IE)]>
		                </td>
		              </tr>
		          </table>
		          <![endif]-->
		        </td>
		      </tr>
		      <tr>
		        <td class="innerpadding borderbottom">
		          <table width="100%" border="0" cellspacing="0" cellpadding="0">
		            <tr>
		              <td class="h2">
		               Hola,$(client) !
		              </td>
		            </tr>
		            <tr>
		              <td class="bodycopy">
		                Mediante la presente, le informamos del envío de la facturación electrónica de venta N° $(number_invoice).<br>
		                Cualquier duda o inquietud nos puede informar por medio de algunas de las opciones que le presentamos por este medio.
						<br>
						<br>
						<span style="font-size: 25px;font-weight: bold;">NOTA:&nbsp;</span><span style="font-size:18px;">ANTES DE SELECCIONAR CUALQUIER OPCIÓN POR FAVOR VERIFIQUE BIEN LOS DATOS DE SU FACTURA</span>
		              </td>
		            </tr>
		          </table>
		        </td>
		      </tr>
		      <tr>
		        <td class="innerpadding borderbottom">
		          <!-- <table width="115" align="left" border="0" cellpadding="0" cellspacing="0">
		            <tr>
		              <td height="115" style="padding: 0 20px 20px 0;">
		                <img class="fix" src="http://theriosoft.com/static/vendors/itemsHome/facturaPdf.png" width="115" height="115" border="0" alt="" />
		              </td>
		            </tr>
		          </table> -->
		          <!--[if (gte mso 9)|(IE)]>
		            <table width="380" align="left" cellpadding="0" cellspacing="0" border="0">
		              <tr>
		                <td>
		          <![endif]-->
		          <table class="col380" align="left" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 380px;">
		            <tr>
		              <td>
		                <table width="100%" border="0" cellspacing="0" cellpadding="0">

		                  <tr>
		                    <td style="padding: 20px 0 0 0;">
		                      <table class="buttonwrapper" style="background-image: linear-gradient(to left bottom, #0db9f8, #0790be, #0c6988, #0f4456, #0c222a);" border="0" cellspacing="0" cellpadding="0">
		                        <tr>
		                          <td class="button" height="45">
		                            <a href="http://localhost:8000/invoice/acceptance/$(token)/$(pk_company)/$(number_invoice)" target="_blank">Aceptar</a>
		                          </td>
		                          <td>&nbsp;&nbsp;&nbsp;</td>
		                          <td class="button" height="45">
		                            <a href="http://localhost:8000/invoice/rejection/$(token)/$(pk_company)/$(number_invoice)" target="_blank">Rechazar</a>
		                          </td>
		                        </tr>
		                        </tr>
		                      </table>
		                    </td>
		                  </tr>
		                </table>
		              </td>
		            </tr>
		          </table>
		          <!--[if (gte mso 9)|(IE)]>
		                </td>
		              </tr>
		          </table>
		          <![endif]-->
		        </td>
		      </tr>


		    </table>
		    <!--[if (gte mso 9)|(IE)]>
		          </td>
		        </tr>
		    </table>
		    <![endif]-->
		    </td>
		  </tr>
		</table>

		</body>
		</html>
	"""

	html = html.replace("$(company_name)",t.decodificar(str(company.business_name)))
	html = html.replace("$(client)",t.decodificar(str(client.client.name)))
	html = html.replace("$(token)",str(token))
	html = html.replace("$(number_invoice)",str(pk))
	html = html.replace("$(pk_company)",str(company.pk))

	pdf = str("FES-"+str(company.prefix)+str(pk)+".pdf")
	path = "/home/sistemadministrativo/mifacturacion/media/company/"+t.decodificar(str(company.documentIdentification))+"/FES-"+str(company.prefix)+str(pk)+".pdf"
	ruta_adjunto = path
	nombre_adjunto = pdf
	mensaje = MIMEMultipart()

	mensaje['From'] = remitente
	mensaje['To'] = ", ".join(destinatarios)
	mensaje['Subject'] = asunto
	mensaje.attach(MIMEText(html,'html'))


	archivo_adjunto = open(ruta_adjunto, 'rb')

	adjunto_MIME = MIMEBase('application', 'octet-stream')
	adjunto_MIME.set_payload((archivo_adjunto).read())
	encoders.encode_base64(adjunto_MIME)
	adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)

	mensaje.attach(adjunto_MIME)
	sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
	sesion_smtp.starttls()
	texto = mensaje.as_string()
	usuario = "evansoftservices@gmail.com"
	clave = "megatron12#$"
	sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
	sesion_smtp.starttls()
	texto = mensaje.as_string()
	remitente = usuario
	sesion_smtp.login(usuario,clave)
	sesion_smtp.sendmail(remitente, destinatarios, texto)
	sesion_smtp.quit()
	return "Exito"


from notification.models import Notification_Acceptance

def acceptance(request,token,company,pk):
	try:
		Token.objects.get(token = token).delete()
	except Token.DoesNotExist:
		return render(request,"token_exp.html")
	client = Invoice.objects.filter(number=t.codificar(str(pk))).last()
	Notification_Acceptance(
		invoice = client,
		company = Company.objects.get(pk = company),
		acceptance = True,
		date = date.today(),
		time = datetime.now().strftime('%H:%M')
	).save()
	sa = gTTS("El cliente "+t.decodificar(str(client.client.name))+" aceptó la Factura electrónica número "+t.decodificar(str(client.number)))
	path_dir = "/home/sistemadministrativo/mifacturacion/static/company/2"
	if not os.path.exists(path_dir):
		print("No existo ACEPT")
		os.makedirs(path_dir)
	sa.save(path_dir+'/message.mp3')
	return render(request,'acceptance.html',{'number':pk})



def rejection(request,token,company,pk):

	if request.method == "POST":
		client = Invoice.objects.filter(number=t.codificar(str(pk))).last()
		Notification_Acceptance(
			invoice = client,
			company = Company.objects.get(pk = company),
			notes = request.POST.get("notes"),
			acceptance = False,
			date = date.today(),
			time = datetime.now().strftime('%H:%M')
		).save()
		sa = gTTS("El cliente "+t.decodificar(str(client.client.name))+" rechazó la Factura electrónica número "+t.decodificar(str(client.number)))
		path_dir = "/home/sistemadministrativo/mifacturacion/static/company/2"
		if not os.path.exists(path_dir):
			print("No existo ACEPT")
			os.makedirs(path_dir)
		sa.save(path_dir+'/message.mp3')

		return render(request,'thanks.html')
	try:
		Token.objects.get(token = token).delete()
	except Token.DoesNotExist:
		return render(request,"token_exp.html")
	return render(request,'rejection.html',{'number':pk})






