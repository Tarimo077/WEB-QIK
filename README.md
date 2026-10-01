# Qiksearch Farm Shop

A responsive Django storefront inspired by Qiksearch's Kenyan agricultural shop.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm install
npm run css:build
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

Tailwind CSS v4 and DaisyUI 5 are used in the Django templates. Use Tailwind's standard color palette, text sizes, and spacing utilities in template classes. Edit `assets/css/app.css` to configure Tailwind and the DaisyUI `qik` theme, then rebuild `static/catalog/tailwind.css` with `npm run css:build`. During development, use `npm run css:watch` in a separate terminal so template utility classes are picked up as you work. The hero background, Qiksearch logo and web fonts are stored locally in `static/catalog`; product photos are served from Django media uploads. The generated stylesheet and fonts are loaded from local static files; no runtime CDN or `site.css` is used.

Visit `http://127.0.0.1:8000/` for the storefront and `/admin/` to manage products and categories. Product photos can be uploaded in admin, or an external image URL can be set on each product. The seed data is starter catalog content based on publicly listed Qiksearch product examples; review prices, descriptions, availability, and photos before launch.

## Production

Set `DJANGO_SECRET_KEY` to a private random value, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS` to the deployed hostnames. Configure HTTPS, a production database, persistent media storage, and a WSGI/ASGI server before deployment. WhiteNoise serves compressed, fingerprinted static files; run `python manage.py collectstatic` during each release. Set `DJANGO_SECURE_SSL_REDIRECT=1` after HTTPS is active, `DJANGO_TRUST_X_FORWARDED_PROTO=1` only behind a trusted proxy that sets `X-Forwarded-Proto`, and optionally set `DJANGO_SECURE_HSTS_SECONDS` after verifying HTTPS across the host. Create a superuser. Do not deploy with the development secret or SQLite as the production database.

## Search visibility

Product pages include canonical URLs, unique titles and descriptions, Open Graph metadata, and Schema.org `Product`/`Offer` JSON-LD. The site also publishes organization and website details, a catalog sitemap, and crawl instructions. Product search results are excluded from indexing to avoid thin duplicate URLs, while category, product, and informational pages remain discoverable. `/google-shopping-feed.xml` publishes active products with images, prices, and stock for Google Merchant Center. After deployment on the final domain, verify the site in Google Search Console, submit the sitemap, add the feed in Merchant Center, and check product URLs with Google's Rich Results Test. Accurate prices, stock, photos, and shipping/returns details matter for product listings. Structured data can make pages eligible for enhanced results but cannot guarantee rankings, indexing, or AI recommendations. Ranking depends on the quality and usefulness of the content, competition, authority, and user needs.

## Catalog and promotions

Use a Django superuser at `/admin/` to manage the storefront. Add categories and products there; product photos are uploaded on each product (or set an image URL). Products can be edited, deleted, featured, or deactivated from the Product list. Create a Promotion, select its products, choose a percentage or fixed KSh reduction, optionally set start/end dates, and switch `Active` on to publish it. Promotions show their badge and discounted price only while active and within their date window. The database catalog is authoritative; no seed catalog runs on startup.

## Storefront

The storefront includes a category directory, daily deals, grid/list product views, session-based cart and wishlist, FAQs, contact, order-help, returns, and terms pages. Cart orders are handed off to Qiksearch through WhatsApp so their team can confirm availability, delivery, and payment with the customer.
