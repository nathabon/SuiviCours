from django import forms
from django.forms import fields
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import CheckboxInput
from django.core.exceptions import ValidationError

from .models import Lesson, Chapter, Professor, Student
import time
import datetime


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, step: int = 15, **kwargs):
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("step", step * 60)
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class TimeInput(forms.TimeInput):
    input_type = "time"


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, step: int = 15, **kwargs):
        attrs = kwargs.setdefault("attrs", {})
        attrs["step"] = 900

        kwargs["format"] = "%Y-%m-%dT%H:%M"

        super().__init__(**kwargs)


class DurationInput(forms.TimeInput):
    input_type = "time"

    def __init__(self, step: int = 15, **kwargs):
        attrs = kwargs.setdefault("attrs", {})

        attrs.setdefault("step", step * 60)
        attrs.setdefault("min", "00:15")
        attrs.setdefault("max", "03:00")

        kwargs["format"] = "%H:%M"

        super().__init__(**kwargs)


class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name')


class NewLessonForm(forms.ModelForm):
    TIME_CHOICES = [
        (
            datetime.time(hour=hour, minute=minute),
            f"{hour:02d}h{minute:02d}",
        )
        for hour in range(24)
        for minute in (0, 15, 30, 45)
    ]

    DURATION_CHOICES = [
        (
            minutes,
            f"{minutes // 60:02d}h{minutes % 60:02d}",
        )
        for minutes in range(15, 181, 15)
    ]


    duration = forms.TypedChoiceField(
        label="Durée",
        choices=DURATION_CHOICES,
        coerce=int,
    )

    class Meta:
        model = Lesson
        exclude = ["professor"]

        widgets = {
            "date": DateTimeInput(),
            "paid": CheckboxInput(attrs={'class':'form-check-input', 'role': 'switch'})
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

            self.fields["price"] = forms.DecimalField(
                max_digits=4,
                decimal_places=1,
                initial=professor.default_price,
            )

        student_id = None

        self.fields["chapter"].widget.attrs.update({
            "class": "searchable-select mb-2",
            "placeholder": "Rechercher un chapitre…",
        })
        self.fields["chapter"].empty_label = "Rechercher un chapitre…"


        if self.data.get("student"):
            student_id = self.data.get("student")

        elif self.instance and self.instance.pk:
            student_id = self.instance.student_id

        if student is not None:
            self.instance.student = student
            student_id = student.id
            self.fields.pop("student")

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

        if not self.is_bound and self.instance and self.instance.pk:
            if self.instance.duration:
                total_minutes = int(
                    self.instance.duration.total_seconds() // 60
                )

                self.initial["duration"] = total_minutes

            if self.instance.date:
                self.initial["date"] = self.instance.date.date()
                self.initial["time"] = self.instance.date.time().replace(
                    second=0,
                    microsecond=0,
                )

        

        self.order_fields([
            'notes',
            'comment',
            'reminders',
            'homeworks',
        ])

    @property
    def selected_fields(self):
        included_names = ['comment', 'reminder', 'homeworks', 'notes', 'chapter']
        return [self[name] for name in self.fields if name in included_names]

    def clean_duration(self) -> datetime.timedelta:
        total_minutes = self.cleaned_data["duration"]

        if total_minutes < 15:
            raise ValidationError(
                "Une séance doit durer au moins 15 minutes."
            )

        if total_minutes > 180:
            raise ValidationError(
                "Une séance ne peut pas durer plus de 3 heures."
            )

        if total_minutes % 15 != 0:
            raise ValidationError(
                "La durée doit être définie par intervalles de 15 minutes."
            )

        return datetime.timedelta(minutes=total_minutes)

    def clean_time(self) -> datetime.time:
        lesson_time = self.cleaned_data["time"]

        if (
            lesson_time.minute % 15 != 0
            or lesson_time.second != 0
            or lesson_time.microsecond != 0
        ):
            raise ValidationError(
                "L’heure du cours doit être définie par intervalles de 15 minutes."
            )

        return lesson_time

    def clean(self):
        cleaned_data = super().clean()

        lesson_date = cleaned_data.get("date")
        lesson_time = cleaned_data.get("time")

        if lesson_date is None or lesson_time is None:
            return cleaned_data

        cleaned_data["date"] = datetime.datetime.combine(
            lesson_date,
            lesson_time,
        )

        return cleaned_data


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'level', 'subject']


class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['subject', 'level', 'comment', 'default_price']


class ContactForm(forms.Form):
    name = fields.CharField(max_length=100, required=True)
    email = fields.EmailField(required=True)
    subject = fields.CharField(max_length=255, required=True)
    message = fields.CharField(widget=forms.Textarea, required=True)
    consent = fields.BooleanField(required=True)