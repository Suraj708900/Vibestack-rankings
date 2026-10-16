// /go/<slug> -> logs an outbound click (kind "aff") then 302s to the active affiliate URL, else the official URL.
const { put } = require('@vercel/blob');
const A = require('../affiliates.json');
const DIR = require('../data/go-directory.json'); // directory tools: official URL only
const PR = require('../data/go-pricing.json'); // verified pricing-page URLs (whitelist for ?to=pricing)
const live = a => a && a.status === 'active' && /^https:\/\//.test(a.affiliate_url || '') &&
  (!a.start || a.start <= new Date().toISOString().slice(0, 10)) && (!a.end || a.end >= new Date().toISOString().slice(0, 10));
module.exports = async (req, res) => {
  const slug = String((req.query && req.query.slug) || '').toLowerCase();
  const ok = /^[a-z0-9-]{1,60}$/.test(slug);
  const a = ok && (A.tools[slug] || (DIR[slug] && /^https?:\/\//.test(DIR[slug]) ? { official_url: DIR[slug] } : null));
  if (!a) { res.setHeader('Location', '/'); return res.status(302).end(); }
  const toPricing = req.query && req.query.to === 'pricing' && /^https:\/\//.test(PR[slug] || '');
  const dest = toPricing ? PR[slug] : (live(a) ? a.affiliate_url : a.official_url);
  const ua = String(req.headers['user-agent'] || '');
  if (process.env.BLOB_READ_WRITE_TOKEN && !/bot|crawl|spider|preview|headless/i.test(ua)) {
    const day = new Date().toISOString().slice(0, 10);
    try { await put(`ev/${day}/aff/click/${toPricing ? slug + '-pricing' : slug}/${Date.now()}${Math.random().toString(36).slice(2, 7)}`, '1', { access: 'private', addRandomSuffix: false, contentType: 'text/plain' }); } catch (e) { console.error('go log failed', e.message); }
  }
  res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  res.setHeader('Location', dest); return res.status(302).end();
};
