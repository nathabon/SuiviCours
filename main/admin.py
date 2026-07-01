from django.contrib import admin

from main.models import Professor

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')

admin.site.register(Professor, ProfessorAdmin)
