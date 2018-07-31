from django.http import Http404
from django.shortcuts import render_to_response

from stl.main.models import Ad, StaticPage
from stl.main.location import LocationPage


class Route(object):
    def __init__(self, request, path):
        self.request = request
        self.path = self.normalize(path)

    def render(self):
        for method in [self.static_page_path, self.ad_path, self.location_path]:
            response = method()
            if response:
                return response
        raise Http404

    @staticmethod
    def normalize(path):
        if not path.startswith('/'):
            path = '/{0}/'.format(path.strip('/'))
        return path

    def static_page_path(self):
        try:
            sp = StaticPage.objects.get(path=self.path)
            return render_to_response('static_page.html', {'sp': sp}, self.request)
        except StaticPage.DoesNotExist:
            pass

    def ad_path(self):
        try:
            ad = Ad.objects.get(path=self.path)
            return render_to_response('ad/ad.html', {'ad': ad}, self.request)
        except Ad.DoesNotExist:
            pass

    def location_path(self):
        params = dict(self.request.GET.items())
        params.update({'path': self.path})
        return render_to_response('location.html', {'lp': LocationPage(params)}, self.request)
