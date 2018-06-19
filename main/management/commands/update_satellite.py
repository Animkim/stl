from django.core.management.base import BaseCommand

from main.api import TranioApi


class Command(BaseCommand):
    def handle(self, **options):
        TranioApi().process()

