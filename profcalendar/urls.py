from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.hello_view, name='index'),

    path('hello/', views.hello_view, name='hello'),
    path('about-us/', views.about_us_view, name='about'),
    path('contact/', views.contact, name='contact'),

    path('admin/', admin.site.urls, name='admin'),

    path('signup/',  views.signup_view, name="signup"),
    path('login/', LoginView.as_view(template_name='account/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(template_name='account/logout.html'), name='logout'),
    path('settings/', views.settings_view, name='settings'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/student/add/', views.dashboard_student_add_view, name='dashboard-add-student'),
    path('dashboard/student/<slug:student_slug>/', views.dashboard_student_detail_view, name='dashboard-student'),
    path('dashboard/lesson/add/', views.dashboard_lesson_add_view, name='dashboard-add-lesson'),
    path('dashboard/lesson/<str:date>/', views.dashboard_lesson_detail_view, name='dashboard-lesson'),

    path('parent/<str:student_uuid>/', views.dashboard_parent_student_view, name='dashboard-parent-student'),
    path('parent/<str:student_uuid>/lesson/<str:date>/', views.dashboard_parent_lesson_view, name='dashboard-parent-lesson'),

    path('api/chapters/', views.api_chapters, name='api-chapters'),
    path('api/chapters/level/<str:level_slug>', views.api_chapters_level, name='api-chapters-level'),
    path('api/chapters/subject/<str:subject_slug>', views.api_chapters_subject, name='api-chapters-subject'),
    path('api/subjects/level/<str:level_slug>', views.api_subjects_level, name='api-subject-level'),
    path('api/student/<int:id>/', views.api_student, name='api-student'),
    path('api/student/<int:id>/chapters/', views.api_student_chapters, name='api-student-chapters'),
]
