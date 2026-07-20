from django import forms
from django.forms import fields
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Lesson, Chapter, Professor, Student

import datetime

class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class TimeInput(forms.TimeInput):
    input_type = "time"


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, step: int = 15, **kwargs):
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("step", step * 60)

        kwargs["format"] = "%Y-%m-%dT%H:%M"

        super().__init__(**kwargs)


class DurationInput(forms.TimeInput):
    input_type = "time"

    def __init__(self, step: int = 15, **kwargs):
        attrs = kwargs.setdefault("attrs", {})

        attrs.setdefault("step", step * 60)  # 900 secondes / 15 minutes
        attrs.setdefault("min", "00:15")
        attrs.setdefault("max", "03:00")

        kwargs["format"] = "%H:%M"

        super().__init__(**kwargs)


class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name')


class NewLessonForm(forms.ModelForm):
    duration = forms.TimeField(
        label="Durée",
        input_formats=["%H:%M"],
        widget=DurationInput(),
    )

    class Meta:
        model = Lesson
        exclude = ["professor"]

        widgets = {
            "date": DateTimeInput(),
        }

    def __init__(
        self,
        *args,
        professor: Professor | None = None,
        student: Student | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if professor is not None:
            self.instance.professor = professor

            self.fields["student"].queryset = Student.objects.filter(
                professor=professor
            )

            self.fields["price"] = fields.DecimalField(
                max_digits=4,
                decimal_places=1,
                initial=professor.default_price,
            )

        student_id = None

        if self.data.get("student"):
            student_id = self.data.get("student")

        elif self.instance and self.instance.pk:
            student_id = self.instance.student_id

        if student is not None:
            self.instance.student = student
            student_id = student.id

        if student_id and professor is not None:
            try:
                selected_student = Student.objects.get(
                    id=student_id,
                    professor=professor,
                )

                self.fields["chapter"].queryset = Chapter.objects.filter(
                    subject=selected_student.subject,
                    level=selected_student.level,
                ).order_by("title")

            except Student.DoesNotExist:
                pass

        if not self.is_bound and self.instance and self.instance.duration:
            total_minutes = int(self.instance.duration.total_seconds() // 60)

            hours, minutes = divmod(total_minutes, 60)

            self.initial["duration"] = datetime.time(hour=hours, minute=minutes)


    def clean_duration(self) -> datetime.timedelta:
        duration_time = self.cleaned_data.get("duration")

        if not isinstance(duration_time, datetime.time):
            raise ValidationError("La durée indiquée est invalide.")

        total_minutes = duration_time.hour * 60 + duration_time.minute

        if duration_time.second != 0 or total_minutes % 15 != 0:
            raise ValidationError("La durée doit être définie par intervalles de 15 minutes.")

        if total_minutes < 15:
            raise ValidationError("Une séance doit durer au moins 15 minutes.")

        if total_minutes > 180:
            raise ValidationError("Une séance ne peut pas durer plus de 3 heures.")

        return datetime.timedelta(minutes=total_minutes)
    
    def clean_date(self) -> datetime.datetime:
        lesson_date = self.cleaned_data["date"]

        if lesson_date.minute % 15 != 0 or lesson_date.second != 0 or lesson_date.microsecond != 0:
            raise ValidationError(
                "L’heure du cours doit être définie par intervalles de 15 minutes."
            )

        return lesson_date

    def clean(self):
        cleaned_data = super().clean()

        lesson_date = cleaned_data.get("date")
        duration = cleaned_data.get("duration")
        status = cleaned_data.get("status")

        if lesson_date is None or duration is None or status is None:
            return cleaned_data

        today = datetime.date.today()

        # if status == "planned" and lesson_date + duration < today:
        #     raise ValidationError("Le statut de la leçon est 'Prévue', alors que la date est passée.")

        # if status == "done" and lesson_date > today:
        #     raise ValidationError("Le statut de la leçon est 'Faite', alors que la date est dans le futur.")

        return cleaned_data


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'level', 'subject']


class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['subject', 'level', 'comment', 'default_price']
