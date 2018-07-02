import os
import datetime


from lxml import etree

from django.conf import settings
from django.core.management.base import BaseCommand

from stl.main.models import Ad, Place


SITE_NAME = 'https://%s' % settings.DOMAIN
SITEMAP_FOLDER = '%ssitemaps' % settings.MEDIA_ROOT
NAME_SPACE = 'http://www.sitemaps.org/schemas/sitemap/0.9'
NS_MAP = {None: NAME_SPACE}
URLS_PER_FILE = 50 * 1000
LASTMOD_FORMAT = '%Y-%m-%d'


class LocationURLs(object):
    @staticmethod
    def make():
        urls = []
        places = Place.objects.filter(ads_count__gt=0).order_by('-wordstat')
        for place in places.iterator():
            urls.append('/%s/' % place.path)
        return [{'loc': SITE_NAME + url} for url in filter(bool, sorted(set(urls)))]


class AdURLs(object):
    @staticmethod
    def make():
        data = []
        ads = Ad.objects.all()
        for ad in ads.select_related('place').iterator():
            loc = '{}{}'.format(SITE_NAME, ad.link)
            data.append({'loc': loc, 'lastmod': ad.changed_at.strftime(LASTMOD_FORMAT), 'priority': '0.9'})
        return data


class XMLFormer(object):
    def __init__(self):
        self.sitemap_index = etree.Element('{%s}sitemapindex' % NAME_SPACE, nsmap=NS_MAP)

    def _make_sitemap_for_file(self, filename):
        sitemap = etree.Element('sitemap')

        loc = etree.Element('loc')
        loc.text = '%s/%s' % (SITE_NAME, filename)
        sitemap.append(loc)

        lastmod = etree.Element('lastmod')
        lastmod.text = datetime.datetime.now().strftime(LASTMOD_FORMAT)
        sitemap.append(lastmod)
        return sitemap

    def _make_url_node(self, data):
        root = etree.Element('url')
        for key, value in data.items():
            node = etree.Element(key)
            node.text = value
            root.append(node)
        return root

    def to_xml(self, data_list):
        xml = etree.Element('{%s}urlset' % NAME_SPACE, nsmap=NS_MAP)
        for data in data_list:
            xml.append(self._make_url_node(data))
        return xml

    def dump(self, name, data_list):
        for n in range(len(data_list) // URLS_PER_FILE + 1):
            data_piece = data_list[n*URLS_PER_FILE:(n+1)*URLS_PER_FILE]
            filename = '%s%.3d.xml' % (name, n)
            xml = self.to_xml(data_piece)
            with open('%s/%s' % (SITEMAP_FOLDER, filename), 'w') as chunk:
                chunk.write(etree.tostring(xml, xml_declaration=True, encoding='utf-8', pretty_print=True))
            self.sitemap_index.append(self._make_sitemap_for_file(filename))

    def save_sitemapindex(self):
        self.clear_sitemap_folder()
        with open('%s/%s' % (SITEMAP_FOLDER, 'sitemap.xml'), 'w') as xml:
            xml.write(etree.tostring(self.sitemap_index, xml_declaration=True, encoding='utf-8', pretty_print=True))

    def clear_sitemap_folder(self):
        in_sitemap = {i.split('/')[-1] for i in self.sitemap_index.xpath('//loc//text()')}
        all_files = set(os.listdir(SITEMAP_FOLDER))
        for filename in all_files - in_sitemap:
            os.unlink('%s/%s' % (SITEMAP_FOLDER, filename))


class Command(BaseCommand):
    def handle(self, **options):
        builders = {'locations': LocationURLs, 'adt': AdURLs}
        self.make('https://%s' % settings.DOMAIN, 'sitemaps', builders)

    def make(self, site_name, folder, builders):
        global SITE_NAME
        global SITEMAP_FOLDER
        SITE_NAME = site_name
        SITEMAP_FOLDER = os.path.join(settings.MEDIA_ROOT, folder)
        if not os.path.exists(SITEMAP_FOLDER):
            os.mkdir(SITEMAP_FOLDER)

        former = XMLFormer()
        for name, builder in builders.items():
            former.dump(name, builder().make())
        former.save_sitemapindex()
