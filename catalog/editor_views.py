from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import json
from decimal import Decimal
from .models import Category, Product, Promotion, SiteSetting

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superadmin, login_url="/admin/login/?next=/superadmin/live-editor/")
def live_editor_dashboard(request):
    """
    Main Live Editor & Preview dashboard for superadmin.
    """
    products = Product.objects.select_related("category").prefetch_related("promotions").order_by("-updated_at")
    products_with_images = Product.objects.filter(is_active=True).exclude(image="", image_url="").order_by("name")
    from django.db.models import Prefetch
    categories = Category.objects.prefetch_related(
        Prefetch("products", queryset=products_with_images, to_attr="collage_products")
    ).order_by("name")
    promotions = Promotion.objects.all().order_by("-created_at")
    settings_qs = SiteSetting.objects.all().order_by("group", "label")

    # Group settings by group
    grouped_settings = {}
    for s in settings_qs:
        grouped_settings.setdefault(s.group, []).append(s)

    stats = {
        "total_products": products.count(),
        "active_products": products.filter(is_active=True).count(),
        "featured_products": products.filter(featured=True).count(),
        "total_categories": categories.count(),
        "total_promotions": promotions.count(),
        "active_promotions": promotions.filter(is_active=True).count(),
        "total_settings": settings_qs.count(),
    }

    initial_type = request.GET.get("type", "product")
    initial_id = request.GET.get("id", "")

    return render(request, "catalog/admin_live_editor.html", {
        "products": products,
        "categories": categories,
        "promotions": promotions,
        "grouped_settings": grouped_settings,
        "settings_list": settings_qs,
        "stats": stats,
        "initial_type": initial_type,
        "initial_id": initial_id,
        "stock_choices": [
            ("InStock", "In stock"),
            ("PreOrder", "Available to order / PreOrder"),
            ("OutOfStock", "Out of stock"),
        ],
        "discount_type_choices": Promotion.DISCOUNT_TYPES,
        "setting_field_types": SiteSetting.FIELD_TYPES,
    })

