from django.contrib.sitemaps import Sitemap
from stl.main.models import Ad, Place


class AdSitemap(Sitemap):
    priority = 0.9

    def items(self):
        return Ad.objects.all()

    def lastmod(self, obj):
        return obj.changed_at
