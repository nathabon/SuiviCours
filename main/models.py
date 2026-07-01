from django.db import models
from django.contrib.auth.models import User, AbstractUser


class CustomUser(models.Model):
    PROFESSOR = 'professor'
    STUDENT = 'student'
    ROLE_CHOICES = [(PROFESSOR, 'Professeur'), (STUDENT, 'Élève')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,null=True, blank=True)


class Professor(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email

    def __str__(self) -> str:
        return self.user.username

