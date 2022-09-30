from from_number_to_letters import numero_a_letras,Thousands_Separator
from django.shortcuts import render
from invoice.models import *
from datetime import date
from api.translator import Translator
from inventory.models import Inventory,Record
from pos.models import *

t = Translator()


def Close_The_Box(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(company = company,date = t.codificar(str(date.today())))
	number_invoice = []
	for i in invoice:
		if int(t.decodificar(str(i.number))) not in number_invoice:
			number_invoice.append(int(t.decodificar(str(i.number))))
	_data = []
	totals = 0
	for j in number_invoice:
		_i = Invoice.objects.filter(company = company,date = t.codificar(str(date.today())), number = t.codificar(str(j)))
		subtotal = 0
		tax = 0
		discount = 0
		cost = 0
		total = 0
		for i_ in _i:
			cost += i_.Base_Product_WithOut_Discount()
			subtotal += i_.Base_Product_WithOut_Discount()
			tax += i_.Tax_Value()
			total += i_.Totals()
		_data.append({
			'number':j,
			'cost': Thousands_Separator(cost),
			'subtotal':Thousands_Separator(subtotal),
			'discount':Thousands_Separator(discount),
			'tax':Thousands_Separator(tax),
			'totals':Thousands_Separator(total),
			'date':str(date.today())
			})
		totals += total
	return render(request,'reports/close_the_box.html',{'data':_data,'total':Thousands_Separator(totals)})

def Invoices(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	import sqlite3
	c = sqlite3.connect('db.sqlite3')
	cur = c.cursor()
	cur.execute("select distinct number from invoice_Invoice where company_id = "+str(company.pk))

	number_invoice = []
	total_invoice = 0
	_data = []
	for i_ in cur.fetchall():
		subtotal = 0
		tax_19 = 0
		tax_5 = 0
		tax_0 = 0
		discount = 0
		cost = 0
		total = 0
		invoice = Invoice.objects.filter(number = i_[0])
		for j in invoice:
			cost += round(j.Base_Product_WithOut_Discount())
			subtotal += round(j.Base_Product_WithOut_Discount() * float(t.decodificar(str(j.quanty))))
			# tax += round(j.Tax_Value())
			total += round(j.Totals())
			inv = Inventory.objects.get(code = j.code)
			if float(t.decodificar(str(inv.tax))) == 19:
				tax_19 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 5:
				tax_5 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 0:
				tax_0 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))


		total_invoice += total
		_data.append({
			'number':'N-'+str(t.decodificar(str(i_[0]))),
			'cost': Thousands_Separator(cost),
			'subtotal':Thousands_Separator(subtotal),
			'discount':Thousands_Separator(discount),
			'tax_19':Thousands_Separator(tax_19),
			'tax_5':Thousands_Separator(tax_5),
			'tax_0':Thousands_Separator(tax_0),
			'totals':Thousands_Separator(total),
			'date':str(date.today())
			})

	totals = numero_a_letras(total_invoice)
	return render(request,'reports/invoice.html',{'data':_data,'totals':totals,'total_report':Thousands_Separator(total_invoice)})


