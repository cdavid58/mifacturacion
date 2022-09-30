from django.db import models
from api.translator import Translator
t = Translator()

class Ref(models.Model):
	pass
	

class Seller(models.Model):
	code = models.CharField(max_length = 6)
	name = models.TextField()
	documentIdentification = models.TextField()
	phone = models.TextField()
	email = models.TextField()
	account_number = models.TextField(default = "")
	bank = models.TextField(default = "")
	ref = models.TextField(default = "",null=True)

	def __str__(self):
		return t.decodificar(str(self.name))	


class Balance(models.Model):
	seller = models.OneToOneField(Seller,on_delete = models.CASCADE,unique=True)
	amount = models.TextField(default = t.codificar(str(0)))

	def __str__(self):
		return t.decodificar(str(self.seller.name))


