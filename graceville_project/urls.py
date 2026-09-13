from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Customize Django Admin Header
admin.site.site_header = "Grace Ville Administration"
admin.site.site_title = "Grace Ville Admin Portal"
admin.site.index_title = "Welcome to Grace Ville Management"

def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin/
Sitemap: https://graceville.vercel.app/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://graceville.vercel.app/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://graceville.vercel.app/spaces/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://graceville.vercel.app/space-details/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://graceville.vercel.app/contact/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return HttpResponse(content, content_type="application/xml")

from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('favicon.ico', RedirectView.as_view(url='/static/assets/images/favicon.ico', permanent=True)),
    path('', include('villa.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'villa.views.custom_404_view'
