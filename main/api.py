import requests

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
        for chunk in zip(*[iter(ads)]*100):
            ads = self._get_request('get_ads', {'ads': chunk})
            [AdCreator(data).process() for data in ads]


class AbsCreator(object):
    lang = settings.ACTIVE_LANG

    def __init__(self, data):
        self.data = data
        self.fields = getattr(self, 'fields', [])

    def _process(self):
        for field in self.fields:
            extractor = getattr(self, '_%s_extract' % field, None)
            extractor and extractor()
        return self.create_model()

    def process(self):
        self._process()

    def create_model(self):
        raise Exception


class PlaceCreator(AbsCreator):
    fields = ['name', 'path']

    def create_model(self):
        fields = [field.attname for field in Place._meta.fields]
        data = {key: val for key, val in self.data.items() if key in fields}
        return Place.objects.create(**data)

    def _name_extract(self):
        field = 'name_{0}'.format(self.lang)
        self.data['name'] = self.data[field]

    def _path_extract(self):
        self.data['path'] = self.data['path'].strip('/')


class AdCreator(AbsCreator):
    fields = ['id', 'object_type', 'price', 'photo', 'title']

    def process(self):
        ad = self._process()
        if ad:
            places = Place.objects.filter(pk__in=self.data.get('places'))
            ad.places.set(places)

    def create_model(self):
        fields = [field.attname for field in Ad._meta.fields]
        data = {key: val for key, val in self.data.items() if key in fields}
        if not data['object_type_id']:
            return None
        with open('test.log', 'w') as f:
            f.write(str(data.get('photos', [])))

        photos = [AdPhoto.objects.create(photo=photo) for photo in self.data.get('photos', [])]
        ad = Ad.objects.create(**data)
        ad.photos.set(photos)
        return Ad.objects.create(**data)

    def _id_extract(self):
        self.data['id'] = None

    def _object_type_extract(self):
        try:
            ot = ObjectType.objects.get(slug=self.data['object_type']).pk
        except (ObjectType.DoesNotExist, ValueError):
            ot = None

        self.data['object_type_id'] = ot

    def _price_extract(self):
        self.data['price'] = self.data['price_euro']

    def _photo_extract(self):
        self.data['photo_id'] = None

    def _title_extract(self):
        field = 'desc_title_{0}'.format(self.lang)
        self.data['title'] = self.data[field]
