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
            data = {k: v for k, v in data.items() if k in ('name', 'slug', 'letter_id')}
            ObjectType.objects.create(**data)

        for data in types:
            parent, children = data['slug'], data['children']
            if not children:
                continue

            parent = ObjectType.objects.get(slug=parent)
            ObjectType.objects.filter(slug__in=children).update(parent=parent)

    def parse_places(self):
        places = self._get_request('get_places')
        for data in places:
            clean_data = self._clean_data(Place, data)
            Place.objects.create(**clean_data)

    def parse_ads(self):
        ads = self._get_request('get_ads')
        for chunk in zip_longest(*[iter(ads)]*100):
            ads = self._get_request('get_ads', {'ads': chunk})
            for data in ads:
                clean_data = self._clean_data(Ad, data)
                if not data['object_type']:
                    return
                clean_data['object_type'] = ObjectType.objects.filter(letter_id=data['object_type']).first()
                clean_data['place'] = Place.objects.filter(pk=data['place']).first()

                ad = Ad(**clean_data)
                ad.save()
                existing_photos = AdPhoto.objects.filter(photo__in=data['photos']).values_list('pk', flat=True)
                [AdPhoto.objects.create(id=pk) for pk in data['photos'] if pk not in existing_photos]
                ad.photos.set(AdPhoto.objects.filter(id__in=data['photos']))
                ad.places.set(Place.objects.filter(pk__in=data.get('places', [])))


    @staticmethod
    def _clean_data(model, data):
        fields = [field.attname for field in model._meta.fields]
        return {key: val for key, val in data.items() if key in fields}
