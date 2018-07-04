import os

from django.conf import settings
from django.test import RequestFactory
from django.core.management.base import BaseCommand
from django.contrib.sitemaps.views import sitemap

from stl.sitemap import AdSitemap, PlaceSitemap


class Command(BaseCommand):
    def handle(self, **options):
        sitemaps = {'ad': AdSitemap, 'place': PlaceSitemap}
        factory = RequestFactory()
        request = factory.get('/')
        xml = sitemap(request, sitemaps)
        with open(os.path.join(settings.MEDIA_ROOT, 'sitemap', 'sitemap.xml'), 'w') as fl:
            fl.write(xml.content)
