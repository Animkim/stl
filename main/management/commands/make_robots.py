import os

from django.conf import settings
from django.core.management.base import BaseCommand

from stl.robots import RobotsCompiler


class Command(BaseCommand):
    def handle(self, **options):
        robots = os.path.join(settings.MEDIA_ROOT, 'robots', 'robots.txt')
        if not os.path.isfile(robots):
            with open(robots, 'w') as fl:
                fl.write(RobotsCompiler().compile(settings.DOMAIN))
