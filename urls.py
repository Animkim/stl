from django.urls import path, re_path

from stl.main import views

urlpatterns = [
    path('robots.txt/', views.robots),
    path('', views.route),
    re_path('/$', views.route),
]
