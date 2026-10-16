// Waitlist interest for our own (pre-launch) products. Stored privately in Vercel Blob as interest/<product>/<id>.json.
// POST stores {product,name,email,whatsapp}; the response includes a delete token so the submitter (or we, for tests) can remove it via DELETE.
const crypto = require('crypto');
const { put, del } = require('@vercel/blob');
const { rateLimited, sameOrigin, normEmail, validEmail } = require('./_lib/auth');
const PRODUCTS = ['ai-learning-kit', 'ai-business-toolkit', 'ai-prompt-library', 'live-ai-training', 'ai-receptionist-setup', 'ai-knowledge-membership', 'industry-ai-kits'];
const tok = p => crypto.createHmac('sha256', process.env.AUTH_SECRET || '').update('interest:' + p).digest('base64url');
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (!['POST', 'DELETE'].includes(req.method)) return res.status(405).json({ ok: false, error: 'POST only' });
  if (!sameOrigin(req)) return res.status(403).json({ ok: false, error: 'Bad origin' });
  if (rateLimited(req, 'interest', 5, 10 * 60 * 1000)) return res.status(429).json({ ok: false, error: 'Too many requests, please try again later.' });
  let b = req.body || {};
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
  if (!process.env.BLOB_READ_WRITE_TOKEN || !process.env.AUTH_SECRET) return res.status(503).json({ ok: false, error: 'Waitlist not configured yet.' });
  if (req.method === 'DELETE') {
    const p = String(b.id || ''), t = String(b.token || '');
    if (!/^interest\/[a-z-]{3,40}\/[0-9a-z]{10,40}\.json$/.test(p)) return res.status(400).json({ ok: false });
    const a = Buffer.from(t), w = Buffer.from(tok(p));
    if (a.length !== w.length || !crypto.timingSafeEqual(a, w)) return res.status(403).json({ ok: false });
    await del(p).catch(() => null); return res.status(200).json({ ok: true, deleted: p });
  }
  if (b.company) return res.status(200).json({ ok: true }); // honeypot
  const product = String(b.product || ''), name = String(b.name || '').trim().slice(0, 80), email = normEmail(b.email);
  const whatsapp = String(b.whatsapp || '').replace(/[^\d+]/g, '').slice(0, 16);
  if (!PRODUCTS.includes(product)) return res.status(400).json({ ok: false, error: 'Please choose a product.' });
  if (name.length < 2) return res.status(400).json({ ok: false, error: 'Please enter your name.' });
  if (!validEmail(email)) return res.status(400).json({ ok: false, error: 'Please enter a valid email.' });
  if (whatsapp && !/^\+?\d{8,15}$/.test(whatsapp)) return res.status(400).json({ ok: false, error: 'Please enter a valid WhatsApp number or leave it empty.' });
  if (b.consent !== true) return res.status(400).json({ ok: false, error: 'Please tick the consent box.' });
  const id = Date.now().toString(36) + crypto.randomBytes(6).toString('hex'), p = `interest/${product}/${id}.json`;
  try {
    await put(p, JSON.stringify({ product, name, email, whatsapp, at: new Date().toISOString() }), { access: 'private', addRandomSuffix: false, contentType: 'application/json' });
    return res.status(200).json({ ok: true, id: p, token: tok(p) });
  } catch (e) { console.error('interest failed', e.message); return res.status(500).json({ ok: false, error: 'Could not save right now.' }); }
};
