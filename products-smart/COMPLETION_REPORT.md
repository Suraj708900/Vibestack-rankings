# Smart products page — 2 November 2026

Scope: `https://aiuseflow.com/products.html` only, with two scoped presentation assets. The existing 11 paid products, original product covers, all detail and purchase links, INR/USD amounts, membership/per-participant labels, structured data and existing ad/consent/application scripts are retained.

Added: goal-based discovery; search including useful task aliases; six category filters; INR price sorting; local saved products; comparison of two or three products with a clear selection limit; expandable descriptions; informative empty/reset states; an animated branded hero with actual product covers; pause and reduced-motion support; ordering, payment-verification, free-tool and refund guidance.

The external AI Free and AI Plus catalogs remain. The payment backend, merchant details, checkout URLs, product files, database and subscription configuration are unchanged. No purchase or payment submission was made during verification. Basic utilities remain INR 0 and paid products remain optional.

Backup: `.private/products-before-smart-20261102.zip`, containing the original `products.html`. ZIP consistency and an extraction-to-original byte comparison passed locally before the private hosting upload. Prior full website/database backups remain available.

Build checks verify every original script, link, image and SEO title/description/canonical is retained. Preview tests cover all products, all 22 checkout links, search, goal discovery, empty/reset states, price ordering, saved products, compare limits/dialog, expandable content, animation pause and the external catalogs. Layout coverage includes 390px, 768px and 1280px in light and dark themes. Physical-device testing and actual payment completion are outside this presentation update.

Costs: no new dependency, paid API, subscription or hosting service. Existing hosting/payment-provider terms continue to apply. No search ranking or AdSense approval is guaranteed.

Source: `build.py` reproduces the enhancement from the actual pre-change page; generated release output stays excluded from source control. Use bounded file uploads for Hostinger; do not deploy the repository's older root build over the website.

Final preview: 17 checks passed, 0 failed, including readable hero text in both themes. Final asset version: `a339c5d23704`. Preview QA remains noindex and is excluded from production deployment.
