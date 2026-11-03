# Checkout and notifications repair — 3 November 2026

Status: published to production on 3 November 2026 after explicit approval (“live kar do”). All 16 deployed files match the tested release. Product prices were not changed.

## Confirmed causes
- Live checkout reads `form.method.value` and `form.name.value`; browser inspection confirmed those properties are strings. This prevents reliable submission.
- Transactional email was disabled and the configured owner destination did not match the connected business mailbox.
- Contact page had only mailto links; it did not contain a functional web form.
- Advertising inquiry acknowledgements were not sent to customers.

## Prepared changes
- Save customer/order before exposing payment instructions. Server-generated tracking ID, idempotent retries, server-authoritative prices, UPI and PayPal links and lazily loaded QR.
- Payment-reference submission remains pending manual verification. No automatic debit, payment verification, subscription or paid upgrade is introduced.
- Private tracking link uses a hashed access token. Fragment is removed from the URL after reading. Status response excludes customer name/email, transaction reference and private product paths. Tracking page is noindex/no-referrer and contains no advertising/analytics scripts.
- Durable, independently retried owner emails to contact@aiuseflow.com and kamdevsuraj03@gmail.com; customer acknowledgement and verified-order download email. Existing Resend account is reused; its restrictions and dry-run settings are respected. No credentials are returned or changed.
- Working contact form with saved reference ID and truthful errors; advertising enquiry owner/customer notices. Failed delivery is queued rather than reported as confirmed delivery.
- Existing ad/consent scripts, payment recipients, product prices, URLs, authentication, paid-order verification, product files, site branding and existing orders are preserved.
- The CLI-only worker and authenticated notification-status/retry endpoint are deployed. The five-minute notification cron is enabled; the existing hourly maintenance job is preserved.

## Evidence
- 17 backend checks + 23 mobile/desktop form/privacy checks + advertising and dual-owner regressions = 42 passed, 0 failed.
- PHP syntax checked for all 11 staged PHP files. Manual browser tests confirmed create -> payment reference -> pending verification -> private tracking, and contact reference acknowledgement.
- Clearly marked smoke emails were delivered by the provider to both owner addresses. Hostinger initially classified its copy as junk despite SPF/DKIM/DMARC passing; it was marked not junk and moved to Inbox. Inbox placement for future messages is not guaranteed.
- Verified hosting-side backup: 9 original source files, existing order records, consistent SQLite snapshot (`PRAGMA integrity_check=ok`); all 12 archive entries restored in memory and SHA-256 checked. Backup remains in protected hosting storage; customer data and credentials were not exported to this source repository.
- All test orders, contact messages and advertising inquiries use separate private sandbox storage. No real payment was submitted and no historical order or customer message was changed.

## Production deployment and live verification
- Published only the approved 16-file repair; no legacy repository-wide build or pending price update was deployed.
- Live-change guards passed. A fresh protected restore archive and SQLite snapshot were verified immediately before publishing (database integrity `ok`, two existing orders preserved).
- All 16 server-side release checksums match; all eight public HTML/assets match exact release bytes. Checkout/contact/advertising/tracking pages return 200. Mutating checkout GET returns 405; notification administration returns 401 without credentials; the CLI worker returns 404 on web access; internal helpers return 403.
- Live checkout form and empty-field validation verified in the browser without creating a customer order or making a payment.
- Notification cron `*/5 * * * *` is enabled (UID Js12nCH6Ts). Existing maintenance cron HfMr1dKPYx is unchanged.
- Two clearly marked live-code test alerts were delivered by the provider to contact@aiuseflow.com and kamdevsuraj03@gmail.com. These tests did not create a customer order or payment.
- No credentials, payment recipients, subscriptions or prices were changed. Live screenshot saved as proof.

## Limits and costs
- UPI and PayPal payment links remain manual verification flows; opening or completing an external payment alone is not a verified webhook event. Customers must submit their reference. Automatic bank/PayPal verification needs separately configured provider webhooks and merchant access.
- Resend plan quota/rate limits and sender reputation apply. No new subscription or paid service was activated. Retry exhaustion is visible through the authenticated notification API; messages remain stored.
- Earlier product price changes remain separately staged on `aiuseflow4-smart-tools`; this branch preserves current live prices.
