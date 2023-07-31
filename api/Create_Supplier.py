from inventory.models import Supplier
from company.models import Company
from .translator import Translator

t = Translator()

class CreateSupplier:
	def __init__(self,data):
		self.data = data

	def Create(self):
		try:
			Supplier(
				name = t.codificar(str(self.data['name'])),
				address = t.codificar(str(self.data['address'])),
				phone = t.codificar(str(self.data['phone'])),
				company = Company.objects.get(documentIdentification = t.codificar(str(self.data['company'])))
			).save()
			return "Successfully Registered Vendor"
		except Exception as e:
			return str(e)+" Create"


