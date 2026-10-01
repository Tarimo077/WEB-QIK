from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category, Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    def items(self): return Product.objects.filter(is_active=True)
    def lastmod(self, obj): return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"
    def items(self): return ["home", "shop", "categories", "deals", "about", "contact", "terms", "returns", "faqs", "track_order"]
    def location(self, item): return reverse(item)

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    def items(self): return Category.objects.filter(products__is_active=True).distinct()
