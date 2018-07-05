import os

from django.conf import settings
from django.core.management.base import BaseCommand

from stl.robots import RobotsCompiler


class Command(BaseCommand):
    def handle(self, **options):
        with open(os.path.join(settings.MEDIA_ROOT, 'robots', 'robots.txt'), 'w') as fl:
            fl.write(RobotsCompiler().compile(settings.DOMAIN))
