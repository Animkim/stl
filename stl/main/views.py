from django.http import Http404
from django.shortcuts import render_to_response

from main.ad import AdPage
from main.models import Ad
from main.location import LocationPage


def main_page(request):
    return render_to_response('main.html', {''}, request)


def location_page(request, path):
    page = request.GET.get('page')
    return render_to_response('location.html', {'rp': LocationPage(path, page)}, request)


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
