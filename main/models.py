from django.db import models
from django.urls import reverse


class Ad(models.Model):
    changed_at = models.DateTimeField()

    title = models.TextField(u'Заголовок объявления')
    desc = models.TextField(u'Содержимое объявления')
    traits = models.TextField(u'Характеристики объявления')

    photos = models.ManyToManyField('main.AdPhoto')

    # sorting
    rank = models.IntegerField(db_index=True)
    price = models.BigIntegerField(db_index=True)
    hide_price = models.BooleanField(u'Цена по запросу', default=False, db_index=True)

    place = models.ForeignKey('Place', verbose_name=u'Локация объекта', on_delete=models.PROTECT)
    places = models.ManyToManyField('Place', verbose_name=u'Входит в локации', related_name='ads')

    object_type = models.ForeignKey('ObjectType', on_delete=models.PROTECT)
    rooms_bed = models.IntegerField(u'Спальни', null=True)
    rooms_bath = models.IntegerField(u'Ванные', null=True)

    def __str__(self):
        return '#{0}'.format(self.pk)

    def get_absolute_url(self):
        return reverse('ad', kwargs={'pk': self.pk})


class Place(models.Model):
    wordstat = models.IntegerField(u'Wordstat', default=0)

    name = models.TextField(u'Топоним в именительном падеже')
    slug = models.TextField(u'Слаг, не уникален')
    path = models.TextField(u'Активный url')

    def __str__(self):
        return self.path

    def get_absolute_url(self):
        return reverse('place', kwargs={'path': self.path})


class AdPhoto(models.Model):
    photo = models.FileField(upload_to='adt/')


class ObjectType(models.Model):
    name = models.TextField(u'Топоним в именительном падеже')
    slug = models.TextField()
    letter_id = models.TextField()
    parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.slug


class MetaData(models.Model):
    path = models.CharField(max_length=800)
    title = models.TextField()
    description = models.TextField()
    keywords = models.TextField()

    def __str__(self):
        return self.path
