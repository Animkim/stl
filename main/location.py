import urllib.parse

from django.db.models import F
from django.http import Http404
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage

from stl.shortcuts import parse_int
from stl.main.models import Place, Ad


class LocationPage(object):
    def __init__(self, path, page=None):
        self.path = path
        self.page = page or 1
        self.place = None

        self._check_path()

    def _check_path(self):
        try:
            self.place = Place.objects.get(path=self.path)
        except Place.DoesNotExist:
            raise Http404

    def get_ads(self):
        return self.place.ads.all()

    def get_ads_count(self):
        return self.get_ads().count()

    def paginator(self):
        paginator = Paginator(self.get_ads(), 10)
        try:
            ads = paginator.page(parse_int(self.page))
        except (EmptyPage, ValueError):
            raise Http404
        return ads


class AdQuery(object):
    orders = {
        'price': ('price_euro', ), '-price': ('-price_euro', ),
        'date': ('novelty', ), '-date': ('-novelty', ),
        'profit': ('-profit', ), 'rank': ('-rank', ),
    }

    def __init__(self, params=None, user=None):
        self.raw = dict((params or {}).items())
        self.query = Ad.objects.all()
        self.params = {}
        self.options = {}
        self._init(user)

    def _init(self, user):
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

        # self.options['type'] = len(self.options.get('types', [])) == 1 and self.options['types'][0] or None
        # self.options['place'] = (self.options.get('places') or [None])[0]

    def url(self):
        params = self.params.copy()
        # params['places'] = ':'.join(filter(lambda p: p != '0', split(params.get('places', ''), ':')))
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
    #
    # def _filter_modifier(self, modifier):
    #     if modifier in ModifierManager.MODIFIERS:
    #         modifier = ModifierManager.MODIFIERS[modifier]
    #     if modifier not in ModifierManager.MODIFIERS.values():
    #         return
    #     self.query = self.query.extra(where=['modifier & {0} = {0}'.format(modifier.mask)])
    #     return modifier.slug, modifier
    #
    # def _filter_feature(self, feature):
    #     if feature in FeatureManager.MODIFIERS:
    #         feature = FeatureManager.MODIFIERS[feature]
    #     if feature not in FeatureManager.MODIFIERS.values():
    #         return
    #     self.query = self.query.extra(where=['feature & {0} = {0}'.format(feature.mask)])
    #     return feature.slug, feature

    def _filter_options(self, options):
        options = sorted(set(options))
        self.query = self.query.filter(options__contains=options)
        return ''.join(options), options

    # def _filter_distance_sea(self, distance_sea):
    #     distance_sea = int(distance_sea)
    #     if not distance_sea:
    #         return
    #
    #     self.query = self.query.filter(advert__distance_sea__lt=distance_sea)
    #     return str(distance_sea), distance_sea

    def _filter_area_object_from(self, area):
        area = parse_int(area)
        if area:
            self.query = self.query.filter(area_object__gte=area)
            return str(area), area

    def _filter_area_object_to(self, area):
        area = parse_int(area)
        if area:
            self.query = self.query.filter(area_object__lte=area)
            return str(area), area

    def _filter_area_land_from(self, area):
        area = parse_int(area)
        if area:
            self.query = self.query.filter(area_land__gte=area)
            return str(area), area

    def _filter_area_land_to(self, area):
        area = parse_int(area)
        if area:
            self.query = self.query.filter(area_land__lte=area)
            return str(area), area

    def _filter_rooms_total(self, rooms):
        rooms = parse_int(rooms)
        if rooms:
            self.query = self.query.filter(advert__rooms_total__gte=rooms)
            return str(rooms), rooms

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

    def _filter_beds_number(self, beds):
        beds = parse_int(beds)
        if beds:
            self.query = self.query.filter(beds_number__gte=beds)
            return str(beds), beds

    def _filter_profitability(self, profitability):
        profitability = parse_int(profitability)
        if profitability:
            self.query = self.query.filter(profitability__gte=profitability)
            return str(profitability), profitability

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

    def _filter_absolute_return(self, absolute_return):
        absolute_return = parse_int(absolute_return)
        if absolute_return:
            self.query = self.query.filter(absolute_return__gte=absolute_return)
            return str(absolute_return), absolute_return

    def _filter_owner_capital(self, owner_capital):
        owner_capital = parse_int(owner_capital)
        if owner_capital and self.params.get('purpose') != 'rent':
            if owner_capital < 100:
                self.query = self.query.filter(owner_capital__gte=F('selling_price')*owner_capital/100.0)
            else:
                self.query = self.query.filter(owner_capital__gte=owner_capital)
            return str(owner_capital), owner_capital

    def _filter_construction_year_from(self, year):
        year = parse_int(year)
        try:
            self.query = self.query.filter(construction_year__gte=year)
        except (TypeError, ValueError):
            return
        return str(year), year

    def _filter_construction_year_to(self, year):
        year = parse_int(year)
        try:
            self.query = self.query.filter(construction_year__lte=year)
        except (TypeError, ValueError):
            return
        return str(year), year
