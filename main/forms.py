from django import forms
from django.forms import fields
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Lesson, Chapter, Professor, Student

import datetime

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name')


class NewLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        exclude = ['professor']

    def __init__(self, *args, professor: Professor | None =None, **kwargs):
        super().__init__(*args, **kwargs)

        if professor is not None:
            self.fields["student"].queryset = Student.objects.filter(professor=professor)
            self.fields['price'] = fields.DecimalField(max_digits=4, decimal_places=1, initial=professor.default_price)

        student_id = None

        if self.data.get("student"):
            student_id = self.data.get("student")
        elif self.instance and self.instance.pk:
            student_id = self.instance.student_id

        if student_id and professor is not None:
            try:
                student = Student.objects.get(
                    id=student_id,
                    professor=professor
                )

                self.fields["chapter"].queryset = Chapter.objects.filter(
                    subject=student.subject,
                    level=student.level
                ).order_by("title")

            except Student.DoesNotExist:
                pass

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")

        if duration is None:
            return duration

        if duration > datetime.timedelta(hours=3):
            raise ValidationError("Une séance ne peut pas durer plus de 3 heures.")

        return duration

    def clean(self):
        cleaned_data = super().clean()

        lesson_date = cleaned_data.get("date")
        duration = cleaned_data.get("duration")
        status = cleaned_data.get("status")

        if lesson_date is None or duration is None or status is None:
            return cleaned_data

        today = datetime.date.today()

        if status == "planned" and lesson_date + duration < today:
            raise ValidationError("Le statut de la leçon est 'Prévue', alors que la date est passée.")

        if status == "done" and lesson_date > today:
            raise ValidationError("Le statut de la leçon est 'Faite', alors que la date est dans le futur.")

        return cleaned_data

