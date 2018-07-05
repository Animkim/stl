import requests

from itertools import zip_longest

from django.conf import settings

from stl.main.models import Ad, AdPhoto, Place, ObjectType


class TranioApi(object):
    @staticmethod
    def _get_request(url, json_data=None):
        if not url:
            raise ValueError

        data = {'token': settings.TOKEN_API}
        data.update(json_data or {})
        request = requests.post('https://tranio.iru/satellite/api/{0}/'.format(url), json=data, verify=False)
        if request.status_code == 200:
            return request.json()
        return []

    def process(self):
        self.clear_models()
        self.parse_types()
        self.parse_places()
        self.parse_ads()

    @staticmethod
    def clear_models():
        Ad.objects.all().delete()
        AdPhoto.objects.all().delete()
        Place.objects.all().delete()
        ObjectType.objects.all().delete()

    def parse_types(self):
        types = self._get_request('get_types')
        for data in types:
            data = {k: v for k, v in data.items() if k in ('name', 'slug')}
            ObjectType.objects.create(**data)

        for data in types:
            parent, children = data['slug'], data['children']
            if not children:
                continue

            parent = ObjectType.objects.get(slug=parent)
            ObjectType.objects.filter(slug__in=children).update(parent=parent)

    def parse_places(self):
        places = self._get_request('get_places')
        [PlaceCreator(data).process() for data in places]

    def parse_ads(self):
        ads = self._get_request('get_ads')
        for chunk in zip_longest(*[iter(ads)]*100):
            ads = self._get_request('get_ads', {'ads': chunk})
            [AdCreator(data).process() for data in ads]


class AdCreator(object):
    def __init__(self, data):
        self.data = AdCleaner(data).clear()

    def process(self):
        for method in dir(self):
            if not method.endswith('_extract'):
                continue
            extractor = getattr(self, method, None)
            extractor and extractor()

        if not self.data.get('object_type_id'):
            return None
        ad = Ad.objects.create(**self.data)
        ad.photos.set(self.get_photos())
        ad.places.set(Place.objects.filter(pk__in=self.data.get('places', [])))
        return ad

    def get_photos(self):
        existing_photos = AdPhoto.objects.filter(photo__in=self.data.get('photos', [])).values_list('photo', flat=True)
        for photo in self.data.get('photos', []):
            if photo in existing_photos:
                continue
            AdPhoto.objects.create(photo=photo)
        return AdPhoto.objects.filter(photo__in=self.data.get('photos', []))

    def _object_type_extract(self):
        try:
            self.data['object_type_id'] = ObjectType.objects.get(slug=self.data['object_type']).pk
        except (ObjectType.DoesNotExist, ValueError):
            pass


class PlaceCreator(object):
    def __init__(self, data):
        self.data = PlaceCleaner(data).clear()

    def process(self):
        for method in dir(self):
            if not method.endswith('_extract'):
                continue
            extractor = getattr(self, method, None)
            extractor and extractor()
        return Place.objects.create(**self.data)

    def _path_extract(self):
        self.data['path'] = self.data['path'].strip('/')


class AbsCleaner(object):
    drop_list = []
    multilang = []
    map_fields = []
    model = None

    def __init__(self, data):
        self.data = data
        self.clean_data = {}
        self.fields = [field.attname for field in self.model._meta.fields()]

    def clear(self):
        self._multilang_fields()
        self._mapping_fields()
        self._clear_data()
        return self.clean_data

    def _multilang_fields(self):
        for field in self.multilang:
            original_field = '{field}_{lang}'.format(field=field, lang=settings.ACTIVE_LANG)
            self.data[field] = self.data[original_field]

    def _mapping_fields(self):
        for field, new_field in self.map_fields:
            self.data[new_field] = self.data[field]

    def _clear_data(self):
        for field in self.fields:
            if field not in self.drop_list:
                self.clean_data[field] = self.data.get(field)


class AdCleaner(AbsCleaner):
    drop_list = ['id']
    multilang = ['desc_title']
    map_fields = [('desc_title', 'title'), ('rank_kludge', 'rank'), ('price_euro', 'price')]
    model = Ad


class PlaceCleaner(AbsCleaner):
    multilang = ['name']
    model = Place
