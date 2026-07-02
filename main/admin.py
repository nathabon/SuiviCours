from django.contrib import admin

from main.models import Professor, Student, Lesson, Chapter, Level, Subject

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'professor')

class LessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'professor', 'date')

class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'short')

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'title')

admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Subject, LevelAdmin)
admin.site.register(Chapter, ChapterAdmin)