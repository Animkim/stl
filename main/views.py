from django.http import Http404
from django.shortcuts import render_to_response

from stl.main.ad import AdPage
from stl.main.models import Ad
from stl.main.location import LocationPage


def main_page(request):
    return render_to_response('main.html', {''}, request)


def location_page(request, path=None):
    page = request.GET.get('page')
    params = dict(request.GET.items())
    return render_to_response('location.html', {'rp': LocationPage(path, page, params)}, request)


def ad_page(request, pk):
    try:
        ad = Ad.objects.get(pk=pk)
    except Ad.DoesNotExist:
        raise Http404
    return render_to_response('ad.html', {'ap': AdPage(ad)}, request)


def about_page(request, slug):
    template = {'about': 'about.html'}.get(slug)
    if not template:
        raise Http404

    return render_to_response('about.html', {}, request)
