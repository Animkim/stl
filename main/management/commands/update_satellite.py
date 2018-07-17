from django.core.management.base import BaseCommand

from main.api import TranioApi


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str, help='email')
        parser.add_argument('--date_range', dest='date_range', type=str, help='dd.mm.yyyy-dd.mm.yyyy')

    def handle(self, *args, **options):
        TranioApi().process(args)

