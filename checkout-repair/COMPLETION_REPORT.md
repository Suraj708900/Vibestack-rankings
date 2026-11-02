# Checkout and notifications repair — 3 November 2026

Status: implemented and tested in isolated staging; NOT published to production. Price changes are not included.

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
- A CLI-only worker and authenticated notification-status/retry endpoint are prepared. Add the documented five-minute cron only after production approval; preserve the existing hourly maintenance job.

## Evidence
- 17 backend checks + 23 mobile/desktop form/privacy checks + advertising and dual-owner regressions = 42 passed, 0 failed.
- PHP syntax checked for all 11 staged PHP files. Manual browser tests confirmed create -> payment reference -> pending verification -> private tracking, and contact reference acknowledgement.
- Clearly marked smoke emails were delivered by the provider to both owner addresses. Hostinger initially classified its copy as junk despite SPF/DKIM/DMARC passing; it was marked not junk and moved to Inbox. Inbox placement for future messages is not guaranteed.
- Verified hosting-side backup: 9 original source files, existing order records, consistent SQLite snapshot (`PRAGMA integrity_check=ok`); all 12 archive entries restored in memory and SHA-256 checked. Backup remains in protected hosting storage; customer data and credentials were not exported to this source repository.
- All test orders, contact messages and advertising inquiries use separate private sandbox storage. No real payment was submitted and no historical order or customer message was changed.

## Production steps after approval
1. Recheck live-file changes against the captured source and verified backup.
2. Upload the 16-file scoped release with rollback and checksum checks; do not deploy the whole legacy repository or the pending price-change branch.
3. Add `/usr/bin/php /home/u788467405/domains/aiuseflow.com/public_html/api/notification-worker.php` on `*/5 * * * *`; do not alter the existing maintenance cron.
4. Clear website cache, verify real live checkout/contact/tracking URLs and delivery statuses. Keep test notifications clearly labelled and avoid submitting real payments.

## Limits and costs
- UPI and PayPal payment links remain manual verification flows; opening or completing an external payment alone is not a verified webhook event. Customers must submit their reference. Automatic bank/PayPal verification needs separately configured provider webhooks and merchant access.
- Resend plan quota/rate limits and sender reputation apply. No new subscription or paid service was activated. Retry exhaustion is visible through the authenticated notification API; messages remain stored.
- Earlier product price changes remain separately staged on `aiuseflow4-smart-tools`; this branch preserves current live prices.
