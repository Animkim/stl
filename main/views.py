from django.http import HttpResponse

from stl.robots import RobotsCompiler
from stl.main.route import Route


def robots(request):
    return HttpResponse(RobotsCompiler().compile(request.get_host()), content_type='text/plain')


def route(request, path='/'):
    return Route(request, path).render()
