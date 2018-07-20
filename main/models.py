from django.db import models


class Ad(models.Model):
    changed_at = models.DateTimeField()
    title = models.TextField(u'Заголовок объявления')
    desc = models.TextField(u'Содержимое объявления')
    traits = models.TextField(u'Характеристики объявления')
    path = models.TextField(u'Активный url')

    photos = models.ManyToManyField('main.AdPhoto')

    # sorting
    rank_kludge = models.IntegerField(db_index=True, default=0)
    price = models.BigIntegerField(db_index=True)
    hide_price = models.BooleanField(u'Цена по запросу', default=False, db_index=True)

    place = models.ForeignKey('Place', verbose_name=u'Локация объекта', on_delete=models.PROTECT, null=True)
    places = models.ManyToManyField('Place', verbose_name=u'Входит в локации', related_name='ads')

    object_type = models.ForeignKey('ObjectType', on_delete=models.PROTECT, null=True)
    rooms_bed = models.IntegerField(u'Спальни', null=True)
    rooms_bath = models.IntegerField(u'Ванные', null=True)

    def __str__(self):
        return '#{0}'.format(self.pk)

    def get_absolute_url(self):
        return self.path


class Place(models.Model):
    wordstat = models.IntegerField(u'Wordstat', default=0)

    name = models.TextField(u'Топоним в именительном падеже')
    slug = models.TextField(u'Слаг, не уникален')
    path = models.TextField(u'Активный url')

    def __str__(self):
        return self.path

    def get_absolute_url(self):
        return self.path


class AdPhoto(models.Model):
    photo = models.FileField(upload_to='adt/')


class ObjectType(models.Model):
    name = models.TextField(u'Топоним в именительном падеже')
    slug = models.TextField()
    char_id = models.TextField()

    def __str__(self):
        return self.slug


class MetaData(models.Model):
    path = models.TextField()
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    def __str__(self):
        return self.path


class StaticPage(models.Model):
    path = models.TextField()
    content = models.TextField()
    page_title = models.TextField(u'Заглавие страницы', blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
