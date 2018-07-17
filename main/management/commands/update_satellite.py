from django.core.management.base import BaseCommand

from main.api import TranioApi


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--ads', help='update Ad model', action='store_true')
        parser.add_argument('--types', help='update ObjectType model', action='store_true')
        parser.add_argument('--places', help='update Place model', action='store_true')
        parser.add_argument('--pages', help='update StaticPage model', action='store_true')
        parser.add_argument('--meta', help='update MetaData model', action='store_true')
        parser.add_argument('--all', help='update all models', action='store_true')

    def handle(self, *args, **options):
        TranioApi().process(args)

