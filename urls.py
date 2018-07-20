from django.urls import path

from stl.main import views

urlpatterns = [
    path('robots.txt/', views.robots),
    path('<path:path>/', views.route),
]
