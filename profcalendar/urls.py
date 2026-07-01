from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('/', views.hello),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('hello/', views.hello),
    path('about-us/', views.about),
    path('profs/', views.profs, name='prof-list'),
    path('profs/<str:username>', views.prof_detail, name="prof-detail")
]
