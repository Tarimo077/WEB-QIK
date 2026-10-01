from django.urls import path
from . import views

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
]
