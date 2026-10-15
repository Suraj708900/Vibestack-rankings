# Promotions (sponsored slots)

All promos live in `promotions.json`. `promos.js` (loaded on every page) shows promos that are
`active: true` and where today is between `start` and `end` (inclusive, YYYY-MM-DD, UTC date).
Every promo is labelled **Sponsored**; entries with `"example": true` also get an **EXAMPLE** badge.
If several promos share a placement they rotate every 8 s (higher `priority` first; pauses on hover).
Rankings are never affected by promos.

## Placements
| value | where |
|---|---|
| `homepage-hero` | banner under the homepage headline |
| `category-top` | top of category pages (set `category` to a tools.json category id to target one; blank = all) |
| `sidebar-card` | floating card on wide screens / end of page on mobile (home + category) |
| `new-this-week` | top of /new.html |
| `sitewide-strip` | thin strip at the top of every page |

## Add a promo (easy way)
1. Open https://vibestack-rankings.vercel.app/admin-promos.html (also works locally).
2. Click **+ New promo**, fill the form (preview updates live), Save. Edits stay in your browser.
3. Click **Export promotions.json**, replace `promotions.json` in the repo, commit and redeploy.

The admin page has search, filters (placement / live / scheduled / ended), sorting and pagination,
so hundreds of promos are fine. It is a static page with no backend: it cannot change the live site by
itself, so it is safe to be public (it is `noindex`). Note `sponsor_contact` is visible in the public JSON;
put only a business email there.

## Fields
`id` (unique, a-z0-9-), `tool`, `logo` (URL, e.g. `https://www.google.com/s2/favicons?domain=TOOL.com&sz=128`),
`headline`, `cta`, `link` (https URL; gets rel="sponsored"), `placement`, `category`, `start`, `end`,
`priority` (number), `active` (bool), `example` (bool, placeholder only), `sponsor_contact`.

When a real sponsor books, delete or deactivate the matching `example-*` slot. Never mark a placeholder as a real sponsor.

## Automation (no manual steps after publishing)
- Promos start and expire on their own based on `start`/`end`; no redeploy needed to switch them on/off.
- Several promos in one slot rotate automatically (every 8 s, priority-ordered).
- The "Builder tips & tool spotlights" feed (`feed.json`, rendered by `feed.js`) picks 3 posts based on the
  date, so it changes daily without redeploying. Add posts by appending to `feed.json` (`type,title,body,link,logo,tags`).
