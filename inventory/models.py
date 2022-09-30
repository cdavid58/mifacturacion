from django.db import models
from company.models import Company
from api.translator import Translator
from empleoyee.models import Empleoyee
from django.http import HttpResponse

t = Translator()

class Category(models.Model):
	name = models.TextField(default="")

	def __str__(self):
		return t.decodificar(str(self.name))

class SubCategories(models.Model):
	name = models.TextField(default="")
	category = models.ForeignKey(Category,on_delete = models.CASCADE,default="",null=True,blank=True)

	def __str__(self):
		return t.decodificar(str(self.name))	


class Supplier(models.Model):
	name = models.TextField()
	address = models.TextField()
	phone = models.TextField()
	company = models.ForeignKey(Company,on_delete=models.CASCADE)

	def __str__(self):
		return t.decodificar(str(self.name))

class Inventory(models.Model):
	code = models.TextField(default="")
	name = models.TextField()
	quanty = models.TextField()
	price = models.TextField()
	tax = models.TextField()
	initial_inventory = models.TextField()
	exhausted = models.BooleanField(default=False)
	subcategories = models.ForeignKey(SubCategories,on_delete = models.CASCADE,default="",null=True,blank=True)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	discount = models.TextField(default = 0)
	ico = models.TextField(default=0)
	supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE, null=True,blank=True, default=1)

	def __str__(self):
		return t.decodificar(str(self.name))

	def Base_Product(self):
		return round(( float(t.decodificar(str(self.price))) - float(t.decodificar(str(self.ico)))) / (1 + (float( t.decodificar(str(self.tax)) )) / 100))

	def Tax_Value(self):
		return round( self.BaseWithOutDiscount() *  ( float( float(t.decodificar(str(self.tax))) / 100  )   ))

	def PriceSale(self):
		price = float(t.decodificar(self.price))
		discount = float(t.decodificar(str(self.discount)))
		return round(price - (price * (discount / 100)))

	def PriceDiscount(self):
		price =  self.Base_Product()
		discount = float(t.decodificar(str(self.discount)))
		return round(price * (discount / 100))

	def BaseWithOutDiscount(self):
		return round(self.Base_Product() - self.PriceDiscount())



class Record(models.Model):
	code = models.TextField()
	quanty = models.TextField()
	price = models.TextField()
	tax = models.TextField()
	date = models.TextField()
	time = models.TextField()
	empleoyee = models.ForeignKey(Empleoyee,on_delete=models.CASCADE)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)


class Shopping_Inventory(models.Model):
	code = models.ForeignKey(Inventory,on_delete=models.CASCADE,default="")
	quanty = models.TextField(default="")
	date = models.CharField(max_length=10)
	time = models.CharField(max_length=10)
	empleoyee = models.ForeignKey(Empleoyee, on_delete= models.CASCADE)
	supplier = models.ForeignKey(Supplier,on_delete = models.CASCADE)
	price = models.TextField(default = 0)
	used = models.BooleanField(default = False)
	paid = models.BooleanField(default = False)
	number_invoice = models.TextField(default = 0)
	company = models.ForeignKey(Company,on_delete=models.CASCADE,default="")
	tax = models.TextField(default="")
	ico = models.TextField(default = "")
	initial_inventory = models.TextField(default = "")

	def Base(self):
		return round( float( float(t.decodificar(str(self.price))) / ( 1 + ( float(t.decodificar(str(Inventory.objects.get(code = self.code.code).tax))) ) / 100) ) * float(t.decodificar(str(self.quanty))) ,2)

	def Tax_Value(self):
		return round(self.Base() * float(float(t.decodificar(str(self.tax))) / 100),2)

	def Subtotal(self):
		return round(self.Base(),2)

	def Total(self):
		return self.Base() + self.Tax_Value()

class Discount_Inventory:
	def __str__(self):
		pass

	def Discount(self,cod,quanty):
		self.i = Inventory.objects.get(code = t.codificar(str(cod)))
		if int(t.decodificar(str(self.i.quanty))) >= quanty:
			less = int(t.decodificar(str(self.i.quanty))) - quanty
			self.i.quanty = t.codificar(str(less))
			self.i.save()
		if int(t.decodificar(str(self.i.quanty))) == 0:
			try:
				self.validate_shopping = Shopping_Inventory.objects.filter(code = self.i, used = False, company = Company.objects.get(documentIdentification = t.codificar(str(9918401)))).first()
			except Shopping_Inventory.DoesNotExist:
				self.validate_shopping = None

			if self.validate_shopping is not None:
				self.i.quanty = self.validate_shopping.quanty
				self.i.price = self.validate_shopping.price
				self.i.save()
				self.validate_shopping.used = True
				self.validate_shopping.save()
			else:
				self.i.exhausted = True
				self.i.save()

		


