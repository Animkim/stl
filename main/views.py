from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response

from stl.main.ad import AdPage
from stl.main.models import Ad
from stl.main.location import LocationPage
from stl.robots import RobotsCompiler


def main_page(request):
    return render_to_response('main.html', {''}, request)


def location_page(request, path=None):
    page = request.GET.get('page')
    params = dict(request.GET.items())
    return render_to_response('location.html', {'rp': LocationPage(path, page, params)}, request)


def ad_page(request, **kwargs):
    try:
        ad = Ad.objects.get(**kwargs)
    except (Ad.DoesNotExist, ValueError):
        raise Http404
    return render_to_response('ad/ad.html', {'ap': AdPage(ad)}, request)


def robots(request):
    return HttpResponse(RobotsCompiler().compile(request.get_host()), content_type='text/plain')
