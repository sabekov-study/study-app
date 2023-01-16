import argparse
from django.core.management.base import BaseCommand, CommandError
from survey.models import Checklist

class Command(BaseCommand):
    help = 'Import checklist from JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=argparse.FileType("r"))

    def handle(self, *args, **options):
        json_file = options['json_file']
        checklist = Checklist.import_from_json(json_file.name)
        if checklist:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported checklist {checklist.name}'
            ))
