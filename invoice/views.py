from django.http import HttpResponse,JsonResponse,FileResponse
from django.shortcuts import render,redirect
from .models import *
from api.translator import Translator
import time, threading, queue,json,requests
from client.models import Client
from inventory.models import Inventory,Discount_Inventory,Shopping_Inventory
from django.http.request import QueryDict
from datetime import datetime,date
from api.SendInvoiceDian import send_invoice_dian
from date import Count_Days
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from from_number_to_letters import numero_a_letras,Thousands_Separator
from api.models import Token
from django.utils.crypto import get_random_string
from gtts import gTTS
from playsound import playsound
from base64 import b64decode
import base64


t = Translator()
my_queue = queue.Queue()
count = 0

def storeInQueue(f):
  def wrapper(*args):
  	global my_queue
  	my_queue.put(f(*args))
  return wrapper

@storeInQueue
def Invoice_Data(request):
	company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	_invoice = Invoice.objects.filter(company = company).distinct()
	try:
		import sqlite3
		con = sqlite3.connect('db.sqlite3')
		c = con.cursor()
		c.execute("""
				SELECT DISTINCT i.number,c.name,i.prefix,i.state,i.date from invoice_Invoice as i 
				inner join client_Client as c on c.id = i.client_id
				where i.company_id = """+str(company.pk)+""" order by i.number desc limit 100
		""")
		data = c.fetchall()

		_data = [
			{
				'pk':t.decodificar(str(i[0])),
				'number':t.decodificar(str(i[2]))+'-'+t.decodificar(str(i[0])),
				'date':t.decodificar(str(i[4])),
				'client':t.decodificar(str(i[1])),
				'state':t.decodificar(str(i[3]))
			}
			for i in data
		]
		return _data
	except Exception as e:
		return []
	

def List_Invoice(request):
	start = time.time()
	u = threading.Thread(target=Invoice_Data,args=(request,), name='Invoice')
	u.start()
	data = my_queue.get()
	if request.is_ajax():
		_inv = Invoice.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))), number =  t.codificar(str(request.GET.get('pk'))))
		for i in _inv:
			_i = Inventory.objects.get(code =i.code)
			n = int(t.decodificar(str(_i.quanty))) + int(t.decodificar(str(i.quanty)))
			_i.quanty = t.codificar(str(n))
			_i.save()
			i.delete()
		return HttpResponse("")
	return render(request,'fe/list_invoice.html',{'invoice':data})

def Create_Invoice(request):
	company = Company.objects.get(documentIdentification=t.codificar(str(request.session['nit_company'])))
	client = Client.objects.filter(company = company)
	inventory = Inventory.objects.filter(company = company)
	request.session['payment_form'] = 1
	if request.is_ajax():
		request.session['client'] = request.GET.get("pk")
		return HttpResponse(request.GET.get("pk"))
	data_client = [
									{'name':t.decodificar(str(i.name)),'code':i.pk}
									for i in client
								]
	data_inventory = [{'code':t.decodificar(str(i.code)),'name':t.decodificar(str(i.name))} for i in inventory]
	pf = Payment_Form.objects.all()
	ce = Consecutive_Elec.objects.get(company = company).number
	if 'payment_form' not in request.session:
		request.session['payment_form'] = 1
	global count
	count = 0
	return render(request,'fe/create_invoice.html',{'client':data_client,'inventory':data_inventory,'cod_bars':company.cod_bars,'pf':pf,'ce':ce})

def a(sms):
	return t.decodificar(str(sms))

def GetProducts(request):
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

def Vence(request):
	if request.is_ajax():
		request.session['date_vence'] = request.GET.get('date')
		request.session['days'] = request.GET.get('days')
		return HttpResponse("")

