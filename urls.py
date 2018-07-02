from django.urls import path
from django.conf import settings

from stl.main import views

urlpatterns = [
    path('', views.main_page),
    path('robots\.txt', views.robots),
    path('{ad}'.format(ad=settings.AD_PATH), views.ad_page),
    path('{location}'.format(location=settings.LOCATION_PATH), views.location_page),
]
