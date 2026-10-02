# Qiksearch Farm Shop

A high-performance, responsive Django storefront and e-commerce platform built for Qiksearch Kenya agricultural equipment, machinery, seeds, and farm supplies.

## Key Features & Functionalities

### 1. Storefront & Catalog Experience
- **Responsive Mobile-First UI**: Fully optimized for mobile screens, tablets, and desktop displays with a slide-out navigation drawer, sticky search header, and a fixed bottom app bar with real-time cart and wishlist counter badges.
- **Advanced Sorting Engine**: Sort products by **Price: Low to High**, **Price: High to Low**, **Name: A to Z**, **Name: Z to A**, **Newest Arrivals**, or **Featured / Best Match** across all listing pages.
- **Multi-Faceted Filtering Suite**:
  - **Category Filter**: Live annotated category directory with real-time product counts.
  - **Price Range Filter**: Custom minimum and maximum price inputs along with quick preset bounds (Under KSh 5,000, KSh 5k–20k, KSh 20k–50k, Over KSh 50,000).
  - **Stock Availability**: Filter by *In Stock Only*, *Available on Pre-Order*, or *All*.
  - **Deals & Highlights**: 1-click toggles for *On Sale Discounts* and *Featured Products*.
  - **Active Filter Chips**: Removable filter tags with 1-click chip removal and instant "Clear all" reset.
  - **Mobile Slide-Out Drawer**: Dedicated mobile filter drawer for effortless touch-friendly filtering.
- **User-Selectable Pagination**: Dynamic pagination with selectable page size options (**10**, **20**, and **50** items per page) and modern page controls (elided page numbers, previous/next buttons, results range count).
- **Universal Grid & List View Toggle**: Seamlessly switch between Grid (`▦`) and List (`☷`) product views across all listing pages (Main Shop, Category listings, Daily Deals, and Wishlist).
- **Smart Query Parameter Preservation**: Custom template tags (`param_replace`, `param_remove`) preserve active search keywords, category filters, price bounds, sorting, page size, and view modes during navigation.
- **Instant Search & Autocomplete**: Debounced typeahead search suggestions endpoint (`/api/search-suggestions/`) with instant product dropdowns.
- **Dynamic Discount Badges**: Automatic `-X%` percentage savings badges on products with active promotions or reduced comparison prices.
- **1-Click WhatsApp Ordering**: Pre-formatted cart order routing directly to Qiksearch WhatsApp support (`+254 700 007 552`), fitting Kenyan agricultural purchasing workflows.
- **Session-Based Cart & Wishlist**: Fast, client-side signed cookie sessions with real-time top-right toast alerts for additions and quantity updates.

### 2. Superadmin Live Editor & Real-Time Preview Portal
- **Dedicated Live Editor Dashboard (`/superadmin/live-editor/`)**: In-place management for all database entities with immediate visual feedback.
  - **Products**: Title, slug, category, price, old price, stock status (InStock, PreOrder, OutOfStock), promotional badge, SKU, dual image management (file upload vs image URL), and active visibility.
  - **Categories**: Name, slug, icon emoji, and descriptions.
  - **Promotions**: Promotional name, badge text, discount type (Percentage vs Fixed KSh), discount value, date ranges, and active toggle.
  - **Site Content & Settings**: Top announcement bar text, homepage hero title/subtitle, support phone numbers, WhatsApp lines, email, address, operating hours, and mission statement.
- **Dual-Mode Image Upload & URL Support**:
  - Direct file upload with drag-and-drop or file picker (`PNG`, `JPG`, `WEBP`, `GIF`, `SVG`) saved to Django media storage.
  - Direct external Image URL input for CDN and manufacturer imagery.
  - Instant client-side object URL rendering for immediate live preview before saving.
  - Current image preview status card with 1-click "Remove Image" action.
- **Real-Time Interactive Preview**: Dual-pane layout that re-renders live component previews (Grid Card, List Card, Product Detail layout, Category header, Component preview) as you type, before committing changes to the database.
- **Multi-Device Viewport Switching**: Toggle preview canvas between Desktop (100%), Tablet (768px), and Mobile (375px) device viewports.
- **Superadmin Storefront Integration**: Floating `⚡ Live Editor` quick launcher and navbar shortcuts for authenticated superusers.

### 3. Search Visibility & SEO
- **Structured Data (JSON-LD)**: Schema.org `Product`, `Offer`, `Organization`, and `BreadcrumbList` metadata on all product and landing pages.
- **Google Shopping Merchant Feed**: Live XML endpoint (`/google-shopping-feed.xml`) publishing active pictured products with prices, SKU, availability, and currency (`KES`).
- **Dynamic Sitemaps & Robots**: Automated `sitemap.xml` for active categories, products, and static routes with canonical URL enforcement.

---

## Local Development Setup

```powershell
# 1. Create and activate virtual environment
python -m venv qikvenv
.\qikvenv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install -r requirements.txt
npm install

# 3. Build Tailwind CSS
npm run css:build

# 4. Run database migrations & seed settings
python manage.py migrate

# 5. Create superuser & start server
python manage.py createsuperuser
python manage.py runserver
```

* Visit `http://127.0.0.1:8000/` for the storefront.
* Visit `http://127.0.0.1:8000/superadmin/live-editor/` for the Superadmin Live Editor & Preview Portal.
* Visit `http://127.0.0.1:8000/admin/` for standard Django Admin.

---

## Production Deployment

1. Set environment variables:
   * `DJANGO_SECRET_KEY`: Secure random key
   * `DJANGO_DEBUG=0`
   * `DJANGO_ALLOWED_HOSTS`: Domain names (e.g. `qiksearch.co.ke,www.qiksearch.co.ke`)
2. Run `python manage.py collectstatic --noinput` to generate fingerprinted WhiteNoise static bundles.
3. Configure PostgreSQL / production database and persistent media storage if user uploads are used.
4. Enable SSL/HTTPS headers: `DJANGO_SECURE_SSL_REDIRECT=1`, `DJANGO_TRUST_X_FORWARDED_PROTO=1`.
