from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views, editor_views
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

    # Superadmin Live Editor & Preview Portal
    path("superadmin/live-editor/", editor_views.live_editor_dashboard, name="live_editor"),
    path("superadmin/live-editor/api/entity/", editor_views.api_get_entity, name="live_editor_api_entity"),
    path("superadmin/live-editor/api/preview/", editor_views.api_preview_entity, name="live_editor_api_preview"),
    path("superadmin/live-editor/api/save/", editor_views.api_save_entity, name="live_editor_api_save"),
    path("superadmin/live-editor/api/toggle/", editor_views.api_toggle_field, name="live_editor_api_toggle"),

    # SEO & Google Shopping endpoints
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("google-shopping-feed.xml", views.google_shopping_feed, name="google_shopping_feed"),
]