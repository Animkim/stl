from django.urls import path
from django.contrib import admin

from main import views
admin.autodiscover()

urlpatterns = [
    path('', views.main_page),
    path('admin/', admin.site.urls),
    path('ad/<int:pk>/', views.ad_page),
    path('about/<slug:slug>/', views.about_page),
    path('<path:path>/', views.location_page),
]
