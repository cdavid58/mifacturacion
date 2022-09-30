from django.http import HttpResponse,FileResponse
from django.shortcuts import render,redirect
from company.models import Company,Files_Company,License_Company
from seller.models import Seller
from api.translator import Translator
from invoice.models import Invoice,Wallet,Payment_Form_Invoice
from empleoyee.models import Empleoyee
from datetime import date
from pos.models import POS
from .send_email import recoverypw
from django.utils.crypto import get_random_string
from api.models import Token
from .registration_request import Request
from date import Count_Days
import os,shutil,sqlite3,json
from notification.models import Notification_Acceptance
from from_number_to_letters import Thousands_Separator


t = Translator()
intentos = 1

def LogOut(request):
	path_dir_media = 'media/company/'+str(request.session['nit_company'])
	path_dir_static = 'static/company/'+str(request.session['nit_company'])
	if os.path.exists(path_dir_media):
		shutil.rmtree(path_dir_media)
		
	if os.path.exists(path_dir_static):
		shutil.rmtree(path_dir_static)
	del request.session['empleoyee_pk']
	del request.session['logo_Company']
	del request.session['name_company']
	del request.session['nit_company']
	del request.session['type_empleoyee']


	return redirect('/')

def Login(request):
	global intentos
	block = False
	block_empleoyee = False
	block_license = False
	if 'block_license' in request.session:
		block_license = True
		del request.session['block_license']
	
	if request.method == 'POST':
		try:
			email = t.codificar(str(request.POST.get("user")))
			pwd = t.codificar(str(request.POST.get("passwd")))
			v_e = Validate_Email(request,email)
			v_p = Validate_Pass(request,pwd)
			if v_e is not None and v_p is not None:
				user = v_e
				if not user.company.block:
					if not user.block:
						request.session['empleoyee_pk'] = user.pk
						request.session['logo_Company'] = user.company.logo.url
						request.session['name_company'] = t.decodificar(user.company.business_name)
						request.session['nit_company'] = t.decodificar(user.company.documentIdentification)
						request.session['type_empleoyee'] = t.decodificar(user.type)
						return redirect('Index')
					else:
						block_empleoyee = True
				else:
					block = True
			elif v_e is None and v_p is None:
				print('No exist')
				pass
			else:
				user_1 = v_e
				user_2 = v_p
				if not user_1.block or not user_2.block:
					if user_1 is not None and user_2 is None:
						intentos += 1
					elif user_1 is None and user_2 is not None:
						intentos += 1
					if intentos == 3:
						if user_1 is not None:
							user_1.block = True
							user_1.save()
							intentos = 0
						elif user_2 is not None:
							user_2.block = True
							user_2.save()
							intentos = 0
				else:
					block_empleoyee = True
		except Exception as e:
			pass
	return render(request,'home/login.html',{'block':block,'e':block_empleoyee,'block_license':block_license})

def Validate_Email(request,email):
	try:
		user = Empleoyee.objects.get(user=t.codificar(str(request.POST.get("user"))))
		return user
	except Empleoyee.DoesNotExist:
		return None

def Validate_Pass(request,pwd):
	try:
		user = Empleoyee.objects.get(passwd = t.codificar(str(request.POST.get("passwd"))))
		return user
	except Empleoyee.DoesNotExist:
		return None
	
def Register(request):
	if request.method == 'POST':
		token = get_random_string(length=10)
		name = request.POST.get('name')
		phone = request.POST.get('phone')
		email = request.POST.get('email')
		Token(
			token = token
		).save()
		Request(name,phone,email,token)
		return redirect('/')
	return render(request,'home/register.html')	

def Vale_Requested(request,token):
	
	if request.method == 'POST':
		file = request.FILES.getlist("file")
		Files_Company(
			rut = file[0],
			chamber_of_commerce = file[1],
			img_document_identification = file[2],
			name_company = t.codificar(str(request.POST.get("name_company"))),
			documentIdentification = t.codificar(str(request.POST.get("nit"))),
			seller = request.POST.get("cod_seller")
		).save()
		return render(request,'home/response.html')

	try:
		token = Token.objects.get(token = token)
		token.delete()
	except Token.DoesNotExist:
		return render(request,"home/served.html")

	return render(request,'home/register_company.html')

