from django.contrib import admin
from .models import Category, Product, Promotion

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_status", "featured", "is_active")
    list_filter = ("category", "stock_status", "featured", "is_active")
    search_fields = ("name", "description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("featured", "is_active")

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "discount_display", "currently_valid", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active", "discount_type")
    search_fields = ("name", "products__name")
    filter_horizontal = ("products",)
    list_editable = ("is_active",)

    @admin.display(description="Discount")
    def discount_display(self, promotion):
        suffix = "%" if promotion.discount_type == Promotion.PERCENTAGE else " KSh"
        return f"{promotion.discount_value:g}{suffix}"

    @admin.display(boolean=True, description="Valid now")
    def currently_valid(self, promotion):
        return promotion.is_current
