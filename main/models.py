from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta
import decimal
import uuid


class Subject(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=100, blank=True)
    slug  = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Level(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=100, blank=True)
    slug  = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    title = models.CharField(max_length=200)

    class Meta:
        ordering = ["subject", "level", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "level", "title"],
                name="unique_chapter_subject_level_title"
            )
        ]

    def __str__(self):
        return f"{self.level} - {self.subject} - {self.title}"


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="professor_profile")

    default_price = models.fields.DecimalField(max_digits=4, decimal_places=1, default=decimal.Decimal(20.0))

    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def name(self):
        return self.user.get_full_name() or self.user.username

    def __str__(self) -> str:
        return self.name



class Student(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=False, null=False)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="students")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=100, unique=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="students", blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="students", blank=True, null=True)


    commment = models.TextField(blank=True)

    default_price = models.fields.DecimalField(max_digits=4, decimal_places=1, default=decimal.Decimal(20.0))

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
    


class Lesson(models.Model):
    STATUS_CHOICES = [
        ("planned", "Prévue"),
        ("done", "Faite"),
        ("cancelled", "Annulée"),
        ("missed", "Absence"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="lessons")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="lessons")

    date = models.fields.DateTimeField(default=timezone.now)
    duration = models.fields.DurationField(default=timedelta(hours=1))

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    homeworks = models.fields.CharField(max_length=255, blank=True) # for the student, before
    reminder = models.fields.CharField(max_length=255, blank=True) # for the professor, before
    notes = models.fields.CharField(max_length=255, blank=True) # for the student, after
    commment = models.fields.CharField(max_length=255, blank=True) # for the professor, after

    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.fields.DecimalField(max_digits=4, decimal_places=1, default=decimal.Decimal(20.0))
    paid = models.fields.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "professor", "date"],
                name="unique_lesson_student_professor_date"
            )
        ]

    @property
    def date_formated(self):
        return self.date.astimezone(timezone.get_default_timezone()).strftime('%y-%m-%d-%H-%M')

    @property
    def is_past(self):
        return self.date < timezone.now()

    @property
    def is_upcoming(self):
        return self.date + self.duration >= timezone.now()

    def __str__(self):
        return f"{self.student} - {self.date:%d/%m/%Y %H:%M}"