def Mora_FE(request,company):
	_invoice = Invoice.objects.filter(company = company)
	clients = 0
	for i in _invoice:
		try:
			w = Payment_Form_Invoice.objects.get(invoice = i)
			if w is not None:
				if int(w.duration_measure) < 0:
					clients += 1
		except Exception as e:
			pass
	return clients

def Index(request):
	total = 0
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	_invoice = Invoice.objects.filter(company = company,date = t.codificar(str(date.today()))).values_list('number','price','tax').distinct()

	
	con = sqlite3.connect("db.sqlite3")
	cursor = con.cursor()
	cursor.execute("select DISTINCT number from invoice_invoice")
	data = cursor.fetchall()
	empleoyee = Empleoyee.objects.filter(company = company)
	for i in _invoice:

		total += ( float(t.decodificar(str(i[1]))) + float(t.decodificar(str(i[2]))) )
	pos = POS.objects.filter(company = company, date= t.codificar(str(date.today()))).values_list('number','price','tax').distinct()
	for j in pos:
		total += ( float(t.decodificar(str(j[1]))) + float(t.decodificar(str(j[2]))) )

	date_ = company.resolution_expiration_date
	_date = date_.split('-')
	dates = list(map(int, _date))
	days = Count_Days(dates)
	message_resolutions = ""
	error_resolution = False
	if int(days) <= 15:
		message_resolutions = "La resolucion vence en "+str(days)
		error_resolution = True
	if int(days) <= 0:
		print(days,'expired')
		error_resolution = "expired"



		

	date_ = company.certificate_expiration_date
	_date = date_.split('-')
	dates = list(map(int, _date))
	days = Count_Days(dates)
	message_certificate = ""
	error_certificate = False
	
	# if int(days) <= 15:
	# 	message_certificate = "El certificado digital vence en "+str(days)
	# 	error_certificate = True
	# if int(days) <= 0:
	# 	error_certificate = "expired"
	


	fc = License_Company.objects.get(company = company).due_date
	date_ = company.certificate_expiration_date
	_date = date_.split('-')
	dates = list(map(int, _date))
	days = Count_Days(dates)
	# print(days)
	# if int(days) <= 0:
	# 	request.session['block_license'] = True
	# 	return redirect('/')


	return render(request,'home/index.html',{
			'invoice':Thousands_Separator(len(data)),
			'pos':Thousands_Separator(len(pos)),
			'totals':Thousands_Separator(round(total,2)),
			'empleoyee':len(empleoyee),
			'error_resolutions':error_resolution,
			'error_certificate':error_certificate,
			'clients_M':Mora_FE(request,company)
		}
	)

def Recoverypw(request):
	message = ""
	if request.method == 'POST':
		try:
			request.session['email'] = t.codificar(str(request.POST.get('email')))
			try:
				company = Empleoyee.objects.get(email = request.session['email'] )
			except Empleoyee.DoesNotExist as e:
				message = "Empleoyee matching query does not exist."
				company = None

			if company is not None:
				if company.type == t.codificar("Administrador"):
					token = get_random_string(length=96)
					Token(
						token = token
					).save()
					recoverypw(company,token)
		except Company.DoesNotExist as e:
			print(e)
	return redirect('/')

def NewPW(request,pk,token):
	if request.method == 'POST':
		try:
			company = Empleoyee.objects.get(email = request.session['email'])
			company.passwd = t.codificar(request.POST.get('passwd'))
			company.save()
			return redirect('/')
		except Company.DoesNotExist:
			pass
	try:
		token = Token.objects.get(token = token)
		token.delete()
	except Token.DoesNotExist:
		return render(request,"400.html")
	return render(request,'home/recoverpw.html')



def notofitications(request):	
	if request.is_ajax():
		try:
			company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
			n = len(Notification_Acceptance.objects.filter(company = company,seen=False))
			_notofitications = Notification_Acceptance.objects.filter(company = company,seen=False).order_by('-pk')[:5]
			_data = [
				{
					'pk':i.pk,
					'date':i.date,
					'number':t.decodificar(str(i.invoice.number)),
					'acceptance':i.acceptance,
					'time':i.time
				}
				for i in _notofitications
			]
			return HttpResponse(json.dumps(_data))
		except Exception as e:
			return HttpResponse(json.dumps([]))

