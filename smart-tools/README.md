# AIUseFlow 4.0 Smart Tools

Additive browser utilities for the existing AIUseFlow Hostinger website. This module is isolated from the repository's older Python/Vercel build. **Do not run the root build or deploy the repository wholesale.**

## Build and test

Use Node 24+, then run `npm ci`, `npm test`, `npm run build` inside `smart-tools/`. The prebuild step downloads the two official Noto fonts only when missing and checks their pinned SHA-256 hashes. The redistribution license is in `public/fonts/LICENSE.txt`.

`dist/` is for the existing preview subdomain's **new** `/smart-tools-v4/` folder. The folder has noindex metadata/headers and a staging banner. No existing preview page should be replaced.

`node build.mjs --production` generates an additive, **unpublished** `dist-production/` package: a new `/tools/index.html`, 50 unique tool folders, tool-specific privacy/terms supplements, and namespaced `/assets/smart-tools-v4/` files. Never copy its `.htaccess` over the website root. Production publication requires owner approval, a fresh backup, path conflict checks and rollback preparation. The existing 36 `/tools/*.html` directory pages must remain intact. New utility pages do not load advertising tags.

## Functionality and privacy

- PDFs: image-to-PDF with ordering/rotation/paper/margins/quality/preview; PDF raster-to-JPG ZIP; merge, split, raster compression, rotation, numbering, text watermark and visible signature image.
- Images: compression including a sequential batch ZIP, resizing, crop, format conversion, passport ratios, edge-connected solid-color background removal, target maximum byte sizes, watermark and pixel color values.
- Business: invoice/GST/quotation/receipt/purchase order PDFs, three visual styles, logo, live preview, explicit local drafts, and exact minor-unit calculations. Income/overhead, GST, discount and profit calculators. Local pattern-based business naming.
- Writing: nine dedicated live AI writers plus local resume PDF with optional live AI refinement. Uses the existing same-origin `/api/ai` endpoint, explicitly requests `groq-oss-20b`, checks live availability and rejects mock responses or a different provider. No new service key or paid fallback. Consent is required before sending text.
- Developer: QR PNG/SVG, Code128/EAN13/UPCA, JSON formatting/validation, Unicode-aware word count, CSPRNG passwords, meta tags, robots, sitemap, UTM and JSON-LD.

The user-facing basic tier is ₹0. No payment enrollment is included. Existing provider/account billing is separate and must be checked by the owner; do not imply an existing paid Groq organization becomes free because the website labels this model “free.” There is no added hosting subscription.

## Important limitations

Hindi PDF exports use browser-rendered image pages for correct complex-script shaping; body text is not selectable. Resume TXT export retains Unicode text for ATS/editing. English document PDFs retain selectable text.

PDF compression creates image-only pages and removes searchable text, forms, links and digital signatures. It may enlarge an already optimized PDF. Visible signatures are not cryptographic signatures. Encrypted PDFs are rejected. Background removal supports solid, edge-connected colors, not general AI segmentation. Passport presets do not guarantee official acceptance. Image conversion can remove metadata/animation. JSON numbers follow JavaScript precision. Local drafts and suggested invoice numbering are per-device, not a business-wide ledger or cloud history. GST templates are not IRN-registered e-invoices or tax returns. AI output needs human review and is subject to the current service quota.

## Verification

`tests/core.test.mjs` covers monetary rounding, GST, discounts, margin losses, zero denominators, allocation, page bounds, safe URLs/markup, barcode check digits, CSPRNG character sets, Unicode counts and real PDF round trips. The staging-only `qa.html` generates synthetic inputs, submits each tool's actual form, validates non-empty downloadable outputs, reloads PDFs/images/ZIPs, and exports evidence. It is excluded from the production build.

All browser automation is performed through the supported cloud browser. Mobile checks use a 390-CSS-pixel iframe in Chrome, not a physical Android/iPhone or a claim of all-browser certification. Search rankings and AdSense approval cannot be guaranteed.
