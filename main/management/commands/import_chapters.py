import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from main.models import Subject, Level, Chapter


class Command(BaseCommand):
    help = "Import subjects, levels and chapters from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the JSON file containing chapters"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise CommandError(f"File not found: {json_file}")
        except json.JSONDecodeError as error:
            raise CommandError(f"Invalid JSON file: {error}")

        if isinstance(data, dict):
            data = [data]

        subjects_created = 0
        levels_created = 0
        chapters_created = 0
        chapters_existing = 0

        with transaction.atomic():
            for item in data:
                subject_name = item.get("matiere")
                level_name = item.get("niveau")
                chapters = item.get("chapitres", [])

                if not subject_name or not level_name:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipped item with missing matiere or niveau: {item}"
                        )
                    )
                    continue

                subject_name = subject_name.strip()
                level_name = level_name.strip()

                subject, subject_was_created = Subject.objects.get_or_create(
                    name=subject_name,
                    defaults={
                        "slug": slugify(subject_name)
                    }
                )

                if subject_was_created:
                    subjects_created += 1

                level, level_was_created = Level.objects.get_or_create(
                    name=level_name,
                    defaults={
                        "slug": slugify(level_name)
                    }
                )

                if level_was_created:
                    levels_created += 1

                for chapter_title in chapters:
                    chapter_title = chapter_title.strip()

                    if not chapter_title:
                        continue

                    chapter, chapter_was_created = Chapter.objects.get_or_create(
                        subject=subject,
                        level=level,
                        title=chapter_title,
                    )

                    if chapter_was_created:
                        chapters_created += 1
                    else:
                        chapters_existing += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Import finished: "
                f"{subjects_created} subjects created, "
                f"{levels_created} levels created, "
                f"{chapters_created} chapters created, "
                f"{chapters_existing} chapters already existing."
            )
        )