import argparse
from datetime import date
from django.core.management.base import BaseCommand, CommandError
import survey.util.importer as importer

class Command(BaseCommand):
    help = 'Import site listing issue from file'

    def add_arguments(self, parser):
        parser.add_argument('listing_file', type=argparse.FileType("r"))
        parser.add_argument('listing_name', type=str)
        parser.add_argument('issue_date', type=date.fromisoformat)

    def handle(self, *args, **options):
        listing_file = options['listing_file']
        with listing_file:
            listing_path = listing_file.name
        name = options['listing_name']
        issue_date = options['issue_date']

        importer.import_sites_from_file(
            listing_path,
            name,
            issue_date,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported listing {name} issue {issue_date}'
        ))
