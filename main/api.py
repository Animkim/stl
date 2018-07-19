import requests

from itertools import zip_longest

from django.conf import settings

from stl.main.models import Ad, AdPhoto, Place, ObjectType, StaticPage, MetaData
from stl.main.creators import DefaultCreator, AdCreator


class TranioApi(object):
    @staticmethod
    def _get_request(method, data=None):
        if not method:
            raise ValueError

        data = data or {}
        data.update({'token': settings.TOKEN_API})
        request = requests.get('https://tranio.iru/satellite/api/{0}/'.format(method), params=data, verify=False)
        if request.status_code == 200:
            return request.json()
        return []

    def process(self, methods, full=False):
        all_methods = [m for m in dir(self) if m.startswith('parse_')]
        methods = all_methods if full else methods
        for method in methods:
            if not method.startswith('parse_'):
                method = 'parse_{}'.format(method)
            getattr(self, method, lambda: None)()

    def parse_types(self):
        types = self._get_request('get_types')
        if types:
            ObjectType.objects.all().delete()

        for data in types:
            creator = DefaultCreator(ObjectType, data)
            creator.process()

    def parse_places(self):
        places = self._get_request('get_places')
        if places:
            Place.objects.all().delete()

        for data in places:
            creator = DefaultCreator(Place, data)
            creator.process()

    def parse_ads(self):
        ads = self._get_request('get_ads')
        if ads:
            Ad.objects.all().delete()
            AdPhoto.objects.all().delete()

        for chunk in zip_longest(*[iter(ads)]*100):
            ads = self._get_request('get_ads', {'ads': ', '.join(chunk)})
            for data in ads:
                creator = AdCreator(Ad, data)
                creator.process()
        # self._get_request('sync_photos')

    def parse_static_pages(self):
        pages = self._get_request('get_static_pages')
        if pages:
            StaticPage.objects.all().delete()

        for data in pages:
            creator = DefaultCreator(StaticPage, data)
            creator.process()

    def parse_meta_data(self):
        meta = self._get_request('get_meta_data')
        if meta:
            MetaData.objects.all().delete()

        for data in meta:
            creator = DefaultCreator(MetaData, data)
            creator.process()
