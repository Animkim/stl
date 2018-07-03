from django.urls import path
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from stl.sitemap import AdSitemap
from stl.main import views

urlpatterns = [
    path('', views.main_page),
    path('robots.txt/', views.robots),
    path('sitemap.xml', sitemap, {'sitemaps': {'ad': AdSitemap}},
         name='django.contrib.sitemaps.views.sitemap'),
    path('{ad}'.format(ad=settings.AD_PATH), views.ad_page, name='ad'),
    path('{location}'.format(location=settings.LOCATION_PATH), views.location_page),
]