@require_http_methods(["GET"])
def api_get_entity(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden("Unauthorized")

    entity_type = request.GET.get("type", "product")
    entity_id = request.GET.get("id")

    if not entity_id:
        return JsonResponse({"error": "Missing entity id"}, status=400)

    try:
        if entity_type == "product":
            p = get_object_or_404(Product.objects.select_related("category"), pk=entity_id)
            data = {
                "id": p.pk,
                "name": p.name,
                "slug": p.slug,
                "category_id": p.category_id,
                "category_name": p.category.name if p.category else "",
                "price": p.price,
                "old_price": p.old_price or "",
                "description": p.description,
                "badge": p.badge,
                "stock_status": p.stock_status,
                "featured": p.featured,
                "is_active": p.is_active,
                "image_url": p.image_url,
                "display_image": p.display_image,
                "has_uploaded_image": bool(p.image),
                "image_filename": p.image.name.split("/")[-1] if p.image else "",
                "sku": p.sku,
                "current_price": p.current_price,
                "discount_percent": p.discount_percent,
                "absolute_url": p.get_absolute_url(),
                "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
        elif entity_type == "category":
            c = get_object_or_404(Category, pk=entity_id)
            collage_images = [p.display_image for p in c.products.filter(is_active=True) if p.display_image][:4]
            data = {
                "id": c.pk,
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "products_count": c.products.count(),
                "collage_images": collage_images,
                "absolute_url": c.get_absolute_url(),
            }
        elif entity_type == "promotion":
            promo = get_object_or_404(Promotion, pk=entity_id)
            data = {
                "id": promo.pk,
                "name": promo.name,
                "badge_text": promo.badge_text,
                "discount_type": promo.discount_type,
                "discount_value": str(promo.discount_value),
                "is_active": promo.is_active,
                "starts_at": promo.starts_at.strftime("%Y-%m-%dT%H:%M") if promo.starts_at else "",
                "ends_at": promo.ends_at.strftime("%Y-%m-%dT%H:%M") if promo.ends_at else "",
                "product_ids": list(promo.products.values_list("pk", flat=True)),
            }
        elif entity_type == "setting":
            s = get_object_or_404(SiteSetting, pk=entity_id)
            data = {
                "id": s.pk,
                "key": s.key,
                "label": s.label,
                "group": s.group,
                "value": s.value,
                "field_type": s.field_type,
                "help_text": s.help_text,
                "updated_at": s.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
        else:
            return JsonResponse({"error": "Unknown entity type"}, status=400)

        return JsonResponse({"success": True, "entity": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
def api_preview_entity(request):
    """
    Renders live HTML previews without committing changes to DB.
    Supports both JSON and Multipart FormData.
    """
    if not is_superadmin(request.user):
        return HttpResponseForbidden("Unauthorized")

    if request.content_type and "application/json" in request.content_type:
        try:
            body = json.loads(request.body.decode("utf-8"))
            entity_type = body.get("type", "product")
            fields = body.get("fields", {})
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        entity_type = request.POST.get("type", "product")
        fields = request.POST.dict()

    try:
        if entity_type == "product":
            category = None
            if fields.get("category_id"):
                category = Category.objects.filter(pk=fields.get("category_id")).first()
            if not category:
                category = Category(name="Farm Machinery", slug="farm-machinery")

            price = int(fields.get("price") or 0)
            old_price = int(fields.get("old_price")) if fields.get("old_price") else None
            
            # Preview image URL can be passed via image_preview_url or image_url
            preview_img = fields.get("image_preview_url") or fields.get("image_url") or ""

            prod = Product(
                pk=fields.get("id") or 99999,
                name=fields.get("name") or "Sample Product Name",
                slug=fields.get("slug") or "sample-product",
                category=category,
                price=price,
                old_price=old_price,
                description=fields.get("description") or "High quality agricultural equipment and supplies.",
                badge=fields.get("badge", ""),
                stock_status=fields.get("stock_status", "InStock"),
                featured=str(fields.get("featured", "")).lower() in ("true", "1", "on"),
                is_active=str(fields.get("is_active", "true")).lower() in ("true", "1", "on"),
                image_url=preview_img,
                sku=fields.get("sku", ""),
            )

            grid_card_html = render_to_string("catalog/_product_card.html", {
                "product": prod,
                "view_mode": "grid",
                "request": request,
            })

            list_card_html = render_to_string("catalog/_product_card.html", {
                "product": prod,
                "view_mode": "list",
                "request": request,
            })

            # Mini detail preview
            detail_html = render_to_string("catalog/_live_preview_product_detail.html", {
                "product": prod,
                "request": request,
            })

            return JsonResponse({
                "success": True,
                "previews": {
                    "grid_card": grid_card_html,
                    "list_card": list_card_html,
                    "detail": detail_html,
                },
                "meta": {
                    "current_price": prod.current_price,
                    "discount_percent": prod.discount_percent,
                    "stock_status": prod.stock_status,
                }
            })

        elif entity_type == "category":
            cat_id = fields.get("id")
            collage_products = []
            if cat_id:
                existing_cat = Category.objects.filter(pk=cat_id).first()
                if existing_cat:
                    collage_products = list(existing_cat.products.filter(is_active=True).exclude(image="", image_url="")[:4])

            cat = Category(
                pk=cat_id or 99999,
                name=fields.get("name") or "Sample Category",
                slug=fields.get("slug") or "sample-category",
                description=fields.get("description") or "Category description",
            )
            cat.collage_products = collage_products
            cat.product_count = len(collage_products)

            banner_html = render_to_string("catalog/_live_preview_category.html", {
                "category": cat,
                "collage_products": collage_products,
                "request": request,
            })
            return JsonResponse({
                "success": True,
                "previews": {
                    "banner": banner_html,
                }
            })

        elif entity_type == "setting":
            setting = SiteSetting(
                key=fields.get("key", "announcement_text"),
                label=fields.get("label", "Setting"),
                group=fields.get("group", "General"),
                value=fields.get("value", ""),
                field_type=fields.get("field_type", "text"),
            )
            preview_html = render_to_string("catalog/_live_preview_setting.html", {
                "setting": setting,
                "request": request,
            })
            return JsonResponse({
                "success": True,
                "previews": {
                    "component": preview_html,
                }
            })

        return JsonResponse({"error": "Unsupported preview type"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
def api_save_entity(request):
    """
    Saves entity changes to database.
    Accepts both JSON and Multipart FormData with file upload support.
    """
    if not is_superadmin(request.user):
        return HttpResponseForbidden("Unauthorized")

    is_json = request.content_type and "application/json" in request.content_type
    if is_json:
        try:
            body = json.loads(request.body.decode("utf-8"))
            entity_type = body.get("type", "product")
            fields = body.get("fields", {})
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        entity_type = request.POST.get("type", "product")
        fields = request.POST.dict()

    entity_id = fields.get("id")

    try:
        if entity_type == "product":
            category = get_object_or_404(Category, pk=fields.get("category_id"))
            if entity_id:
                p = get_object_or_404(Product, pk=entity_id)
            else:
                p = Product()

            p.name = fields.get("name", "").strip()
            if fields.get("slug"):
                p.slug = fields.get("slug", "").strip()
            p.category = category
            p.price = int(fields.get("price") or 0)
            p.old_price = int(fields.get("old_price")) if fields.get("old_price") else None
            p.description = fields.get("description", "")
            p.badge = fields.get("badge", "").strip()
            p.stock_status = fields.get("stock_status", "InStock")
            p.featured = str(fields.get("featured", "")).lower() in ("true", "1", "on")
            p.is_active = str(fields.get("is_active", "true")).lower() in ("true", "1", "on")
            p.sku = fields.get("sku", "").strip()

            # Handle Image Upload, URL, and Clear Image options
            clear_image = str(fields.get("clear_image", "")).lower() in ("true", "1", "yes")
            image_mode = fields.get("image_mode", "url")

            if clear_image:
                if p.image:
                    p.image.delete(save=False)
                p.image = None
                p.image_url = ""
            else:
                if "image_file" in request.FILES:
                    p.image = request.FILES["image_file"]
                elif image_mode == "url" or fields.get("image_url"):
                    new_url = fields.get("image_url", "").strip()
                    p.image_url = new_url
                    if new_url and p.image and not request.FILES.get("image_file"):
                        # Clear old uploaded file if user explicitly switched to a new external URL
                        p.image.delete(save=False)
                        p.image = None

            p.full_clean()
            p.save()

            return JsonResponse({
                "success": True,
                "message": f'Product "{p.name}" saved successfully in database.',
                "id": p.pk,
                "name": p.name,
                "display_image": p.display_image,
                "image_url": p.image_url,
                "has_uploaded_image": bool(p.image),
                "image_filename": p.image.name.split("/")[-1] if p.image else "",
                "view_url": p.get_absolute_url(),
            })

        elif entity_type == "category":
            if entity_id:
                c = get_object_or_404(Category, pk=entity_id)
                # Existing category: slug is locked and immutable in Live Editor to preserve URLs and SEO
            else:
                c = Category()
            c.name = fields.get("name", "").strip()
            c.description = fields.get("description", "").strip()
            c.icon = fields.get("icon", "🌱").strip()
            c.full_clean()
            c.save()

            return JsonResponse({
                "success": True,
                "message": f'Category "{c.name}" saved successfully.',
                "id": c.pk,
                "name": c.name,
                "slug": c.slug,
                "view_url": c.get_absolute_url(),
            })

        elif entity_type == "promotion":
            if entity_id:
                promo = get_object_or_404(Promotion, pk=entity_id)
            else:
                promo = Promotion()
            promo.name = fields.get("name", "").strip()
            promo.badge_text = fields.get("badge_text", "Sale").strip()
            promo.discount_type = fields.get("discount_type", "percentage")
            promo.discount_value = Decimal(str(fields.get("discount_value", "10")))
            promo.is_active = str(fields.get("is_active", "")).lower() in ("true", "1", "on")
            promo.full_clean()
            promo.save()

            product_ids = fields.get("product_ids", [])
            if isinstance(product_ids, str):
                product_ids = [int(x.strip()) for x in product_ids.split(",") if x.strip().isdigit()]
            elif not isinstance(product_ids, list):
                product_ids = []
            promo.products.set(product_ids)

            return JsonResponse({
                "success": True,
                "message": f'Promotion "{promo.name}" saved successfully.',
                "id": promo.pk,
                "name": promo.name,
            })

        elif entity_type == "setting":
            key = fields.get("key", "").strip()
            if entity_id:
                s = get_object_or_404(SiteSetting, pk=entity_id)
            elif key:
                s = SiteSetting.objects.filter(key=key).first() or SiteSetting(key=key)
            else:
                return JsonResponse({"error": "Setting key is required"}, status=400)

            s.label = fields.get("label", s.label or key).strip()
            s.group = fields.get("group", s.group or "General").strip()
            s.value = fields.get("value", "")
            s.field_type = fields.get("field_type", s.field_type or "text")
            s.help_text = fields.get("help_text", s.help_text or "").strip()
            s.full_clean()
            s.save()

            return JsonResponse({
                "success": True,
                "message": f'Site setting "{s.label}" updated in database.',
                "id": s.pk,
                "name": s.label,
            })

        return JsonResponse({"error": "Unknown entity type"}, status=400)
    except ValidationError as ve:
        return JsonResponse({"error": f"Validation error: {ve.message_dict if hasattr(ve, 'message_dict') else ve}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["POST"])
def api_toggle_field(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden("Unauthorized")

    try:
        body = json.loads(request.body.decode("utf-8"))
        entity_type = body.get("type", "product")
        entity_id = body.get("id")
        field_name = body.get("field")

        if entity_type == "product":
            p = get_object_or_404(Product, pk=entity_id)
            if field_name == "is_active":
                p.is_active = not p.is_active
                p.save(update_fields=["is_active"])
                return JsonResponse({"success": True, "value": p.is_active, "name": p.name})
            elif field_name == "featured":
                p.featured = not p.featured
                p.save(update_fields=["featured"])
                return JsonResponse({"success": True, "value": p.featured, "name": p.name})

        elif entity_type == "promotion":
            promo = get_object_or_404(Promotion, pk=entity_id)
            if field_name == "is_active":
                promo.is_active = not promo.is_active
                promo.save(update_fields=["is_active"])
                return JsonResponse({"success": True, "value": promo.is_active, "name": promo.name})

        return JsonResponse({"error": "Invalid toggle request"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
