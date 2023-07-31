from django.http import HttpResponse
from django.shortcuts import render
from .models import Notification_Acceptance

def List_Notifications(request):
	na = Notification_Acceptance.objects.all()
	for i in na:
		i.seen = True
		i.save()
	return render(request,'notifications/view_notificate.html')


def Read(request):
	if request.is_ajax():
		print("Hola")
		na = Notification_Acceptance.objects.all()
		for i in na:
			i.seen = True
			i.save()
		return HttpResponse("hola")
