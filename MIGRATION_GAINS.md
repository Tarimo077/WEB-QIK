# Platform Migration Overview: Transition from WordPress to Custom Django (Qiksearch)

## Executive Summary

Migrating from WordPress / WooCommerce to a tailored Django architecture provides a lightweight, highly maintainable, and secure foundation designed specifically for agricultural e-commerce in Kenya. By shedding plugin bloat, database overhead, and rigid theme layers, this new implementation directly improves page speed, conversion rates, mobile usability, SEO discoverability, and administrative agility.

---

## 1. Performance & Page Speed

| Dimension | Legacy WordPress / WooCommerce | New Custom Django Platform |
| :--- | :--- | :--- |
| **Asset Delivery** | 30+ separate CSS/JS plugin bundles | A single, compiled Tailwind CSS stylesheet with WhiteNoise static compression |
| **Server Latency (TTFB)** | 800ms – 2500ms due to PHP hooks & plugin chains | 50ms – 200ms lightweight WSGI/ASGI Python responses |
| **Client Overhead** | Heavy render-blocking scripts, jQuery, Gutenberg styles | Zero third-party runtime frameworks; lightweight native Vanilla JS |
| **Core Web Vitals** | High Cumulative Layout Shift (CLS) from injected widgets | Zero CLS; pre-sized containers and optimized local asset loading |
| **Listing Pagination** | Clunky full-page reloads losing filters | Instant, lightweight pagination with custom `param_replace` query state preservation |

* **Conversion Impact:** Kenyan mobile shoppers operating on limited data packages or 3G/4G connections receive near-instant page loads.
* **Serverless Compatibility:** The architecture deploys seamlessly to read-only, ephemeral serverless execution environments (e.g., AWS Lambda, Vercel) without persistent disk dependencies.

---

## 2. Superadmin Live Editor & Real-Time Preview Portal

Unlike standard WordPress customizer tools or rigid admin tables, the Django platform includes a dedicated **Superadmin Live Editor & Preview Portal (`/superadmin/live-editor/`)**:

* **Universal Database Entity Editing:** Superadmins can modify Products, Categories, Promotions, and Site Settings (announcements, hero banners, phone numbers, WhatsApp lines, addresses, operating hours) directly from one interface.
* **Dual-Mode Image Management (File Upload & URL):** Supports instant drag-and-drop / file upload (`PNG`, `JPG`, `WEBP`, `GIF`, `SVG`) directly into Django media storage **or** external image URLs, with instant client-side object URL previews before saving.
* **Instant In-Memory Live Preview:** Renders live component previews (**Grid Cards**, **List Cards**, **Product Detail Views**, **Category Headers**, and **Banner Contexts**) debounced in real time as the administrator types, without writing unverified data to the database.
* **Multi-Device Viewport Switching:** One-click preview testing across **Desktop (100%)**, **Tablet (768px)**, and **Mobile (375px)** viewports to ensure presentation quality before publishing.
* **Storefront Quick Launcher:** Authenticated superusers have a direct floating `⚡ Live Editor` shortcut on the storefront for instant edits.
* **Zero-Downtime Content Updates:** The `SiteSetting` model and context processor eliminate code edits and deployments for updating phone numbers, WhatsApp order routing, or homepage campaigns.

---

## 3. Mobile-First Storefront, Filtering & Sorting Engine

* **Advanced Multi-Metric Sorting:** Instant sorting across all listings by **Price (Low to High / High to Low)**, **Name (A to Z / Z to A)**, **Newest Arrivals**, and **Featured / Best Match**.
* **Multi-Faceted Sidebar & Mobile Drawer Filters:**
  - **Category Directory:** Category navigation annotated with real-time product counts.
  - **Price Range Filtering:** Min and max price limits with quick presets (*Under KSh 5k*, *KSh 5k–20k*, *KSh 20k–50k*, *Over KSh 50k*).
  - **Stock Availability:** Filter for *In Stock Only* or *Available on Pre-Order*.
  - **Special Deals & Featured:** 1-click toggles for *On Sale Discounts* and *Featured Equipment*.
  - **Active Removable Chips:** Visual badges showing all currently applied filters with 1-click removal and reset.
  - **Mobile Slide-Out Drawer:** Seamless touch modal for mobile shoppers to filter and sort without losing navigation context.
* **Mobile App-Like Experience:** Integrated slide-out navigation drawer and a fixed bottom navigation bar with real-time cart and wishlist badges.
* **Universal Grid & List View Toggle:** Available across all product listings (**Shop**, **Daily Deals**, and **Wishlist**) allowing users to switch between visual gallery cards and information-dense list cards.
* **User-Selectable Pagination:** Buyers can choose between **10**, **20**, and **50** products per page, with touch-friendly navigation controls, active page pill indicators, and query state preservation.
* **Automatic Discount Percentage Badges:** Dynamically computes and displays `-X%` badges on products with active promotions or reduced comparison prices.
* **Clean Visual Brand Identity:** Pure alpha-transparent logo assets integrated seamlessly without background box artifacts.

---

## 4. Security & Maintenance Overhead

### Eliminate the Plugin Vulnerability Trap
* **No Third-Party Plugin Risk:** WordPress vulnerabilities originate predominantly from third-party plugins. This platform uses native Django modules for session handling, sitemaps, messaging, and search.
* **No Automatic Breaking Updates:** Eliminates unexpected downtime caused by background plugin or theme updates clashing with PHP versions.
* **Built-in Security Defaults:** Django enforces strict CSRF verification, SQL injection protection via parameterized ORM queries, XSS auto-escaping in templates, and strict `X-Frame-Options` headers natively.

---

## 5. Custom E-Commerce & Kenyan Market Localization

### Direct WhatsApp Order Routing
* Unlike generic WooCommerce checkout flows that force multi-step account creation and payment gateways, this platform provides direct, pre-formatted WhatsApp order generation (`https://wa.me/...`).
* Formats item names, quantities, and totals cleanly, fitting standard buying behavior across Kenyan agricultural and livestock sectors.

### Interactive In-Shop Experience
* **Instant Typeahead Search:** Debounced auto-complete endpoint (`/api/search-suggestions/`) querying active products with zero page refreshes.
* **Modern Toast System:** Real-time top-right notifications for cart updates and wishlist saves without full-page reloads.
* **Tailored Currency & Stock Displays:** Native `django.contrib.humanize` formatting for clean Kenyan Shilling (`KSh`) representations.

---

## 6. Search Engine Optimization (SEO) & Google Shopping

* **Automated Product Schema (`JSON-LD`):** Every product page renders `schema.org/Product` metadata out of the box, including currency (`KES`), price, availability, and SKU.
* **Live Google Merchant Feed:** Built-in XML endpoint (`/google-shopping-feed.xml`) directly generates compliant feeds for Google Shopping campaigns without requiring paid extensions.
* **Dynamic Sitemaps & Robots.txt:** Integrated `django.contrib.sitemaps` dynamically indexes active categories, products, and static landing pages as the catalog evolves.

---

## 7. Architectural Scalability & Infrastructure Cost

* **Stateless Client Sessions:** Support for cryptographically signed cookie sessions (`SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"`) eliminates database writes during browsing, cart modification, and wishlist actions.
* **Lower Compute Requirements:** Serves significantly more concurrent users on entry-level hosting or serverless tiers compared to heavy PHP/MySQL stacks.
* **Data Ownership & Clean Schema:** Direct control over relational tables (`Category`, `Product`, `Promotion`, `SiteSetting`) without serialized meta-tables (`wp_postmeta`, `wp_options`) slowing down lookups.