def Save_Invoice_FE(request):
	if request.is_ajax():
		data = request.GET
		success = False
		for i in data:
			_data = json.loads(i)
			if len(_data) == 0:
				break
			di = Discount_Inventory()
			company = Company.objects.get(documentIdentification=t.codificar(str(request.session['nit_company'])))
			consecutive = Consecutive_Elec.objects.get(company = company)
			pm = 0
			price = 0
			for j in _data:
				n = 0
				Invoice(
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
					state = t.codificar(str("Sin enviar a la DIAN")),
					empleoyee = Empleoyee.objects.get(pk = request.session['empleoyee_pk'])
				).save()
				price += float(j['Costo'])
				if n == 0:
					pm = 10 if int(request.session['payment_form']) == 1 else 30
					if pm == 30:
						date_ = request.session['date_vence']
						_date = date_.split('-')
						dates = list(map(int, _date))
						days = Count_Days(dates)
					Payment_Form_Invoice(
						payment_form_id = Payment_Form.objects.get(pk = request.session['payment_form']),
						payment_method_id = Payment_Method.objects.get(_id = pm),
						payment_due_date = date.today() if pm == 10 else request.session['date_vence'],
						duration_measure = 0 if pm == 10 else days,
						invoice = Invoice.objects.filter(number = t.codificar(str(consecutive.number)),company = company).last()
					).save()
				di.Discount(str(j['Código']),int(j['Cantidad']))
			if pm == 30:
				Wallet(
					invoice = Invoice.objects.filter(number = t.codificar(str(consecutive.number)),company = company).last(),
					client = Client.objects.get(pk = request.session['client']),
					price = t.codificar(str(price)),
					date = t.codificar(str(date.today())),
					company = company
				).save()
				n += 1
				request.session['client']
			n = consecutive.number + 1
			consecutive.number = n 
			consecutive.save()
			success = True
		return HttpResponse(success)

def Payment_Forms(request):
	if request.is_ajax():
		request.session['payment_form'] = request.GET.get("pk")
		return HttpResponse(request.session['payment_form'])

def Print_Invoice(request):
	return render(request,'invoice.html')

@storeInQueue
def Sending(request,pk):
	sd = send_invoice_dian(pk,request.session['nit_company'])
	sd.Send_Electronic_Invoice()
	return True

def Send_Dian(request,pk):
	u = threading.Thread(target=Sending,args=(request,pk), name='PDF')
	u.start()
	return redirect('List_Invoice')

