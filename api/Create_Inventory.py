from .translator import Translator
from company.models import Company
from inventory.models import Inventory,SubCategories,Supplier

t = Translator()

class CreateInventory:
	def __init__(self,data):
		self.data = data
		print(self.data)

	def Create(self):
		try:
			if self.Validate()[0]:
				Inventory(
					code = t.codificar(str(self.data['code'])),
					name = t.codificar(str(self.data['name'])),
					quanty = t.codificar(str(self.data['quanty'])),
					price = t.codificar(str(self.data['price'])),
					tax = t.codificar(str(self.data['tax'])),
					initial_inventory = t.codificar(str(self.data['initial_inventory'])),
					subcategories = SubCategories.objects.get(pk =str(self.data['subCategories'])),
					company = Company.objects.get(documentIdentification = t.codificar(str(self.data['company']))),
					discount = t.codificar(str(self.data['discount'])),
					ico = t.codificar(str(self.data['ico'])),
					supplier = Supplier.objects.get(name = t.codificar(str(self.data['supplier'])))
				).save()
				return "Product registered successfully"
			return self.Validate()[1]
		except Exception as e:
			print(e)
			return e

	def Validate(self):
		for i in self.data:
			if self.data[i] == "" or self.data[i] == None:
				return (False, "Missing data or wrong data")
		return (True,'Success')



