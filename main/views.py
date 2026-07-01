from django.http import HttpResponse
from django.shortcuts import render
from main.models import Professor

def hello(request):
    return HttpResponse('<h1>Hello Django!</h1>')

def profs(request):
    profs = Professor.objects.all()
    return render(request, 'profs.html', {"profs": profs})

def prof_detail(request, username: str):
    prof = Professor.objects.get(username=username)
    return render(request, 'prof_detail.html', {"prof": prof})

def about(request):
    return HttpResponse('<h1> À propos de nous </h1>')