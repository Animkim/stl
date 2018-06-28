import urllib.parse

from django.http import Http404
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage

from stl.shortcuts import parse_int
from stl.main.models import Place, Ad


class LocationPage(object):
    def __init__(self, path, page=None, params=None):
        self.path = path
        self.page = page or 1
        self.adq = AdQuery(params)
        self.place = None

        self._check_path()

    def _check_path(self):
        if not self.path:
            return
        try:
            self.place = Place.objects.get(path=self.path)
        except Place.DoesNotExist:
            raise Http404

    def get_ads(self):
        if not self.place:
            return self.adq.query
        return self.place.ads.all()

    def get_ads_count(self):
        return self.get_ads().count()

    def href(self):
        if not self.place:
            return self.adq.url()
        return self.place.path

    def paginator(self):
        paginator = Paginator(self.get_ads(), 10)
        try:
            ads = paginator.page(parse_int(self.page))
        except (EmptyPage, ValueError):
            raise Http404
        return ads


class AdQuery(object):
    orders = {
        'price': ('price', ), '-price': ('-price', ),
        'date': ('novelty', ), '-date': ('-novelty', ),
        'profit': ('-profit', ), 'rank': ('-rank', ),
    }

    def __init__(self, params=None):
        self.raw = dict((params or {}).items())
        self.query = Ad.objects.all()
        self.params = {}
        self.options = {}

        self.raw['order'] = self.raw.get('order') or 'default'
        self.raw['types'] = self.raw.get('types') or self.raw.get('type')
        self.raw['places'] = self.raw.get('places') or self.raw.get('place')

        for key, value in self.raw.items():
            value = value.strip() if hasattr(value, 'strip') else value
            if not value:
                continue

            filter_name = '_filter_%s' % slugify(key.lower())
            filter_method = getattr(self, filter_name, lambda *a, **kw: None)
            result = filter_method(value)
            if isinstance(result, tuple) and len(result) == 2:
                self.params[key], self.options[key] = result

    def url(self):
        params = self.params.copy()
        params = sorted(filter(lambda i: bool(i[1]), params.items()))
        link = u'%s?%s' % ('/search/', urllib.parse.urlencode(params))
        return link

    def get_ads(self):
        return self.query

    def _filter_order(self, order):
        if order in self.orders:
            self.query = self.query.order_by(*self.orders[order])
            return order, order
        self.query = self.query.order_by('-rank')
        return '', ''

    def _filter_price_from(self, price_from):
        price_from = parse_int(price_from)
        if price_from:
            self.query = self.query.filter(price__gte=price_from)
            return str(price_from), price_from

    def _filter_price_to(self, price_to):
        price_to = parse_int(price_to)
        if price_to:
            self.query = self.query.filter(price__lte=price_to)
            return str(price_to), price_to

    def _filter_places(self, places):
        if isinstance(places, Place):
            self.query = self.query.filter(places__in=[places.pk])
            return str(places.pk), [places]

        if isinstance(places, (set, tuple, list)):
            places = ':'.join(sorted([str(p.pk) for p in places]))

        if isinstance(places, str):
            places = sorted(map(parse_int, urllib.parse.unquote_plus(places).split(':')))
            self.query = self.query.filter(places__in=places)
            return ':'.join(map(str, places)), Place.objects.filter(pk__in=places)

    def _filter_types(self, types):
        types = set(urllib.parse.unquote_plus(types))
        self.query = self.query.filter(object_type__in=types) if types else self.query
        return types, types

    def _filter_rooms_bath(self, rooms):
        rooms = parse_int(rooms)
        if rooms:
            self.query = self.query.filter(rooms_bath__gte=rooms)
            return str(rooms), rooms

    def _filter_rooms_bed(self, rooms):
        rooms = parse_int(rooms)
        if rooms:
            self.query = self.query.filter(rooms_bed__gte=rooms)
            return str(rooms), rooms

    def _filter_yield_from(self, percent):
        percent = parse_int(percent)
        if percent:
            self.query = self.query.filter(profitability__gte=percent)
            return str(percent), percent

    def _filter_yield_to(self, percent):
        percent = parse_int(percent)
        if percent:
            self.query = self.query.filter(profitability__lte=percent)
            return str(percent), percent
