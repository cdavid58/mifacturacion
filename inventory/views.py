from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import *
from datetime import date
from api.Create_Inventory import CreateInventory
# from api.Create_Supplier import Create
from empleoyee.models import Empleoyee
from company.models import Company
import json

def c(request):
	return Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))


def Add_Category(request):
	global c
	if request.is_ajax():
		Category(
			name = t.codificar(str(request.GET.get('name')))
		).save()
		return HttpResponse("")




def Add_Inventory(request):
	global c
	category = Category.objects.all()

	if request.is_ajax():
		data = request.GET
		print(data)
		_data = {
		   "code":data['code'],
			"name":data['name'],
			"quanty":data['quanty'],
			"price":data['price'],
			"tax":data['tax'],
			"initial_inventory":data['quanty'],
			"subCategories":data['subcategory'],
			"company":request.session['nit_company'],
			"discount":data['discount'],
			'ico':data['ico'],
			'supplier':data['supplier']
		}
		c_ = CreateInventory(_data)
		message = c_.Create()
		return HttpResponse(message)
	cat = [
		{
			'pk':c.pk,
			'name':t.decodificar(str(c.name))
		}
		for c in category
	]
	supplier = Supplier.objects.filter(company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company']))))
	_sp = [
		{
			'name':t.decodificar(str(i.name))
		}
		for i in supplier
	]
	return render(request,'inventory/add.html',{'c':cat,'supplier':_sp})

def List_Inventory(request):
	inv = Inventory.objects.filter(company = c(request))
	_data = [
		{
			'pk':i.pk,
			'code': t.decodificar(str(i.code)),
			'description': t.decodificar(str(i.name)),
			'quanty': t.decodificar(str(i.quanty)),
			'tax':t.decodificar(str(i.tax)),
			'price': t.decodificar(str(i.price)),
			'category':t.decodificar(str(i.subcategories.category.name)),
			'subCategory':t.decodificar(str(i.subcategories.name)),
			'discount':t.decodificar(str(i.discount)),
			'ico':t.decodificar(str(i.ico)),
			'price_sele':i.PriceSale()
		}
		for i in inv
	]
	utility = 0
	assets = 0
	for x in inv:
		tax = float(t.decodificar(str(x.tax)))
		win = float(t.decodificar(str(x.price))) - x.Base_Product()
		utility += round(float(t.decodificar(str(x.quanty))) * win,2)

		assets += round((x.Base_Product() * float(t.decodificar(str(x.quanty))) ),2)

	assets = "{:,}".format(assets).replace(',','~').replace('.',',').replace('~','.')
	utility = "{:,}".format(utility).replace(',','~').replace('.',',').replace('~','.')

	return render(request,'inventory/list_inventory.html',{'data':_data,'utility':utility,'assets':assets})

def Edit_Inventory(request,pk):
	global c
	i = Inventory.objects.get(company = c(request),pk = pk)
	if request.is_ajax():
		data = request.GET
		i.name = t.codificar(str(data['name']))
		i.price = t.codificar(str(data['price']))
		i.tax = t.codificar(str(data['tax']))
		i.quanty = t.codificar(str(data['quanty']))
		i.discount = t.codificar(str(data['discount']))
		i.ico = t.codificar(str(data['ico']))
		i.subcategories = SubCategories.objects.get(pk = data['subcategory'])
		n = int(t.decodificar(str(i.initial_inventory))) + int(data['quanty'])
		i.initial_inventory = t.codificar(str(n))

		i.save()
		if int(t.decodificar(str(i.quanty))) > 0:
			i.exhausted = False
			i.save()
		Record(
			code = i.code,
			quanty = t.codificar(str(data['quanty'])),
			price = t.codificar(str(data['price'])),
			tax = t.codificar(str(data['tax'])),
			date = date.today(),
			time = "",
			empleoyee = Empleoyee.objects.get(pk=request.session['empleoyee_pk']),
			company = c(request)
		).save()
		return HttpResponse()
	_data ={
		'pk':i.pk,
		'code': t.decodificar(str(i.code)),
		'description': t.decodificar(str(i.name)),
		'quanty': t.decodificar(str(i.quanty)),
		'tax':t.decodificar(str(i.tax)),
		'price': t.decodificar(str(i.price)),
		'category':t.decodificar(str(i.subcategories.category.name)),
		'subcategory':t.decodificar(str(i.subcategories.name)),
		'subCategory_pk':i.subcategories.pk,
		'discount':t.decodificar(str(i.discount)),
		'ico':t.decodificar(str(i.ico))
	}
	category = Category.objects.all()
	cat = [
		{
			'pk':c.pk,
			'name':t.decodificar(str(c.name))
		}
		for c in category
	]
	subc = [
		{
			'pk': s.pk,
			'name':t.decodificar(str(s.name))
		}
		for s in SubCategories.objects.filter(category = i.subcategories.category)
	]
	# print(cat)


	return render(request,'inventory/edit.html',{'i':_data,'c':cat,'sub':subc})

def Delete_Inventario(request,pk):
	Inventory.objects.get(pk = pk).delete()
	return redirect("List_Inventory")


def GetSubCategories(request):
	if request.is_ajax():
		import json
		try:
			print(request.GET.get('pk'))
			cate = Category.objects.get(name = t.codificar(str(request.GET.get('pk'))))
			sc = SubCategories.objects.filter(category = cate)
			_data = [
				{
					'pk':i.pk,
					'name':t.decodificar(str(i.name))
				}
				for i in sc
			]
		except Category.DoesNotExist:
			_data = []
		return HttpResponse(json.dumps(_data))



def Shopping(request):
	company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
	if request.is_ajax():
		i = Inventory.objects.get(code = t.codificar(str(request.GET.get('code'))))
		request.session['invoice_shopping'] = request.GET.get("invoice_number")
		request.session['supplier'] = request.GET.get("supplier")
		_data = [
			{
				'name':t.decodificar(str(i.name)),
				'price':t.decodificar(str(i.price)),
				'tax':t.decodificar(str(i.tax)),
				'quanty':t.decodificar(str(i.quanty))
			}
		]
		return HttpResponse(json.dumps(_data))
	supplier = Supplier.objects.filter(company = company)

	_sp = [
		{
			'name':t.decodificar(str(i.name))
		}
		for i in supplier
	]

	return render(request,'inventory/shopping.html',{'supplier':_sp})

def AddSupplier(request):

	if request.is_ajax():
		data = request.GET
		Supplier(
			name = t.codificar(str(data['name'])),
			address = t.codificar(str(data['address'])),
			phone = t.codificar(str(data['phone'])),
			company = Company.objects.get(documentIdentification = t.codificar(str(request.session['nit_company'])))
		).save()
		return HttpResponse()

def trans(value):
	return t.codificar(str(value))

def Save_Shopping(request):
	if request.is_ajax():
		data = request.GET
		success = False
		message = ""
		for i in data:
			_data = json.loads(i)
			if len(_data) == 0:
				break
			for j in _data:
				inv = Inventory.objects.get(code = t.codificar(str(j['Código'])))
				totals = float(j['Costo']) + float(j['Iva Val'])
				Shopping_Inventory(
					code = inv,
					quanty = t.codificar(str(j['Cantidad'])),
					date = date.today(),
					time = "14:28",
					empleoyee = Empleoyee.objects.get(pk = request.session['empleoyee_pk']),
					supplier = Supplier.objects.get(name = t.codificar(str(request.session['supplier']))),
					price = t.codificar(str(totals)),
					number_invoice = t.codificar(str(request.session['invoice_shopping'])),
					company = Empleoyee.objects.get(pk = request.session['empleoyee_pk']).company,
					tax = t.codificar(str(j['Iva'])),
					ico = t.codificar(str(j['ICO'])),
					initial_inventory = t.codificar(str(j['Cantidad']))
				).save()

				# if int(t.decodificar(str(inv.quanty))) <= 0:
				# 	si = Shopping_Inventory.objects.filter(code = inv, used = False, company = Company.objects.get(documentIdentification = t.codificar(str(9918401)))).first()
				# 	inv.quanty = si.quanty
				# 	inv.tax = trans(j['Iva'])
				# 	inv.price = trans(totals)
				# 	inv.ico = si.ico
				# 	inv.discount = trans(j['Desc.'])
				# 	inv.save()
				# 	si.used = True
				# 	si.save()
				si = Shopping_Inventory.objects.filter(code = inv, used = False).first()
				n = int(t.decodificar(str(inv.quanty)))
				q = int(j['Cantidad'])
				inv.quanty = t.codificar(str(n + q))
				inv.tax = trans(j['Iva'])
				inv.price = trans(totals)
				inv.ico = si.ico
				inv.discount = trans(j['Desc.'])
				inv.save()
				si.used = True
				si.save()
				Record(
				    code = inv.code,
				    quanty = t.codificar(str(data['Cantidad'])),
				    price = t.codificar(str(data['Costo'])),
				    tax = t.codificar(str(data['Iva Val'])),
				    date = date.today(),
				    time = "",
				    empleoyee = Empleoyee.objects.get(pk=request.session['empleoyee_pk']),
				    company = c(request)
				).save()
		del request.session['invoice_shopping']
		del request.session['supplier']
		return HttpResponse("")
