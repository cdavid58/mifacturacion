from company.models import *
from data.models import *
from api.translator import Translator
from data.models import *
from invoice.models import Consecutive_Elec,Consecutive_POS,Consecutive_CreditNote
from validate import Validate_Email,Validate_Phone
from seller.models import Seller,Balance
from payroll.models import Consecutive_Payroll
from .Create_Company_API import RegisterCompanyAPI
from .Register_Resolutions import Register
import datetime

t = Translator()

class CreateCompany:

	def __init__(self,data,token,passwd):
		self.data = data
		self.token = token
		self.passwd = passwd

	def Create(self):
		try:			
			if self.Validate()[0]:
				if Validate_Email(self.data['email']):
					if Validate_Phone(self.data['phone']):
						now = datetime.datetime.utcnow()
						full_license = True if str(self.data['payment']) == "1000000" else False
						rca = RegisterCompanyAPI(self.data)
						token = rca.Register()
						Register(token)
						Company(
							documentIdentification = t.codificar(str(self.data['document_identification'])),
							type_documentI = Type_Document_Identification.objects.get(_id = self.data['type_document_identification_id']),
							type_organization = Type_Organization.objects.get(_id = self.data['type_organization_id']),
							type_regime = Type_Regime.objects.get(_id = self.data['type_regime_id']),
							business_name = t.codificar(str(self.data['business_name'])),
							municipality = Municipality.objects.get(_id = self.data['municipality_id']),
							address = t.codificar(str(self.data['address'])),
							phone = t.codificar(str(self.data['phone'])),
							email = t.codificar(str(self.data['email'])),
							certificate_generation_date = self.data['certificate_generation_date'],
							certificate_expiration_date = self.data['certificate_expiration_date'],
							resolution_generation_date = self.data['resolution_generation_date'],
							resolution_expiration_date = self.data['resolution_expiration_date'],
							token = t.codificar(str(self.token)),
							user = t.codificar(str(self.data['user'])),
							password = t.codificar(str(self.passwd)),
							cod_bars = self.data['cod_bars'],
							files_company = Files_Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification']))),
							license = True if str(self.data['payment']) == "1000000" else False,
							date_register = str(now + datetime.timedelta(days=365) if full_license else datetime.timedelta(days=30)),
							from_resolution_pos = t.codificar(str(self.data['from_resolution_pos'])),
							to_resolution_pos = t.codificar(str(self.data['to_resolution_pos'])),
							from_resolution_fe = t.codificar(str(self.data['from_resolution_fe'])),
							to_resolution_fe = t.codificar(str(self.data['to_resolution_fe']))
						).save()
						Consecutive_POS(
							number = 1,
							company = Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification'])))
						).save()
						Consecutive_Elec(
							number = 1,
							company = Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification'])))
						).save()
						Consecutive_CreditNote(
							number = 1,
							company = Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification'])))
						).save()
						Consecutive_Payroll(
							number = 1,
							company = Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification'])))
						).save()						
						
						License_Company(
							full_license = full_license,
							registration_date = t.codificar(str(now)),
							due_date = t.codificar(str(now + datetime.timedelta(days=365) if full_license else datetime.timedelta(days=30))),
							company = Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification'])))
						).save()
						balance = Balance.objects.get(seller = Seller.objects.get(code = Files_Company.objects.get(documentIdentification = t.codificar(str(self.data['document_identification']))).seller))
						n = float(t.decodificar(balance.amount)) + (float(self.data['payment']) * 0.20 )
						balance.amount = t.codificar(str(n))
						balance.save()
						
					return "Invalid phone number"
				return "Invalid E-mail"
			return self.Validate()[1]
		except Exception as e:
			print(e)
			return str(e)

	def Validate(self):
		for i in self.data:
			if self.data[i] == "" or self.data[i] == None:
				return (False,"Missing data or wrong data")
		return (True,'Success')
		