def Close_The_Box_POS(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(company = company,date = t.codificar(str(date.today())))
	number_invoice = []
	for i in invoice:
		if int(t.decodificar(str(i.number))) not in number_invoice:
			number_invoice.append(int(t.decodificar(str(i.number))))
	_data = []
	for j in number_invoice:
		_i = Invoice.objects.filter(company = company,date = t.codificar(str(date.today())), number = t.codificar(str(j)))
		subtotal = 0
		tax = 0
		discount = 0
		cost = 0
		total = 0
		for i_ in _i:
			cost += i_.Base_Product_WithOut_Discount()
			subtotal += i_.Base_Product_WithOut_Discount() * float(t.decodificar(str(i_.quanty)))
			tax += i_.Tax_Value()
			total += i_.Totals()
		_data.append({
			'number':j,
			'cost': cost,
			'subtotal':subtotal,
			'discount':discount,
			'tax':tax,
			'totals':total,
			'date':str(date.today())
			})
	return render(request,'reports/close_the_box.html',{'data':_data})

def Invoices_pos(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	invoice = Invoice.objects.filter(company = company,date = t.codificar(str(date.today())))
	number_invoice = []
	subtotal = 0
	tax = 0
	discount = 0
	cost = 0
	total = 0
	_data = []
	for i_ in invoice:
		cost += i_.Base_Product_WithOut_Discount()
		subtotal += i_.Base_Product_WithOut_Discount() * float(t.decodificar(str(i_.quanty)))
		tax += i_.Tax_Value()
		total += i_.Totals()
		_data.append({
			'number':'N-'+str(t.decodificar(str(i_.number))),
			'cost': cost,
			'subtotal':subtotal,
			'discount':discount,
			'tax':tax,
			'totals':total,
			'date':str(date.today())
			})
	return render(request,'reports/invoice.html',{'data':_data})


def Report_Inventory(request):
	
	try:
		company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
		inventory = Inventory.objects.filter(company = company)
		_data = [
			{
				'code': t.decodificar(str(i.code)),
				'description': t.decodificar(str(i.name)),
				'quanty': t.decodificar(str(i.quanty)),
				'initial_inventory':t.decodificar(str(i.initial_inventory)),
				'price': t.decodificar(str(i.price)),
				'subcategories':t.decodificar(str(i.subcategories.name)),
				'category':t.decodificar(str(i.subcategories.category.name))
			}
			for i in inventory
		]
	except Exception as e:
		_data = []

	return render(request,'reports/inventory.html',{'data':_data})

	




def Close_The_Box_POS(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	invoice = POS.objects.filter(company = company,date = t.codificar(str(date.today())))
	number_invoice = []
	for i in invoice:
		if int(t.decodificar(str(i.number))) not in number_invoice:
			number_invoice.append(int(t.decodificar(str(i.number))))
	_data = []
	for j in number_invoice:
		_i = POS.objects.filter(company = company,date = t.codificar(str(date.today())), number = t.codificar(str(j)))
		subtotal = 0
		tax = 0
		discount = 0
		cost = 0
		total = 0
		for i_ in _i:
			cost += i_.Base_Product_WithOut_Discount()
			subtotal += i_.Base_Product_WithOut_Discount() * float(t.decodificar(str(i_.quanty)))
			tax += i_.Tax_Value()
			total += i_.Totals()
		_data.append({
			'number':j,
			'cost': cost,
			'subtotal':subtotal,
			'discount':discount,
			'tax':tax,
			'totals':total,
			'date':str(date.today())
			})
	return render(request,'reports/close_the_box_pos.html',{'data':_data})


def Record_Inventory(request):
	try:
		record = Record.objects.all()
		_data = [
			{
				'code':t.decodificar(str(i.code)),
				'quanty':t.decodificar(str(i.quanty)),
				'price':t.decodificar(str(i.price)),
				'tax':t.decodificar(str(i.price)),
				'date':i.date,
				'empleoyee':t.decodificar(str(i.empleoyee.firstname))+' '+t.decodificar(str(i.empleoyee.surname)),
				'current_amount':t.decodificar(str(Inventory.objects.get(code = i.code).quanty)),
				'quanty_initial':t.decodificar(str(Inventory.objects.get(code = i.code).initial_inventory))
			}
			for i in record
		]
	except Exception as e:
		_data= []
	

	return render(request,'reports/movements_inventory.html',{'data':_data})



def Report_General_FE(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	import sqlite3
	c = sqlite3.connect('db.sqlite3')
	cur = c.cursor()
	cur.execute("select distinct number from invoice_Invoice where company_id = "+str(company.pk))

	number_invoice = []
	total_invoice = 0
	_data = []
	for i_ in cur.fetchall():
		subtotal = 0
		tax_19 = 0
		tax_5 = 0
		tax_0 = 0
		discount = 0
		cost = 0
		total = 0
		invoice = Invoice.objects.filter(number = i_[0])
		for j in invoice:
			cost += round(j.Base_Product_WithOut_Discount())
			subtotal += round(j.Base_Product_WithOut_Discount() * float(t.decodificar(str(j.quanty))))
			# tax += round(j.Tax_Value())
			total += round(j.Totals())
			inv = Inventory.objects.get(code = j.code)
			if float(t.decodificar(str(inv.tax))) == 19:
				tax_19 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 5:
				tax_5 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 0:
				tax_0 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))


		total_invoice += total
		_data.append({
			'number':'N-'+str(t.decodificar(str(i_[0]))),
			'cost': Thousands_Separator(cost),
			'subtotal':Thousands_Separator(subtotal),
			'discount':Thousands_Separator(discount),
			'tax_19':Thousands_Separator(tax_19),
			'tax_5':Thousands_Separator(tax_5),
			'tax_0':Thousands_Separator(tax_0),
			'totals':Thousands_Separator(total),
			'date':str(date.today())
			})

	totals = numero_a_letras(total_invoice)
	return render(request,'reports/general_fe.html',{'data':_data,'totals':totals,'total_report':Thousands_Separator(total_invoice)})

def Report_General_POS(request):
	company = Company.objects.get(documentIdentification =t.codificar(str(request.session['nit_company'])))
	import sqlite3
	c = sqlite3.connect('db.sqlite3')
	cur = c.cursor()
	cur.execute("select distinct number from pos_POS where company_id = "+str(company.pk))

	number_invoice = []
	total_invoice = 0
	_data = []
	for i_ in cur.fetchall():
		subtotal = 0
		tax_19 = 0
		tax_5 = 0
		tax_0 = 0
		discount = 0
		cost = 0
		total = 0
		invoice = POS.objects.filter(number = i_[0])
		for j in invoice:
			cost += round(j.Base_Product_WithOut_Discount())
			subtotal += round(j.Base_Product_WithOut_Discount() * float(t.decodificar(str(j.quanty))))
			# tax += round(j.Tax_Value())
			total += round(j.Totals())
			inv = Inventory.objects.get(code = j.code)
			if float(t.decodificar(str(inv.tax))) == 19:
				tax_19 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 5:
				tax_5 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))
			if float(t.decodificar(str(inv.tax))) == 0:
				tax_0 += round(inv.Tax_Value() * float(t.decodificar(str(j.quanty))))


		total_invoice += total
		_data.append({
			'number':'N-'+str(t.decodificar(str(i_[0]))),
			'cost': Thousands_Separator(cost),
			'subtotal':Thousands_Separator(subtotal),
			'discount':Thousands_Separator(discount),
			'tax_19':Thousands_Separator(tax_19),
			'tax_5':Thousands_Separator(tax_5),
			'tax_0':Thousands_Separator(tax_0),
			'totals':Thousands_Separator(total),
			'date':str(date.today())
			})

	totals = numero_a_letras(total_invoice)
	return render(request,'reports/general_pos.html',{'data':_data,'totals':totals,'total_report':Thousands_Separator(total_invoice)})












