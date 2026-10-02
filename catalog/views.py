from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import json
import xml.etree.ElementTree as ET
from django.utils.html import strip_tags
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from urllib.parse import quote
from .models import Category, Product
from django.contrib import messages

def home(request):
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("promotions")
    deals = [product for product in products if product.active_promo()][:4]
    return render(request, "catalog/home.html", {"products": products, "categories": Category.objects.all(), "deals": deals})

def shop(request):
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("promotions")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    view_mode = request.GET.get("view", "grid")
    if view_mode not in ("grid", "list"):
        view_mode = "grid"
    return render(request, "catalog/shop.html", {"products": products, "categories": Category.objects.all(), "query": query, "selected_category": category, "view_mode": view_mode})

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.filter(is_active=True).select_related("category").prefetch_related("promotions"), slug=slug)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk).prefetch_related("promotions")[:4]
    promo = product.active_promo()
    if promo:
        product.promo_price = promo.discounted_price_for(product.price)
    availability = {
        "InStock": "https://schema.org/InStock",
        "PreOrder": "https://schema.org/PreOrder",
        "OutOfStock": "https://schema.org/OutOfStock",
    }.get(product.stock_status, "https://schema.org/OutOfStock")
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": strip_tags(product.description),
        "image": [request.build_absolute_uri(product.display_image)] if product.display_image else [],
        "sku": product.sku or product.slug,
        "category": product.category.name,
        "offers": {
            "@type": "Offer",
            "url": request.build_absolute_uri(product.get_absolute_url()),
            "priceCurrency": "KES",
            "price": str(product.current_price),
            "availability": availability,
            "itemCondition": "https://schema.org/NewCondition",
        },
    }
    structured_data = mark_safe(json.dumps(product_schema, ensure_ascii=False).replace("<", "\\u003c"))
    return render(request, "catalog/product.html", {
        "product": product,
        "related": related,
        "structured_data": structured_data,
        "absolute_product_image": request.build_absolute_uri(product.display_image) if product.display_image else "",
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).prefetch_related("promotions")
    view_mode = request.GET.get("view", "grid")
    if view_mode not in ("grid", "list"):
        view_mode = "grid"
    return render(request, "catalog/shop.html", {"products": products, "categories": Category.objects.all(), "active_category": category, "view_mode": view_mode})

def about(request): 
    return render(request, "catalog/about.html")

def categories(request):
    products_with_images = Product.objects.filter(is_active=True).exclude(image="", image_url="").order_by("name")
    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__is_active=True), distinct=True)
    ).prefetch_related(
        Prefetch("products", queryset=products_with_images, to_attr="collage_products")
    )
    return render(request, "catalog/categories.html", {"categories": categories})

def deals(request):
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("promotions")
    products = [product for product in products if product.active_promo()]
    return render(request, "catalog/deals.html", {"products": products})

def cart(request):
    cart_data = request.session.get("cart", {})
    products = Product.objects.filter(pk__in=cart_data, is_active=True).select_related("category").prefetch_related("promotions")
    items = []
    total = 0
    message_lines = ["Hello Qiksearch, I would like to order:"]
    for product in products:
        quantity = max(1, int(cart_data.get(str(product.pk), 1)))
        line_total = product.current_price * quantity
        total += line_total
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        message_lines.append(f"{quantity} x {product.name} — KSh {line_total:,.0f}")
    message_lines.append(f"Total: KSh {total:,.0f}")
    return render(request, "catalog/cart.html", {"items": items, "total": total, "whatsapp_url": "https://wa.me/254700007552?text=" + quote("\n".join(message_lines))})

