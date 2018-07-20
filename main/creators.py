from datetime import datetime

from stl.main.models import AdPhoto, Place, ObjectType


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
        changed_at = self.data.get('created_at', '')
        if changed_at:
            self.clean_data['changed_at'] = datetime.strptime(changed_at, '%Y-%m-%d %H:%M:%S.%f')

    def post_save(self):
        photos = self.data.get('photos', [])
        existing_photos = AdPhoto.objects.filter(original_url__in=photos).values_list('original_url', flat=True)
        for photo_url in photos:
            if photo_url in existing_photos:
                continue
            AdPhoto.objects.create(original_url=photo_url)
        self.model.photos.set(AdPhoto.objects.filter(photo_url__in=photos))
        self.model.places.set(Place.objects.filter(pk__in=self.data.get('places')))
