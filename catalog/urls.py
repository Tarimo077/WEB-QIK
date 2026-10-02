from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("about/", views.about, name="about"),
    path("categories/", views.categories, name="categories"),
    path("deals/", views.deals, name="deals"),
    path("cart/", views.cart, name="cart"),
    path("cart/<int:product_id>/", views.cart_action, name="cart_action"),
    path("contact/", views.contact, name="contact"),
    path("terms-and-conditions/", views.terms, name="terms"),
    path("refund-and-returns/", views.returns, name="returns"),
    path("faqs/", views.faqs, name="faqs"),
    path("track-order/", views.track_order, name="track_order"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/<int:product_id>/", views.wishlist_action, name="wishlist_action"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="product"),
    path("api/search-suggestions/", views.search_suggestions, name="search_suggestions"),
    path("platform-gains/", views.migration_gains, name="migration_gains"),

    # SEO & Google Shopping endpoints
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("google-shopping-feed.xml", views.google_shopping_feed, name="google_shopping_feed"),
]