def cart_action(request, product_id):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart_data = request.session.get("cart", {})
    key = str(product.pk)
    action = request.POST.get("action", "add")
    toast_msg = ""
    toast_type = "success"

    if action == "remove":
        cart_data.pop(key, None)
        toast_msg = f'"{product.name}" removed from your cart.'
        toast_type = "warning"
        messages.warning(request, toast_msg)
    elif action == "set":
        try:
            quantity = min(99, max(0, int(request.POST.get("quantity", 1))))
        except (TypeError, ValueError):
            quantity = 1

        if quantity == 0:
            cart_data.pop(key, None)
            toast_msg = f'"{product.name}" removed from your cart.'
            toast_type = "warning"
            messages.warning(request, toast_msg)
        else:
            cart_data[key] = quantity
            toast_msg = f'Quantity updated for "{product.name}".'
            toast_type = "info"
            messages.info(request, toast_msg)
    else:
        cart_data[key] = min(99, int(cart_data.get(key, 0)) + 1)
        toast_msg = f'"{product.name}" added to your cart!'
        toast_type = "success"
        messages.success(request, toast_msg)

    request.session["cart"] = cart_data
    request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": toast_msg,
            "type": toast_type,
            "cart_count": sum(cart_data.values()),
        })

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = reverse("cart")
    return redirect(next_url)

def contact(request): 
    return render(request, "catalog/contact.html")

def terms(request): 
    return render(request, "catalog/terms.html")

def returns(request): 
    return render(request, "catalog/returns.html")

def faqs(request): 
    return render(request, "catalog/faqs.html")

def track_order(request): 
    return render(request, "catalog/track_order.html")

def wishlist(request):
    saved = request.session.get("wishlist", [])
    products = Product.objects.filter(pk__in=saved, is_active=True).select_related("category").prefetch_related("promotions")
    return render(request, "catalog/wishlist.html", {"products": products})

def wishlist_action(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        saved = request.session.get("wishlist", [])
        str_id = str(product_id)
        if str_id in saved:
            saved.remove(str_id)
            added = False
            toast_msg = f'"{product.name}" removed from your wishlist.'
            toast_type = "info"
            messages.info(request, toast_msg)
        else:
            saved.append(str_id)
            added = True
            toast_msg = f'"{product.name}" added to your wishlist!'
            toast_type = "success"
            messages.success(request, toast_msg)

        request.session["wishlist"] = saved
        request.session.modified = True

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "added": added,
                "message": toast_msg,
                "type": toast_type,
                "wishlist_count": len(saved),
            })

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = reverse("wishlist")
    return redirect(next_url)

def robots(request):
    origin = request.build_absolute_uri("/").rstrip("/")
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /?q=\nSitemap: {origin}/sitemap.xml\n", content_type="text/plain")

def google_shopping_feed(request):
    """Live Google Merchant Center RSS feed built from active, pictured products."""
    rss = ET.Element("rss", {"version": "2.0", "xmlns:g": "http://base.google.com/ns/1.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Qiksearch Kenya Product Catalog"
    ET.SubElement(channel, "link").text = request.build_absolute_uri("/")
    ET.SubElement(channel, "description").text = "Farm equipment and agricultural supplies from Qiksearch Kenya."
    products = Product.objects.filter(is_active=True).exclude(image="", image_url="").select_related("category").prefetch_related("promotions")
    for product in products:
        image = product.display_image
        if not image:
            continue
        item = ET.SubElement(channel, "item")
        fields = {
            "id": product.sku or str(product.pk),
            "title": product.name,
            "description": strip_tags(product.description),
            "link": request.build_absolute_uri(product.get_absolute_url()),
            "image_link": request.build_absolute_uri(image),
            "availability": {
                "InStock": "in stock",
                "PreOrder": "preorder",
                "OutOfStock": "out of stock",
            }.get(product.stock_status, "out of stock"),
            "price": f"{product.current_price} KES",
            "condition": "new",
        }
        for key, value in fields.items():
            ET.SubElement(item, f"{{http://base.google.com/ns/1.0}}{key}").text = str(value)
    body = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
    return HttpResponse(body, content_type="application/rss+xml; charset=utf-8")

def search_suggestions(request):
    """
    Returns instant search suggestion results matching the query `q`.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if len(query) >= 2:
        products = Product.objects.filter(
            Q(is_active=True) & (
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        ).distinct()[:6]

        for product in products:
            image_url = product.image.url if getattr(product, 'image', None) else ''
            results.append({
                'name': product.name,
                'url': f'/product/{product.slug}/',
                'price': f'{product.price:,.2f}' if getattr(product, 'price', None) else '',
                'image': image_url,
            })

    return JsonResponse({'results': results})

def migration_gains(request):
    return render(request, "catalog/migration_gains.html")