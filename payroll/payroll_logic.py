import pandas as pd, json, requests, numpy as np,pymysql.cursors
from datetime import datetime,timedelta,date
from api.translator import Translator
from dateutil.relativedelta import relativedelta
t = Translator()

class Request:
	def __init__(self):
		self.MyDB = pymysql.connect(host="localhost:8000",port=3306,user="evansoft",passwd="medellin100",db="apidian",charset='utf8',cursorclass=pymysql.cursors.DictCursor)
		self.cursor = self.MyDB.cursor()

	def typeWorker(self,value):
		self.cursor.execute("select id from type_workers where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

	def typeDocument(self,value):
		self.cursor.execute("select id from type_document_identifications where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

	def Municipalities(self,value):
		self.cursor.execute("select id from municipalities where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

	def typeContract(self,value):
		self.cursor.execute("select id from type_contracts where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

	def PaymentMethod(self,value):
		self.cursor.execute("select id from payment_methods where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

	def TypeDisabilities(self,value):
		self.cursor.execute("select id from type_disabilities where name = '"+str(value)+"'")
		return self.cursor.fetchone()['id']

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

class Payroll_Calculations:

	def __init__(self,path,worker):
		self.xlsx = path
		self.pages = pd.ExcelFile(path)	
		self.list_pages = self.pages.sheet_names
		self.worker = worker
		self.r = Request()

	def DataPages(self,page):
		data = pd.read_excel(self.xlsx, sheet_name=page)
		return data

	def Worker(self):
		data = self.DataPages(self.list_pages[0])
		identification = data['Cedula Empleado']
		conditional = identification == self.worker
		for i in range(len(data)):			
			if data['Cedula Empleado'].values[i] == self.worker:
				return {
					"type_worker_id": self.r.typeWorker(data['Tipo de Trabajador'].values[i]),
					"sub_type_worker_id": 1,
					"payroll_type_document_identification_id": self.r.typeDocument(data['Tipo de Documento'].values[i]),
					"municipality_id": self.r.Municipalities(data['Municipio'].values[i]),
					"type_contract_id": self.r.typeContract(data['Tipo de Contrato'].values[i]),
					"high_risk_pension": False,
					"identification_number": data['Cedula Empleado'].values[i],
					"surname": data['Primer Apellido'].values[i],
			      	"second_surname": "" if 'nan' in str(data['Segundo Apellido'].values[0]) else data['Segundo Apellido'].values[i],
					"first_name": data['Nombre'].values[i],
					"address": data['Domicilio'].values[i],
			      	"integral_salarary": False,
			      	"salary": data['Sueldo Base'].values[i]
				}

	def PaymentMethod(self):
		data = self.DataPages(self.list_pages[1])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				try:
					if self.r.PaymentMethod(data["Metodo de Pago"].values[i]) == 10:
						return {
							"payment_method_id": self.r.PaymentMethod(data["Metodo de Pago"].values[i]),
						}
					return {
						"payment_method_id": self.r.PaymentMethod(data["Metodo de Pago"].values[i]),
						"bank_name": data['Banco'].values[i],
						"account_type": data['Tipo de Cuenta'].values[i],
						"account_number": data['Numero de Cuenta'].values[i]
					}
				except Exception as e:
					break
		return {'Message':"Por favor verifique el documento excel ya que falta llenar los campos de forma de pago"}

	def Worked_Days(self):
		data = self.DataPages(self.list_pages[0])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return {"worked_days": data['Dias Trabajdos'].values[i]}


	#################################################################
	#	ACCRUED

	def Salary(self):
		data = self.DataPages(self.list_pages[0])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return {"salary": data['Sueldo'].values[i]}

	def Transportation_Allowance(self):
		data = self.DataPages(self.list_pages[0])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return {"transportation_allowance": data['Subsidio de Transport'].values[i]}

	def LogicHours(self,page):
		data = self.DataPages(self.list_pages[page])
		value = data['Cedula Empleado'].dropna()
		values = []
		for i in range(len(value)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
								"start_time": "2021-03-01T18:00:00",
								"end_time": "2021-03-01T19:00:00",
								"quantity": data['Cantidad'].values[i],
								"percentage": data['Porcentaje'].values[i],
								"payment": data['Total Pago'].values[i]
							}
				      )
		return values if values else 0

	def ExtraHour(self):
		return self.LogicHours(2)

	def ExtraNightTime(self):
		return self.LogicHours(3)

	def ExtraHourNightSurcharge(self):
		return self.LogicHours(4)

	def SundayExtraDaytime(self):
		return self.LogicHours(5)

	def ExtraHourDaytimeSurcharge(self):
		return self.LogicHours(6)

	def SundayExtraNightTime(self):
		return self.LogicHours(7)

	def ExtraHourNightSurchargeSun(self):
		return self.LogicHours(8)


	def LogicVaction(self, page):
		data = self.DataPages(page)
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
				    "start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
				    "end_date": data['Fecha Final'].values[i].astype(str)[:10],
				    "quantity": data['Cantidad'].values[i],
				    "payment": "{:.2f}".format(data['Total Pago'].values[i])
				})
				return values
		return 0

	def Vacations(self):
		return self.LogicVaction(9)

	def CompensatedVacationDays(self):
		return self.LogicVaction(10)

	def LogicNonSalaryPremium(self,page):
		data = self.DataPages(self.list_pages[page]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
	                "quantity": int(data['Cantidad de meses'].values[i]),
	                "payment": "{:.2f}".format(data['Pago Legal'].values[i]),
	                "paymentNS": "{:.2f}".format(data['Pago Extra Legal No Salarial'].values[i])
	            })
				return values
		return 0

	def ExtraLegalNonSalaryPremium(self):
		return self.LogicNonSalaryPremium(11)

	def Severance(self):
		data = self.DataPages(self.list_pages[12])
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append(
					{
						"payment": data['Pago Censatias'].values[i],
                		"percentage": data['Porcentaje'].values[i],
					   	"interest_payment": data['Tasa de Intereses'].values[i]
					}
				)
		return values if values else 0
	

	# START
	def WorkDisabilities(self):
		data = self.DataPages(self.list_pages[13])
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"end_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"type": self.r.TypeDisabilities(data['Tipo'].values[i]),
					"quantity": int(data['Cantidad'].values[i]),
					"payment": "{:.2f}".format(data['Pago Total'].values[i])
				})
				break
		return values if values else 0

	def MaternityLeave(self):
		data = self.DataPages(self.list_pages[14])
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"end_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"quantity": int(data['Cantidad'].values[i]),
					"payment": "{:.2f}".format(data['Pago Total'].values[i])
				})
		return values if values else 0

	def PaidLeave(self):
		data = self.DataPages(self.list_pages[15]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"end_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"quantity": int(data['Cantidad'].values[i]),
					"payment": "{:.2f}".format(data['Pago Total'].values[i])
				})
		return values if values else 0

	def PaidNotLeave(self):
		data = self.DataPages(self.list_pages[16]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"end_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"quantity": int(data['Cantidad'].values[i]),
					"payment": "{:.2f}".format(data['Pago Total'].values[i])
				})
		return values if values else 0

	def BonusSocial(self):
		data = self.DataPages(self.list_pages[17]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"salary_bonus": "{:.2f}".format(data['Bono Salario'].values[i]),
					"non_salary_bonus": "{:.2f}".format(data['Bono no Salario'].values[i])
				})
				break
		return values if values else 0

	def SalaryAssistant(self):
		data = self.DataPages(self.list_pages[18]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"salary_assistance": "{:.2f}".format(data['Auxilio Salario'].values[i]),
					"non_salary_assistance": "{:.2f}".format(data['Auxilio no Salario'].values[i])
				})
		return values if values else 0

	def LegalStrike(self):
		data = self.DataPages(self.list_pages[19]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"start_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"end_date": data['Fecha Inicial'].values[i].astype(str)[:10],
					"quantity": int(data['Cantidad'].values[i]),
					"payment": "{:.2f}".format(data['Pago Total'].values[i])
				})
		return values if values else 0

	def OtherConcepts(self):
		data = self.DataPages(self.list_pages[20]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"salary_concept": "{:.2f}".format(data['Salarial'].values[i]),
					"non_salary_concept": "{:.2f}".format(data['No Salarial'].values[i]),
					"description_concept": data['Concepto'].values[i]
				})
		return values if values else 0

	def Compensations(self):
		data = self.DataPages(self.list_pages[21]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"ordinary_compensation": "{:.2f}".format(data['Compensacion Ordinaria'].values[i]),
					"extraordinary_compensation": "{:.2f}".format(data['Compensacion ExtraOrdinaria'].values[i])
				})
		return values if values else 0

	def EpctvBonuses(self):
		data = self.DataPages(self.list_pages[22]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"paymentS": "{:.2f}".format(data['Pago Salarial'].values[i]),
					"paymentNS": "{:.2f}".format(data['Pago No Salarial'].values[i]),
					"salary_food_payment": "{:.2f}".format(data['Pago Salarial Alimentacion'].values[i]),
					"non_salary_food_payment": "{:.2f}".format(data['Pago No Salarial Alimentacion'].values[i])
				})
		return values if values else 0

	def Commissions(self):
		data = self.DataPages(self.list_pages[23]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"commission": "{:.2f}".format(data['Comision'].values[i])
				})
		return values if values else 0

	def ThirdPartyPayments(self):
		data = self.DataPages(self.list_pages[24]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
                "third_party_payment": "{:.2f}".format(data['Pago Tercera Partes'].values[i])
            })
		return values if values else 0

	def Advances(self):
		data = self.DataPages(self.list_pages[25]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
	                "advance": "{:.2f}".format(data['Avances'].values[i])
	            })
		return values if values else 0

	def Endowment(self):
		data = self.DataPages(self.list_pages[26]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Pago'].values[i])
		return 0

	def SustenanceSupport(self):
		data = self.DataPages(self.list_pages[27]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Pago'].values[i]) if data['Pago'].values[i] != "null" else 0
		return 0

	def Telecommuting(self):
		data = self.DataPages(self.list_pages[28]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Pago'].values[i]) if data['Pago'].values[i] != "null" else 0
		return 0

	def WithdrawalBonus(self):
		data = self.DataPages(self.list_pages[29]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
					return "{:.2f}".format(data['Pago'].values[i]) if data['Pago'].values[i] != "null" else 0
		return 0

	def Compensation(self):
		data = self.DataPages(self.list_pages[30]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Pago'].values[i]) if data['Pago'].values[i] != "null" else 0
		return 0

	def Monthly_Payment(self):
		data = self.DataPages(self.list_pages[0]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Sueldo Mensual'].values[i])


	#############################################################
	#	DEDUCTIONS

	def EPS(self):
		data = self.DataPages(self.list_pages[31])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return {"eps_type_law_deductions_id": 1,"eps_deduction": data['Pago'].values[i]}

	def Pension(self):
		data = self.DataPages(self.list_pages[31])
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return {"pension_type_law_deductions_id": 5,"pension_deduction": data['Pago'].values[i]}

	def LaborUnion(self):
		data = self.DataPages(self.list_pages[33]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"percentage": data['Porcentaje'].values[i],
					"deduction": "{:.2f}".format(data['Pago'].values[i])
				})
				return values
		return 0

	def Sanctions(self):
		data = self.DataPages(self.list_pages[34]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"public_sanction": "{:.2f}".format(data['Publica'].values[i]),
					"private_sanction": "{:.2f}".format(data['Privada'].values[i])
				})
				return values
		return 0

	def Orders(self):
		data = self.DataPages(self.list_pages[35]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
					"description": data['Descripcion'].values[i],
					"deduction": "{:.2f}".format(data['Valor'].values[i])
				})
				return values
		return 0

	def ThirdPartyPaymentsD(self):
		data = self.DataPages(self.list_pages[36]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
                	"third_party_payment": "{:.2f}".format(data['Valor'].values[i])
            	})
				return values
		return 0

	def AdvancesD(self):
		data = self.DataPages(self.list_pages[37]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
                	"advance": "{:.2f}".format(data['Valor'].values[i])
            	})
				return values
		return 0

	def OtherDeductions(self):
		data = self.DataPages(self.list_pages[38]).dropna()
		values = []
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				values.append({
                	"other_deduction": "{:.2f}".format(data['Valor'].values[i])
            	})
				return values
		return 0

	def VoluntaryPension(self):
		data = self.DataPages(self.list_pages[39]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def WithholdingAtSource(self):
		data = self.DataPages(self.list_pages[40]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def AFC(self):
		data = self.DataPages(self.list_pages[41]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def Cooperative(self):
		data = self.DataPages(self.list_pages[42]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def TaxLiens(self):
		data = self.DataPages(self.list_pages[43]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def SupplementaryPlan(self):
		data = self.DataPages(self.list_pages[44]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def Education(self):
		data = self.DataPages(self.list_pages[45]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def Fefund(self):
		data = self.DataPages(self.list_pages[46]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

	def Debt(self):
		data = self.DataPages(self.list_pages[47]).dropna()
		for i in range(len(data)):
			if data['Cedula Empleado'].values[i] == self.worker:
				return "{:.2f}".format(data['Valor'].values[i])
		return 0

class Declare_Payroll(Payroll_Calculations):
	def __init__(self,path,worker,company):
		super().__init__(path,worker)
		self.c = company

	def Verificate_Data(self,obj,key):
		value = 0
		try:
			if obj is list:
				value += round(float(obj[0][key]),2)
		except Exception as e:
			print(e)
		return value

	def Totals_Accrued(self):
		totals = 0
		totals += round(float(self.Salary()['salary']),2)
		totals += round(float(self.Transportation_Allowance()['transportation_allowance']),2)
		totals += self.Verificate_Data(self.ExtraHour(),'payment')
		totals += self.Verificate_Data(self.ExtraNightTime(),'payment')
		totals += self.Verificate_Data(self.ExtraHourNightSurcharge(),'payment')
		totals += self.Verificate_Data(self.SundayExtraDaytime(),'payment')
		totals += self.Verificate_Data(self.ExtraHourDaytimeSurcharge(),'payment')
		totals += self.Verificate_Data(self.SundayExtraNightTime(),'payment')
		totals += self.Verificate_Data(self.ExtraHourNightSurchargeSun(),'payment')
		totals += self.Verificate_Data(self.Vacations(),'payment')
		totals += self.Verificate_Data(self.CompensatedVacationDays(),'payment')
		totals += self.Verificate_Data(self.ExtraLegalNonSalaryPremium(),'payment')
		totals += self.Verificate_Data(self.ExtraLegalNonSalaryPremium(),'paymentNS')
		totals += self.Verificate_Data(self.Severance(),'payment')
		totals += self.Verificate_Data(self.WorkDisabilities(),'payment')
		totals += self.Verificate_Data(self.MaternityLeave(),'payment')
		totals += self.Verificate_Data(self.PaidLeave(),'payment')
		totals += self.Verificate_Data(self.PaidNotLeave(),'payment')
		totals += self.Verificate_Data(self.BonusSocial(),'salary_bonus')
		totals += self.Verificate_Data(self.BonusSocial(),'non_salary_bonus')
		totals += self.Verificate_Data(self.SalaryAssistant(),'salary_assistance')
		totals += self.Verificate_Data(self.SalaryAssistant(),'non_salary_assistance')
		totals += self.Verificate_Data(self.LegalStrike(),'payment')
		totals += self.Verificate_Data(self.OtherConcepts(),'salary_concept')
		totals += self.Verificate_Data(self.OtherConcepts(),'non_salary_concept')
		totals += self.Verificate_Data(self.Compensations(),'ordinary_compensation')
		totals += self.Verificate_Data(self.Compensations(),'extraordinary_compensation')
		totals += self.Verificate_Data(self.EpctvBonuses(),'paymentS')
		totals += self.Verificate_Data(self.EpctvBonuses(),'paymentNS')
		totals += self.Verificate_Data(self.EpctvBonuses(),'salary_food_payment')
		totals += self.Verificate_Data(self.EpctvBonuses(),'non_salary_food_payment')
		totals += self.Verificate_Data(self.Commissions(),'commission')
		totals += self.Verificate_Data(self.ThirdPartyPayments(),'third_party_payment')
		totals += self.Verificate_Data(self.Advances(),'advance')
		totals += self.Verificate_Data(self.Endowment(),'endowment')
		totals += round(float(self.SustenanceSupport()),2)
		totals += round(float(self.Telecommuting()),2)
		totals += round(float(self.WithdrawalBonus()),2)
		totals += round(float(self.Compensation()),2)

		return totals

	def Totals_Deductions(self):
		totals = 0
		totals += round(float(self.Pension()['pension_deduction']),2)
		totals += round(float(self.EPS()['eps_deduction']),2)
		totals += self.Verificate_Data(self.LaborUnion(),'deduction')
		totals += self.Verificate_Data(self.Sanctions(),'public_sanction')
		totals += self.Verificate_Data(self.Sanctions(),'private_sanction')
		totals += self.Verificate_Data(self.Orders(),'deduction')
		totals += self.Verificate_Data(self.ThirdPartyPaymentsD(),'third_party_payment')
		totals += self.Verificate_Data(self.AdvancesD(),'advance')
		totals += self.Verificate_Data(self.OtherDeductions(),'other_deduction')
		totals += round(float(self.VoluntaryPension()),2)
		totals += round(float(self.WithholdingAtSource()),2)
		totals += round(float(self.AFC()),2)
		totals += round(float(self.Cooperative()),2)
		totals += round(float(self.TaxLiens()),2)
		totals += round(float(self.SupplementaryPlan()),2)
		totals += round(float(self.Education()),2)
		totals += round(float(self.Fefund()),2)
		totals += round(float(self.Debt()),2)
		return totals

	def Preview(self):
		data = self.Data(1)
		data['period'] = self.Period()
		data['worker'] = self.Worker()
		data['payment'] = self.PaymentMethod()
		data['payment_dates'] = [
			{
				'payment_date':str(date.today())
			}
		]
		data['accrued'] = self.Accrued()
		data['deductions'] = self.Deductions()

		payload = json.dumps(data,cls=NpEncoder)
		print(payload)
		url = "http://localhost/api_solo_pdf/public/api/ubl2.1/payroll"
		token = "656aa7a5d876bc6d8c21d5df54937e51c85fd49f6802da7e0a56676b6c3afa76"
		headers = {
		  'Content-Type': 'application/json',
		  'Accept': 'application/json',
		  'Authorization': 'Bearer '+str(token)
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		print(response.text)

		return payload

	def Period(self):
		ahora = datetime.now()
		dentro_de_un_mes = str(ahora - relativedelta(months=1))[:10]
		mes = dentro_de_un_mes.split('-')[1]
		anio = dentro_de_un_mes.split('-')[0]
		date_from = str(anio)+'-'+mes+'-01'
		self.date_to = str(anio)+'-'+mes+'-30'
		return {
	        "admision_date": str(date.today()),
	        "settlement_start_date": date_from,
	        "settlement_end_date": self.date_to,
	        "worked_time": 30,
	        "issue_date": str(date.today())
	    }

	def Data(self,consec):
		return {
			"type_document_id": 9,
			"establishment_name": t.decodificar(str(self.c.business_name)),
			"establishment_address": t.decodificar(str(self.c.address)),
			"establishment_phone": t.decodificar(str(self.c.phone)),
			"establishment_municipality": self.c.municipality.id,
			"foot_note": "Nómina Electrónica elaborada por Evansoft s.a.s",
			"worker_code": "001",
			"prefix": "NI",
			"consecutive": consec,
			"payroll_period_id": 4,
			"notes": "PRUEBA DE ENVIO DE NOMINA ELECTRONICA"
		}

	def Accrued(self):

		data = {}
		tag = ['worked_days','salary','transportation_allowance','HEDs','HENs','HRNs','HEDDFs','HRDDFs','HENDFs','HRNDFs','common_vacation','paid_vacation','service_bonus',
				'severance','work_disabilities','maternity_leave','paid_leave','non_paid_leave','bonuses','aid','legal_strike','other_concepts','compensations','epctv_bonuses',
				'commissions','third_party_payments','advances','endowment','sustenance_support','telecommuting','withdrawal_bonus','compensation','accrued_total']
		value = [
			self.Worked_Days()['worked_days'],round(self.Salary()['salary'],2),round(self.Transportation_Allowance()['transportation_allowance'],2),self.ExtraHour(),
			self.ExtraNightTime(),self.ExtraHourNightSurcharge(),self.SundayExtraDaytime(),self.ExtraHourDaytimeSurcharge(),self.SundayExtraNightTime(),
			self.ExtraHourNightSurchargeSun(),self.Vacations(),self.CompensatedVacationDays(),self.ExtraLegalNonSalaryPremium(),self.Severance(),
			self.WorkDisabilities(),self.MaternityLeave(),self.PaidLeave(),self.PaidNotLeave(),self.BonusSocial(),self.SalaryAssistant(),self.LegalStrike(),
			self.OtherConcepts(),self.Compensations(),self.EpctvBonuses(),self.Commissions(),self.ThirdPartyPayments(),self.Advances(),
			self.Endowment(),self.SustenanceSupport(),self.Telecommuting(),self.WithdrawalBonus(),self.Compensation(),self.Totals_Accrued()
		]

		n = 0
		for i in value:
			if i != 0:
				data[tag[n]] = i
			n += 1
		return data

	def Deductions(self):
		data = {}
		tag = ['eps_type_law_deductions_id','eps_deduction','pension_type_law_deductions_id', 'pension_deduction',
			'labor_union','sanctions','orders','third_party_payments','advances','other_deductions','voluntary_pension',
			'withholding_at_source','afc','cooperative','tax_liens','supplementary_plan','education','refund',
			'debt','deductions_total']
		value = [1,self.EPS()['eps_deduction'],5,self.Pension()['pension_deduction'],self.LaborUnion(),self.Sanctions(),self.Orders(),self.ThirdPartyPaymentsD(),
				self.AdvancesD(),self.OtherDeductions(),self.VoluntaryPension(),self.WithholdingAtSource(),
				self.AFC(),self.Cooperative(),self.TaxLiens(),self.SupplementaryPlan(),
				self.Education(),self.Fefund(),self.Debt(),self.Totals_Deductions()
		]

		n = 0
		for i in value:
			if i != 0:
				data[tag[n]] = i
			n += 1
		return data


