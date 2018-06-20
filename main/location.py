from django.http import Http404
from django.core.paginator import Paginator, EmptyPage

from stl.main.models import Place, Ad


class LocationPage(object):
    def __init__(self, path, page=None):
        self.path = path
        self.page = page or 1
        self.place = None

        self._check_path()

    def _check_path(self):
        print(self.path)
        try:
            self.place = Place.objects.get(path=self.path)
        except Place.DoesNotExist:
            raise Http404

    def get_ads(self):
        return self.place.ads.all()

    def get_ads_count(self):
        return self.get_ads().count()

    def paginator(self):
        paginator = Paginator(self.get_ads(), 10)
        try:
            ads = paginator.page(int(self.page))
        except (EmptyPage, ValueError):
            raise Http404
        return ads
