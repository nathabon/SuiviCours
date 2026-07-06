from django.http import HttpResponse, HttpRequest, QueryDict, Http404, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from django.conf import settings
from .models import Professor, Student, Lesson, Chapter
from . import forms
from datetime import datetime
import uuid


# MARK: Static
def hello_view(request: HttpRequest):
    return render(request, 'index.html')


def about_us_view(request: HttpRequest):
    return render(request, 'about.html')

def contact(request: HttpRequest):
    return HttpResponse('<h1> Contact </h1>')


#MARK: Account
def signup_view(request: HttpRequest):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'account/signup.html', context={'form': form})


def logout_view(request: HttpRequest):
    logout(request)

    return redirect('login')


def profs_list_view(request: HttpRequest):
    profs = Professor.objects.all()
    return render(request, 'other/profs.html', {"profs": profs})


def prof_detail_view(request: HttpRequest, username: str):
    prof = Professor.objects.get(username=username)
    return render(request, 'other/prof_detail.html', {"prof": prof})


#MARK: Dashboard
@login_required
def dashboard_view(request: HttpRequest):
    prof = request.user.professor_profile

    return render(request, 'dashboard/dashboard.html', {"prof": prof})


@login_required
def dashboard_student_detail_view(request: HttpRequest, student_slug: str):
    prof = request.user.professor_profile
    student = get_object_or_404(Student, professor=prof, slug=student_slug)

    return render(request, 'dashboard/dashboard_student.html', {"prof": prof, 'student': student})


@login_required
def dashboard_lesson_add_view(request: HttpRequest):
    prof = request.user.professor_profile
    form = forms.NewLessonForm(professor=prof)

    if request.method == "POST":
        form = forms.NewLessonForm(request.POST, professor=prof)

        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.save()

            return redirect('dashboard-lesson', date=lesson.date_formated, permanent=True)
        
    return render(request, 'dashboard/dashboard_lesson_add.html', {'form': form})



@login_required
def dashboard_lesson_detail_view(request: HttpRequest, date: str):
    try:
        date = datetime.strptime(date, "%y-%m-%d-%H-%M")
    except ValueError as error:
        raise Http404(error)
    
    prof = request.user.professor_profile
    lesson = get_object_or_404(Lesson, professor=prof, date=date)

    return render(request, 'dashboard/dashboard_lesson.html', {'professsor': prof, 'lesson': lesson})


#MARK: Dashboard parent
def dashboard_parent_student_view(request: HttpRequest, student_uuid: uuid.UUID):
    student = get_object_or_404(Student, uuid = uuid.UUID(student_uuid))

    return render(request, 'dashboard/dashboard_parent_student.html', {'student': student})

def dashboard_parent_lesson_view(request: HttpRequest, student_uuid: uuid.UUID, date: str):
    student = get_object_or_404(Student, uuid = uuid.UUID(student_uuid))
    try:
        date = datetime.strptime(date, "%y-%m-%d-%H-%M")
    except ValueError as error:
        raise Http404(error)
    lesson = get_object_or_404(Lesson, student=student, date=date)

    return render(request, 'dashboard/dashboard_parent_lesson.html', {'student': student, 'lesson': lesson})



#MARK: API
@login_required
def api_student(request: HttpRequest, id: str):
    prof = request.user.professor_profile
    student = get_object_or_404(Student, professor=prof, id=id)

    return JsonResponse(model_to_dict(student), safe=False)


@login_required
def api_student_chapters(request: HttpRequest, id: str):
    prof = request.user.professor_profile
    student = get_object_or_404(Student, professor=prof, id=id)

    chapters = Chapter.objects.filter(
        subject=student.subject,
        level=student.level
    ).order_by("title")

    data = [
        {
            "id": chapter.id,
            "title": chapter.title,
        }
        for chapter in chapters
    ]

    return JsonResponse(data, safe=False)
