from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('spaces/', views.properties, name='properties'),
    path('details/', views.property_details, name='property_details'),
    path('contact/', views.contact, name='contact'),
    path('api/book/', views.api_book, name='api_book'),
]

