from django.urls import path, re_path

from stl.main import views

urlpatterns = [
    path('robots.txt/', views.robots),
    re_path('/$', views.route),
]
