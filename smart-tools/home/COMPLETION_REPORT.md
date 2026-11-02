# AIUseFlow 4.0 — integrated homepage release

Production: https://aiuseflow.com/
Released: 2 November 2026, 02:51 UTC. Version: `4f059cf67797`.

## Completed and deployed

All 50 existing utilities can now open directly within the main homepage. Intent search, five categories, favorites, recently used tools, task shortcuts and related tools guide visitors to the right utility. Only the selected tool loads. A warning protects unfinished work before switching. Individual tool URLs remain available for search engines and bookmarks.

The homepage has an English-only professional hero, animated gradients and CSS/SVG 3D illustrations. Motion can be paused and reduced-motion preferences are supported. Shared visual and navigation improvements were applied to 1,258 public HTML pages while retaining the existing brand and theme preference.

Klap remains featured. Existing rankings, blog posts, affiliate URLs, dashboards, authentication and backend services were preserved. The publisher verified all 14,004 existing script blocks and page SEO metadata were retained across updated pages. Ad and consent scripts remain. No database or payment configuration was changed.

## Backup and restore verification

Before deployment, a 247,264,299-byte website archive was created. All 13,252 archive entries passed CRC verification, three SQLite snapshots were captured, and ten critical file restore comparisons passed. The previously verified MySQL snapshot was retained; this release did not take a fresh MySQL dump or modify MySQL.

Archive SHA-256: `d800944083ddcf00d22d1f4af112bd90947412db02af2b0a005133e861873613`.
Private hosting archive: `v4-release-backups/professional-home-20261102025101/before-homepage-integration.zip`.

## Testing

- 17 automated tests passed.
- 62 homepage staging checks passed, including all 50 inline tool forms, intent discovery, favorites, unfinished-work protection and six viewport/theme combinations.
- Actual photo PDF export independently parsed as two pages. Invoice export parsed as one page, with the expected total of INR 180.45.
- Original homepage scripts, affiliate destinations, all 31 Klap mentions, canonical URL and single H1 were checked.
- Representative shared-page checks passed 22 of 24 cases on the latest staging round. Two narrow privacy-page loads encountered transient upstream connection errors. The privacy page loaded after reload; these two cases are not claimed as passed.
- Live homepage and inline QR generation were verified in the browser. QR status was Ready and its PNG download link was present. The final live QR download transfer was not independently certified after the browser download wait timed out.
- HTTP and asset checks are recorded in `../tests/homepage-live-verification.json`.

## Staging, limitations and costs

QA pages and public-content samples remain on the preview subdomain. Production receives the homepage and shared presentation changes, not the QA harness. The existing hourly maintenance job remains; temporary deployment jobs were removed.

No new API, dependency subscription or paid service was introduced. Basic utilities remain INR 0. Existing hosting and AI provider usage still apply; the account's actual recurring bills and provider quotas were not certified. No payment subscription was activated.

Existing processor limitations remain: background removal handles simple solid backgrounds; stronger PDF compression can rasterize pages; signatures are visual rather than cryptographic; passport photos carry no acceptance guarantee. Authenticated invoice history, physical-device certification and logged-in legacy journey certification are not included. A successful AdSense application or ranking improvement cannot be guaranteed. Core Web Vitals field scores were not newly certified.

The repository's older root Python/Vercel build is not the Hostinger release workflow. Do not deploy that build over the live website. Use the scoped publisher and existing verified release process.