def Credit_Notes(request,number):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(number = t.codificar(str(number)), company = company)
	Credit_Note(
		invoice = invoice.last(),
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
	return redirect('List_Invoice')

@storeInQueue
def Create_NoteCredit_Product(request):
	print("aplicando notecredit by product")

def NoteCreditProduct(request):
	if request.is_ajax():
		company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
		inv = Inventory.objects.get(code = t.codificar(str(request.GET.get("pk"))),company = company)
		n = int(t.decodificar(str(inv.quanty))) + int(request.GET.get('quanty'))
		inv.quanty = t.codificar(str(n))
		inv.save()
		_i = Invoice.objects.filter(number = t.codificar(str(request.GET.get('consecutive'))),company = company)
		if len(_i) > 1:
			for j in Invoice.objects.filter(number = t.codificar(str(request.GET.get('consecutive'))),code = t.codificar(str(request.GET.get('pk'))),company = company):
				j.delete()
			u = threading.Thread(target=Create_NoteCredit_Product,args=(request,), name='PDF')
			u.start()

		return HttpResponse(request.GET.get("pk"))
	

def NoteCredit_From_JS(request):
	if request.is_ajax():
		print(request.session['number_invoice'])
		company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
		invoice = Invoice.objects.get(number = t.codificar(str(request.session['number_invoice'])), company = company)
		invoice.state = t.codificar(str("Se aplico nota crédito"))
		Credit_Notes(request,request.session['number_invoice'])
		del request.session['number_invoice']
		return HttpResponse("Hola notecredit")

def List_Credit_Note(request):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	cn = Credit_Note.objects.filter(company = company)
	_data = [
			{
				'pk':i.pk,
				'number':t.decodificar(str(i.invoice.prefix))+'-'+t.decodificar(str(i.invoice.number)),
				'date':i.date,
				'client':t.decodificar(str(i.invoice.client.name)),
				'state':t.decodificar(str(i.invoice.state)),
				'invoice':t.decodificar(str(i.invoice.number))
			}
			for i in cn
		]


	return render(request,'fe/credit_note_fe.html',{'invoice':_data})


from jinja2 import Environment, FileSystemLoader
from template.make_pdf import *
import os,constants

def Create_PDF_Invoice(request,pk):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(number = t.codificar(str(pk)), company = company )
	env = Environment(loader=FileSystemLoader("template"))
	template = env.get_template("credit_note_sample.html")
	name_doc = "FES-"+str(company.prefix)+str(pk)

	_data = [
		{
			'code':t.decodificar(str(i.code)),
			"name":t.decodificar(str(i.description)),
			"quanty":Thousands_Separator(round(float(t.decodificar(str(i.quanty))))),
			"price":Thousands_Separator(round(float(t.decodificar(str(i.price))),2)),
			'tax':t.decodificar(str(Inventory.objects.get(code = i.code).tax)),
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
	for i in invoice:
		subtotal += i.Base_Product_WithOut_Discount()
		tax += i.Tax_Value()
	subtotal_ = Thousands_Separator(round(subtotal,2))

	
	_payment_form = Payment_Form_Invoice.objects.get(invoice = invoice.last())

	data = {
		'name_client':t.decodificar(str(invoice.last().client.name)),
		"email_client":t.decodificar(str(invoice.last().client.email)),
		"address_client":t.decodificar(str(invoice.last().client.address)),
		'phone_client':t.decodificar(str(invoice.last().client.phone)),
		"data": _data,
		'cufe':'a7e53384eb9bb4251a19571450465d51809e0b7046101b87c4faef96b9bc904cf7f90035f444952dfd9f6084eeee2457433f3ade614712f42f80960b2fca43ff',
		'subtotal_invoice':subtotal_,
		'total_invoice':Thousands_Separator(round(subtotal + tax,2)),
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
		'type_invoice':"Factura Electonica de venta",
		'consecutive':t.decodificar(str(invoice.last().number)),
		'logo':'https://c2.staticflickr.com/4/3123/2710432413_9f8aedce5f.jpg'
	}
	
	tax = {}
	tax_0 = 0
	tax_5 = 0
	tax_19 = 0
	for i in invoice:
		inventory = Inventory.objects.get(code = i.code)
		tax_product = t.decodificar(str(inventory.tax))
		if int(tax_product) == 0:
			tax_0 += round(float(t.decodificar(str(inventory.price))),2)
		if int(tax_product) == 5:
			tax_5 += round(i.Tax_Value(),2)
		if int(tax_product) == 19:
			tax_19 += round(i.Tax_Value(),2)

	if tax_19 > 0:
		data['tax_19'] = Thousands_Separator(tax_19)
	if tax_5 > 5:
		data['tax_5'] = Thousands_Separator(tax_5)
	if tax_0 > 0:
		data['tax_0'] = Thousands_Separator(tax_0)

	html = template.render(data)
	file = open("template/pdfs/"+name_doc+".html",'w')
	file.write(html)
	file.close()
	path = "media/company/"+request.session['nit_company']
	GeneratePDF(name_doc,path)
	os.remove('template/pdfs/'+name_doc+'.html')


def GetPDF(request,pk):
	company = Company.objects.get(documentIdentification= t.codificar(str(request.session['nit_company'])))	
	name_doc = "FES-"+str(company.prefix)+str(pk)
	path_dir = "media/company/"+request.session['nit_company']+'/'+name_doc+'.pdf'
	if not os.path.exists(path_dir):
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
	print(t.decodificar(str(client.client.email)))

	destinatarios = ["carlosdelaguila917@gmail.com",t.decodificar(str(company.email)),t.decodificar(str(client.client.email))]
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
	path = "media/company/"+t.decodificar(str(company.documentIdentification))+"/FES-"+str(company.prefix)+str(pk)+".pdf"
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
	clave = "xarauthaynkevvpj"
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
	sa = gTTS("El cliente "+t.decodificar(str(client.client.name))+" aceptó la Factura electrónica número "+t.decodificar(str(client.number)),lang='es',tld='com.mx')
	path_dir = "./static/company/"+str(request.session['nit_company'])
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
		sa = gTTS("El cliente "+t.decodificar(str(client.client.name))+" rechazó la Factura electrónica número "+t.decodificar(str(client.number)),lang='es',tld='com.mx')
		path_dir = "./static/company/"+str(request.session['nit_company'])
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



























