from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('spaces/', views.properties, name='properties'),
    path('details/', views.property_details, name='property_details'),
    path('space-details/', views.property_details, name='space_details'),  # Fix for sitemap.xml URL
    path('contact/', views.contact, name='contact'),
    path('api/book/', views.api_book, name='api_book'),
    # Free Public Calendar Endpoints (iPhone / Android / Outlook / Mac 1-Tap Sync)
    path('booking/<str:ref_id>/calendar.ics', views.download_calendar_ics, name='download_calendar_ics'),
    path('api/calendar/<str:ref_id>.ics', views.download_calendar_ics, name='api_download_calendar_ics'),
]
