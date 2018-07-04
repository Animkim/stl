from django.conf import settings


def context(request):
    return {
        'LANG': settings.ACTIVE_LANG
    }
