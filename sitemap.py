from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from django.conf import settings

from stl.main.models import Ad, Place


class BaseSitemap(Sitemap):
    def get_urls(self, site=None, **kwargs):
        site = Site(domain=settings.DOMAIN, name=settings.DOMAIN)
        return super(BaseSitemap, self).get_urls(site=site, **kwargs)


class AdSitemap(BaseSitemap):
    priority = 0.9

    def items(self):
        return Ad.objects.all()

    def lastmod(self, obj):
        return obj.changed_at


class PlaceSitemap(BaseSitemap):
    def items(self):
        return Place.objects.all()
