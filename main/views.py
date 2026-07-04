from django.http import HttpResponse, HttpRequest, QueryDict, Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Professor, Student, Lesson
from . import forms
from datetime import datetime


# MARK: Static
def hello_view(request: HttpRequest):
    return render(request, 'index.html')


def about_us_view(request: HttpRequest):
    return HttpResponse('<h1> À propos de nous </h1>')


#MARK: Account
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


#MARK: Dashboard
@login_required
def dashboard_view(request: HttpRequest):
    prof = request.user.professor_profile

    return render(request, 'dashboard.html', {"prof": prof})


@login_required
def dashboard_student_detail_view(request: HttpRequest, student_slug: str):
    prof = request.user.professor_profile
    student = get_object_or_404(Student, professor=prof, slug=student_slug)

    return render(request, 'dashboard_student.html', {"prof": prof, 'student': student})

@login_required
def dashboard_lesson_detail_view(request: HttpRequest, date: str):
    try:
        date = datetime.strptime(date, "%y-%m-%d-%H-%M")
    except ValueError as error:
        raise Http404(error)
    
    prof = request.user.professor_profile
    lesson = get_object_or_404(Lesson, professor=prof, date=date)

    return render(request, 'dashboard_lesson.html', {'professsor': prof, 'lesson': lesson})