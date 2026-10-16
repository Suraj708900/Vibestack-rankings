# Affiliate / partner programs for tools on VibeStack Rankings

Researched 2026-10-16 (Asia/Colombo). Nothing has been signed up for. Commission is listed only where the program states it publicly, with the source. Re-check terms before applying: they change.

| Tool | Program / signup URL | Network | Commission (public, with source) | Free to join? |
|---|---|---|---|---|
| Lovable | https://lovable.dev/partners/affiliates | Impact (per openaffiliate.dev listing) | "Up to $100 for each first-time subscriber" (source: lovable.dev/partners/affiliates) | Yes, application + approval |
| ElevenLabs | https://elevenlabs.io/affiliate | PartnerStack | 22% of payments for first 12 months on Starter/Creator/Pro/Scale; 11% on Business; paid after 90 days active (source: elevenlabs.io/affiliate) | Yes, application |
| HeyGen | https://www.heygen.com/affiliate-program (terms: https://heygen.getrewardful.com/terms) | Rewardful | 35% for first 3 months on Creator/Team plans; 30-day last-click; $30 min payout via PayPal; no search ads allowed (source: heygen.com affiliate page) | Yes, application |
| Runway | https://runway.com/affiliate-program | In-house | $15 per new paying subscriber via your code; accepted partners' code gives followers 25% off; 3-month pilot; needs a Runway account and an active social channel (source: runway.com/affiliate-program) | Yes, application (creator-focused) |
| n8n | https://n8n.io/affiliates/ | In-house dashboard | 30% on n8n Cloud referrals for 12 months (source: n8n.io/affiliates) | Yes, application |
| Replit | Referral program inside Replit account | In-house | Referral credits (not cash): $10 credit to each party per referred paying user per affiliateotter.com; openaffiliate.dev lists $20 credits. Unconfirmed on an official page, so verify in-app | Yes |
| Kling AI | https://kling.ai/explore/kling_affiliate_program | Unknown | Not publicly stated | Unknown |
| Bolt.new | Not confirmed | In-house (per openaffiliate.dev, unverified) | Not published | Unknown |
| Supabase | No public affiliate program (per affilipilot.io, checked 2026-08-25) | – | – | – |

Not found / not confirmed in this pass: Cursor, Windsurf, Vapi, Render, Neon, Vercel, GitHub Copilot, the AI API providers. Check their sites for partner pages before assuming none exist.

## How to activate one
1. Apply yourself (Suraj). Once approved, put the tracking link in `site/affiliates.json` -> `affiliate_url`, set `status` to `active`, and optionally `start`/`end`.
2. Only add `discount_code` / `discount_text` if the program gave you a real code (e.g. Runway partner codes). It then shows on /deals and /deals/<tool>.html with a Copy code button.
3. Run `python3 build.py`, commit, deploy. /go/<slug> starts redirecting to the affiliate URL automatically.
4. Follow each program's disclosure rules; the site footer already carries an affiliate disclosure.
