from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=240, blank=True)
    icon = models.CharField(max_length=8, default="🌱")
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            suffix = 2
            while Category.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("category", kwargs={"slug": self.slug})

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Price in Kenyan shillings")
    old_price = models.PositiveIntegerField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    badge = models.CharField(max_length=30, blank=True)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Turn off to hide this product from the storefront.")
    stock_status = models.CharField(max_length=24, default="InStock", choices=[("InStock", "In stock"), ("PreOrder", "Available to order"), ("OutOfStock", "Out of stock")])
    sku = models.CharField(max_length=40, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-featured", "name"]
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            suffix = 2
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("product", kwargs={"slug": self.slug})
    @property
    def display_image(self):
        if self.image: return self.image.url
        return self.image_url or ""

    def active_promo(self):
        promos = getattr(self, "_prefetched_objects_cache", {}).get("promotions")
        if promos is None:
            promos = self.promotions.all()
        return next((promo for promo in promos if promo.is_current), None)

    @property
    def current_price(self):
        promo = self.active_promo()
        return promo.discounted_price_for(self.price) if promo else self.price

    @property
    def structured_price(self):
        """Unformatted price string for machine-readable Product JSON-LD."""
        return format(self.current_price, "f")


class Promotion(models.Model):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    DISCOUNT_TYPES = [(PERCENTAGE, "Percentage"), (FIXED, "Fixed amount (KSh)")]
    name = models.CharField(max_length=120)
    products = models.ManyToManyField(Product, related_name="promotions", blank=True)
    discount_type = models.CharField(max_length=12, choices=DISCOUNT_TYPES, default=PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    badge_text = models.CharField(max_length=30, default="Sale")
    is_active = models.BooleanField(default=False, help_text="Only active and in-date promotions appear on the storefront.")
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_current(self):
        now = timezone.now()
        return self.is_active and (not self.starts_at or self.starts_at <= now) and (not self.ends_at or self.ends_at >= now)

    def discounted_price_for(self, price):
        price = Decimal(price)
        amount = price * self.discount_value / Decimal("100") if self.discount_type == self.PERCENTAGE else self.discount_value
        return max(Decimal("0"), price - min(price, amount))

    def __str__(self):
        return self.name
