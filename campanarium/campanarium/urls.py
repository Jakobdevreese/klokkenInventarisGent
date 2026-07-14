"""
URL configuration for campanarium project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from inventory import views

urlpatterns = [
    path('', views.home_view, name='home'),

    path('klokken/', views.bell_view, name='bells'),
    path('klokken/toevoegen/', views.add_bell_view, name='add_bell'),
    path('klokken/<int:pk>/', views.bell_detail_view, name='bell_detail'),

    path('beiaarden/', views.carillon_view, name='carillons'),
    path('beiaarden/<int:pk>/', views.carillon_detail_view, name='carillon_detail'),

    path('torens/', views.tower_view, name='towers'),
    path('torens/<int:pk>/', views.tower_detail_view, name='tower_detail'),

    path('gieters/', views.manufacturer_view, name='manufacturers'),
    path('gieters/<int:pk>/', views.manufacturer_detail_view, name='manufacturer_detail'),

    path('zoeken/', views.search_view, name='search'),
    path('feedback/', views.feedback_view, name='feedback'),

    path('admin/', admin.site.urls),
]

# Serve user-uploaded media during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
