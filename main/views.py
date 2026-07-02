from django.http import HttpResponse, HttpRequest, QueryDict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Professor, Student, Lesson
from . import forms

def hello_view(request: HttpRequest):
    return render(request, 'index.html')


def about_us_view(request: HttpRequest):
    return HttpResponse('<h1> À propos de nous </h1>')


def signup_view(request: HttpRequest):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'signup.html', context={'form': form})


def logout_view(request: HttpRequest):
    logout(request)

    return redirect('login')


def profs_list_view(request: HttpRequest):
    profs = Professor.objects.all()
    return render(request, 'profs.html', {"profs": profs})

def prof_detail_view(request: HttpRequest, username: str):
    prof = Professor.objects.get(username=username)
    return render(request, 'prof_detail.html', {"prof": prof})

@login_required()
def dashboard_view(request: HttpRequest):
    prof = Professor.objects.get(user=request.user)

    return render(request, 'dashboard.html', {"prof": prof})

@login_required
def dashboard_student_detail_view(request: HttpRequest, student_name: str):
    prof = Professor.objects.get(user=request.user)
    student = get_object_or_404(Student, professor=prof, first_name=student_name)

    return render(request, 'dashboard_student.html', {"prof": prof, 'student': student})