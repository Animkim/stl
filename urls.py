from django.urls import path

from stl.main import views

urlpatterns = [
    path('robots.txt/', views.robots),
    path('', views.route, path='/'),
    path('<path:path>', views.route),
]
