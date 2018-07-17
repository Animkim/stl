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
            creator = DefaultCreator(ObjectType, data)
            creator.process()

        for data in types:
            parent, children = data['slug'], data['children']
            if not children:
                continue

            parent = ObjectType.objects.get(slug=parent)
            ObjectType.objects.filter(slug__in=children).update(parent=parent)

    def parse_places(self):
        places = self._get_request('get_places')
        for data in places:
            creator = DefaultCreator(Place, data)
            creator.process()

    def parse_ads(self):
        ads = self._get_request('get_ads')
        for chunk in zip_longest(*[iter(ads)]*100):
            ads = self._get_request('get_ads', {'ads': chunk})
            for data in ads:
                creator = AdCreator(Ad, data)
                creator.process()


class DefaultCreator(object):
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.clean_data = self._clear_data()

    def _clear_data(self):
        fields = [field.attname for field in self.model._meta.fields]
        return {key: val for key, val in self.data.items() if key in fields}

    def process(self):
        self.pre_save()
        self.model = self.model(**self.clean_data)
        self.model.save()
        self.post_save()
        return self.model

    def pre_save(self):
        pass

    def post_save(self):
        pass


class AdCreator(DefaultCreator):
    def pre_save(self):
        self.clean_data['object_type'] = ObjectType.objects.filter(char_id=self.data.get('object_type')).first()
        self.clean_data['place'] = Place.objects.filter(pk=self.data.get('place')).first()

    def post_save(self):
        photos = self.data.get('photos', [])
        existing_photos = AdPhoto.objects.filter(photo__in=photos).values_list('photo', flat=True)
        for photo in photos:
            if photo in existing_photos:
                continue
            AdPhoto.objects.create(photo=photo)
        self.model.photos.set(AdPhoto.objects.filter(photo__in=photos))
        self.model.places.set(Place.objects.filter(pk__in=self.data.get('places')))
