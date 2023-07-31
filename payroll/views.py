from django.http import HttpResponse
from django.shortcuts import render,redirect
from empleoyee.models import Empleoyee
from company.models import Company
from api.translator import Translator
from .payroll_logic import Declare_Payroll
from .models import *
from from_xlsx_to_base64 import *
import json,requests,pandas as pd,queue,threading
from from_number_to_letters import numero_a_moneda
from datetime import datetime,timedelta
from datetime import date

t = Translator()
my_queue = queue.Queue()

def storeInQueue(f):
  def wrapper(*args):
  	global my_queue
  	my_queue.put(f(*args))
  return wrapper

def Send_Payroll(request):
	c = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	p = Payroll_Document.objects.get(company = c).payroll_document.url
	df = pd.read_excel('.'+p)
	df.dropna()
	
	_data_employee = [
		{
			'name':str(df['Nombre'].values[i])+' '+str(df['Primer Apellido'].values[i]),
			'documentI':df['Cedula Empleado'].values[i],
			'salary':df['Sueldo Base'].values[i],
			'transportation_allowance':df['Subsidio de Transport'].values[i],
			'worked_days':df['Dias Trabajdos'].values[i],
			'total_payroll':round(df['Sueldo Mensual'].values[i])
		}
		for i in range(len(df.dropna()))
	]

	total = 0
	for i in range(len(df.dropna())):
		total += float(df['Sueldo Mensual'].values[i])

	if request.is_ajax():
		u = threading.Thread(target=Send_Dian_Payroll,args=(request,), name='Payroll')
		u.start()
		return HttpResponse("Enviando Nomina")


	return render(request,'payroll/send_payroll.html',{'data':_data_employee,'total_payroll':round(total),'letter':numero_a_moneda(round(total))})

@storeInQueue
def Send_Dian_Payroll(request):
	if request.is_ajax():
		# token = "656aa7a5d876bc6d8c21d5df54937e51c85fd49f6802da7e0a56676b6c3afa76"
		c = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
		p = Payroll_Document.objects.get(company = c).payroll_document.url
		df = pd.read_excel('.'+p)
		for i in range(len(df)):
			dp = Declare_Payroll('.'+p,df['Cedula Empleado'].values[i],c)
			payload = dp.Preview()
			break


			



def Update_Payroll_Document(request):
	message = ""
	# Dates_Payroll()
	
	meses = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
	if request.method == 'POST':
		c = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
		try:
			p = Payroll_Document.objects.get(company = c)
		except Payroll_Document.DoesNotExist:
			p = None
		if p is not None:
			import os
			os.remove('./media/'+str(p.payroll_document))
			p.payroll_document = request.FILES.get('file')
			p.month = meses[datetime.today().month]
			p.anio = date.today().year
			p.save()
		else:
			con = Consecutive_Payroll.objects.get(company = c)
			Payroll_Document(
				company = c,
				payroll_document = request.FILES.get('file'),
				month = meses[datetime.today().month],
				anio = date.today().year,
				number = con.number
			).save()
		document = Payroll_Document.objects.get(company = c).payroll_document.url
		code = str(Create_Document64('.'+document))
		message = json.loads(BackUp_Payroll(c.pk,code[2:len(code) - 1],meses[datetime.today().month],date.today().year,con.number))

	return render(request,'payroll/update_payroll_document.html',{'message':message})

def BackUp_Payroll(company,code,month,anio,number):
	url = "http://localhost:9090/api/Create_BackUp_Payroll"
	payload = json.dumps({
	  "company": company,
	  "payroll": code,
	  'month':month,
	  'anio':anio,
	  'number':number
	})
	headers = {
	  'Content-Type': 'application/json'
	}
	response = requests.request("POST", url, headers=headers, data=payload)
	return response.text


def Dates_Payroll():
	ahora = datetime.now()
	print("Ahora: " + str(ahora))
	hace_una_semana = ahora - timedelta(days=7)
	mes = str(hace_una_semana)[5:7]
	anio = str(hace_una_semana)[0:4]

	if len(str(int(mes))) == 1:
		print('01-0'+str(int(mes) - 1 )+'-'+anio)
		print('30-0'+str(int(mes) - 1 )+'-'+anio)
	else:	
		print('01-'+str(int(mes) - 1 )+'-'+anio)
		print('30-'+str(int(mes) - 1 )+'-'+anio)



def Recovery_Payroll(request):
	c = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	pd = Payroll_Document.objects.filter(company = c)
	return render(request,'payroll/recovery_payroll.html',{'pd':pd})


def Generate_Payroll(request):
	c = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))

	if request.is_ajax():
		e = Empleoyee.objects.get(pk = request.GET.get('pk'))
		
		data = {
			'salary':t.decodificar(str(e.salary)),
			'hiring_date': t.decodificar(str(e.hiring_date))
		}
		return HttpResponse(json.dumps(data))

	empleoyee = Empleoyee.objects.filter(company = c)

	emp = [
		{
			'pk':i.pk,
			'name':t.decodificar(str(i.firstname))+' '+t.decodificar(str(i.surname))
		}
		for i in empleoyee
	]
	return render(request,'payroll/generate.html',{'data':emp})



def Save_Payroll(request):
	if request.method == 'POST':
		data = request.POST.get("")
		return HttpResponse()







