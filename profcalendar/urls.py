from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.hello_view, name='index'),

    path('hello/', views.hello_view, name='hello'),
    path('about-us/', views.about_us_view, name='about-us'),

    path('admin/', admin.site.urls),

    path('signup/',  views.signup_view, name="signup"),
    path('login/', LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    
    path('profs/', views.profs_list_view, name='prof-list'),
    path('profs/<str:username>', views.prof_detail_view, name="prof-detail"),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/student/<str:student_slug>', views.dashboard_student_detail_view, name='dashboard-student'),
    path('dashboard/lesson/<str:date>', views.dashboard_lesson_detail_view, name='dashboard-lesson'),
]
