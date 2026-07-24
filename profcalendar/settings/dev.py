from .base import *
from typing import Any

DEBUG = True

DATABASES: dict[str, Any] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

ALLOWED_HOSTS: list[str] = [
    "localhost",
    "192.168.1.27"
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"