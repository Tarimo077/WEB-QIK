from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from catalog.sitemaps import CategorySitemap, ProductSitemap, StaticViewSitemap
from catalog import views

sitemaps = {"products": ProductSitemap, "categories": CategorySitemap, "pages": StaticViewSitemap}
urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps, "template_name": "sitemap.xml"}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("google-shopping-feed.xml", views.google_shopping_feed, name="google_shopping_feed"),
    path("", include("catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
