from django.db import models
from invoice.models import Invoice
from company.models import Company


class Notification_Acceptance(models.Model):
	invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	notes = models.TextField(null=True,blank=True)
	acceptance = models.BooleanField(default=False)
	date = models.CharField(max_length = 10)
	time = models.CharField(max_length=10,default="")
	seen = models.BooleanField(default = False)


