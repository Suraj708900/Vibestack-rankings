# AIUseFlow 4.0 implementation state

## Safety and architecture

Owner authorizes staging implementation; production publication requires separate approval. Current Hostinger static/PHP production and its existing preview, authentication, dashboard, blogs, editorial rankings, affiliate links and databases must be preserved.

- Live root: `/home/u788467405/domains/aiuseflow.com/public_html`.
- Existing preview root: `public_html/preview`. New module is confined to **`preview/smart-tools-v4/`**.
- Existing `/tools/` has 36 AI detail `.html` pages and no hub index. The candidate package adds folders/index and namespaced `/assets/smart-tools-v4/`; it does not replace those existing pages or root hosting rules.
- GitHub repository `Suraj708900/Vibestack-rankings` is a stale Vercel-era version relative to live PHP. Feature branch `aiuseflow4-smart-tools` is isolated. Never run the root Python build or deploy the whole repository. Hostinger reports no Git auto-deployment.

## Backup and preservation verified

Fresh protected archive outside the public root: `v4-backups-20261101/aiuseflow-4-full-before-upgrade.zip`.

- 220,573,304 bytes; SHA256 `6cc57d8552732a45f7007d2ce00be1cdf66b39b29eda7b691de3fc7f569b59f0`.
- All 12,475 ZIP entries streamed and CRC-verified, then extracted in a private restore test.
- Three consistent SQLite snapshots pass integrity checks.
- Current MySQL export: 21 tables, SHA256 `b0b3f65e09e91a917f54d0ab1c0e953f6e63e03e395aa79f8658ffc14e42644e`. Complete SQL imported successfully into a separate MariaDB bootstrap runtime, networking disabled, exit 0, 21 restored tables. SQL/data/credentials stay outside Git and public web access.
- Read-only comparison against the backup confirms **2,409 production application/content files unchanged**, zero missing files. Auth, account, AI endpoint, homepage, legal pages, ads.txt and consent.js match exactly.
- Production candidate dry run finds zero conflicting existing target files. It is **not deployed**.

## Implemented module

50 browser tools, searchable category hub, intent aliases, daily rotating pick, related tools, per-device trending/recent/favorites, bilingual tool names/form labels, English/Hindi interface controls, real download/export states, local-only ordinary file processing, explicit business drafts, free basic tier and no payment enrollment.

Live AI uses the existing same-origin free-model endpoint only. It rejects mock or wrong-provider responses, requires consent, enforces input limits and retains existing server quotas. No new billing, subscription, key or paid fallback was activated. Existing Groq account billing tier is not verified.

Tools privacy/terms supplements are additive `/tools/privacy/` and `/tools/terms/` pages. Staging has noindex metadata/headers; generated production assets are namespaced. Production rules apply only to new index pages/assets, preserving old AI detail page behavior.

## Verification

- 16 automated tests pass, including monetary allocation/rounding, GST, negative/zero ratios, markup rounding, URL/markup safety, barcode checksums, CSPRNG, file signatures, PDF round trips and mixed Hindi/Latin/rupee multipage PDF shaping.
- Dependency audit reports zero known vulnerabilities at audit time.
- All 53 new staging pages pass HTTP, unique title/description, canonical, single-H1, noindex, CSP and no-ad/analytics-tag checks.
- Initial first-six browser tests: all six pass after correcting QR CommonJS import/cache versioning.
- All nine dedicated AI writers and optional resume AI refinement return verified live provider output using generic synthetic facts.
- QR and Code128 PNGs independently decode to their expected data. Background alpha and GST PDF totals independently verified.
- PDF.js cleanup API and complex-script font runtime issues were found and fixed. Final full local-tool/extended/layout regression is pending; do not call it complete until final evidence is saved.

## Remaining publication gate / limitations

Production publication awaits owner approval. There are no new 4.0 production application changes. Signed-in legacy account/dashboard journeys have not been repeated with a real user session; unchanged source and public page/API availability are verified. Physical Android/iPhone and non-Chrome browser testing are not claimed. Core Web Vitals field results require real traffic.

Background removal supports connected solid colors, not arbitrary AI segmentation. PDF compression is image-only and may be larger on already optimized PDFs. Signatures are visual marks. Passport presets need authority-specific review. AI output is fallible/quota-limited. Local invoice numbering/drafts are not a global ledger or authenticated history. Some guidance remains English alongside bilingual names/labels.

## Operations

Backup/extraction/patch/audit jobs are one-off, idempotent CLI operations. Remove each temporary cron after success and retain existing hourly maintenance. Backup files and upload credentials must never be copied into source/public downloads. Existing production application data and payments are not overwritten or enrolled by this module.
