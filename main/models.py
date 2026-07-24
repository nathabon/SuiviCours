from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator 
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

    @property
    def title(self):
        if self.short is None or self.short != '':
            return self.short

        return self.name


class Level(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=100, blank=True)
    slug  = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def title(self):
        if self.short is None or self.short != '':
            return self.short

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
        return f"{self.level.title} - {self.subject.title} - {self.title}"


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
    
    @property
    def money_total(self):
        return sum([l.price for l in self.lessons.all()])
    
    @property
    def money_get(self):
        return sum([l.price for l in self.lessons.all() if l.paid])

    def __str__(self) -> str:
        return self.name



class Student(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=False, null=False)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="students")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=100, unique=True)

    email = models.EmailField(blank=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="students", blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="students", blank=True, null=True)

    comment = models.TextField(blank=True)

    default_price = models.fields.DecimalField(max_digits=4, decimal_places=1, default=decimal.Decimal(20.0))

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self):
        super().clean()

        if self.subject_id and self.level_id:
            chapter_exists = Chapter.objects.filter(
                subject_id=self.subject_id,
                level_id=self.level_id
            ).exists()

            if not chapter_exists:
                raise ValidationError({
                    "subject": f"Aucun chapitre n’existe pour cette matière à ce niveau.",
                    "level": f"Aucun chapitre n’existe pour ce niveau dans cette matière.",
                })
    
    @property
    def full_name(self):
        return self.first_name + " " + self.last_name
    
    @property
    def initials(self):
        return self.first_name[0] + self.last_name[0]
    
    @property
    def next_lessons(self):
        return self.lessons.filter(date__gt=timezone.now()).order_by("date")
    


class Lesson(models.Model):
    STATUS_CHOICES = [
        ("planned", "Prévue"),
        ("done", "Faite"),
        ("cancelled", "Annulée"),
        ("missed", "Absence"),
    ]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "professor", "date"],
                name="unique_lesson_student_professor_date"
            )
        ]


    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="lessons")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="lessons")

    date = models.fields.DateTimeField(default=timezone.now)
    duration = models.fields.DurationField(default=timedelta(hours=1))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    note = models.PositiveIntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(5)])


    homeworks = models.fields.CharField(max_length=255, blank=True, help_text="À l'intention de l'étudiant") # for the student, before
    reminder = models.fields.CharField(max_length=255, blank=True, help_text="Pour le professeur") # for the professor, before
    notes = models.fields.CharField(max_length=255, blank=True, help_text="Visible par l'étudiant pour voir un recap de la séance") # for the student, after
    comment = models.fields.CharField(max_length=255, blank=True, help_text="Pour le professeur pour avoir des notes sur la séance") # for the professor, after

    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.fields.DecimalField(max_digits=4, decimal_places=1, default=decimal.Decimal(20.0))
    paid = models.fields.BooleanField(default=False)
    

    @property
    def date_formated(self):
        return self.date.astimezone(timezone.get_default_timezone()).strftime('%y-%m-%d-%H-%M')
    
    @property
    def end_date(self):
        return self.date + self.duration

    @property
    def is_passed(self):
        return self.date < timezone.now()

    @property
    def is_upcoming(self):
        return self.date + self.duration >= timezone.now()

    def __str__(self):
        return f"{self.student} - {self.date:%d/%m/%Y %H:%M}"
    
    def toEvent(self):
        return {
            "title": self.student.full_name,
            # "id": self.date_formated,
            "start": self.date.isoformat(),
            "end": self.end_date.isoformat(),
            "editable": False
        }



class Goal(models.Model):
    TYPE_CHOICES = [
        ("exam", "Examen"),
        ("year", "Année")
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="exam")
    date = models.DateField()
    done = models.BooleanField(default=False)
