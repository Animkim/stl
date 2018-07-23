from django.http import HttpResponse
from django.shortcuts import render_to_response

from stl.main.models import Ad, StaticPage
from stl.main.location import LocationPage
from stl.robots import RobotsCompiler


def robots(request):
    return HttpResponse(RobotsCompiler().compile(request.get_host()), content_type='text/plain')


def route(request, path):
    with open('test.txt', 'w') as fl:
        fl.write(path)

    try:
        sp = StaticPage.objects.get(path=request.path)
        return render_to_response('static_page.html', {'sp': sp})
    except StaticPage.DoesNotExist:
        pass

    try:
        ad = Ad.objects.get(path=request.path)
        return render_to_response('ad/ad.html', {'ad': ad}, request)
    except Ad.DoesNotExist:
        params = dict(request.GET.items())
        params.update({'path': request.path})
        return render_to_response('location.html', {'lp': LocationPage(params)}, request)
