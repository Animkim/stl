import os
import sys
import requests

from itertools import zip_longest
from threading import Thread, RLock

from django.conf import settings
from django.core.management.base import OutputWrapper

from stl.main.models import Ad, AdPhoto, Place, ObjectType, StaticPage, MetaData, SiteData
from stl.main.creators import DefaultCreator, AdCreator
from stl.main.management.commands.make_sitemap import make_sitemap


class DownloadThread(Thread):
    def __init__(self, downloads, lock, number):
        self.lock = lock
        self.downloads = downloads
        super(DownloadThread, self).__init__(name='DownloadThread-%s' % number)

    def run(self):
        while True:
            self.lock.acquire()
            if not self.downloads:
                self.lock.release()
                break
            link, path = self.downloads.pop()
            self.lock.release()

            content = self.download(link)
            if content:
                with open(path, 'wb') as photo:
                    photo.write(content)

    def download(self, link):
        try:
            return requests.get(link).content
        except requests.exceptions.RequestException:
            return None


class TranioApi(object):
    def __init__(self):
        self.stdout = OutputWrapper(sys.stdout)

    @staticmethod
    def _get_request(method, data=None):
        if not method:
            raise ValueError

        data = data or {}
        data.update({'token': settings.TOKEN_API})
        request = requests.get('{url}{method}/'.format(url=settings.URL_API, method=method), params=data, verify=False)
        if request.status_code == 200:
            return request.json()
        return []

    def process(self, methods):
        if 'all' in methods:
            methods = ('site_data', 'types', 'places', 'ads', 'static_pages', 'meta_data')
        for method in methods:
            if not method.startswith('parse_'):
                method = 'parse_{}'.format(method)

            self.stdout.write('Start {}'.format(method))
            parse_count = getattr(self, method, lambda: None)()
            self.stdout.write('End {0} object parse {1}'.format(method, parse_count))

        self.stdout.write('Start make sitemap')
        make_sitemap()
        self.stdout.write('Sitemap ready')
        sys.exit(0)

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
            ads = self._get_request('get_ads', {'ads': ', '.join(str(pk) for pk in chunk if pk)})
            for data in ads:
                creator = AdCreator(Ad, data)
                creator.process()
        self.sync_photos()
        return Ad.objects.count()

    def parse_static_pages(self):
        pages = self._get_request('get_static_pages')
        if pages:
            StaticPage.objects.all().delete()

        for data in pages:
            creator = DefaultCreator(StaticPage, data)
            creator.process()
        return StaticPage.objects.count()

    def parse_meta_data(self):
        meta = self._get_request('get_meta_data')
        if meta:
            MetaData.objects.all().delete()

        for data in meta:
            creator = DefaultCreator(MetaData, data)
            creator.process()
        return MetaData.objects.count()

    def parse_site_data(self):
        site_data = self._get_request('get_site_data')
        if site_data:
            SiteData.objects.all().delete()

        for data in site_data:
            creator = DefaultCreator(SiteData, data)
            creator.process()
        return SiteData.objects.count()

    def sync_photos(self):
        self.stdout.write('Start sync photos')
        downloads = []
        for source, photo in AdPhoto.objects.values_list('download_link', 'photo'):
            path = '{static}{photo}'.format(static=settings.STATIC_ROOT, photo=photo)
            if os.path.isfile(path):
                continue
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            downloads.append((source, path))

        lock = RLock()
        for n in range(5):
            DownloadThread(downloads, lock, n).start()
        self.stdout.write('Photos all: {0} \n Photos downloaded {1}'.format(AdPhoto.objects.count(), len(downloads)))

