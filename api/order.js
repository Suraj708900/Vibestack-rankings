// POST /api/order {id, product, method:'upi'|'paypal', name, email, utr (UPI UTR or PayPal transaction ID)}: records a UPI payment claim as a pending order for manual verification.
const { rateLimited, sameOrigin, normEmail, validEmail, json } = require('./_lib/auth');
const O = require('./_lib/orders');
module.exports = async (req, res) => {
  if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed.' });
  if (!sameOrigin(req)) return json(res, 403, { error: 'Forbidden.' });
  if (rateLimited(req, 'order', 6, 60 * 60e3)) return json(res, 429, { error: 'Too many attempts. Please try again later.' });
  const b = typeof req.body === 'object' && req.body ? req.body : {};
  if (b.company) return json(res, 200, { ok: true }); // honeypot
  const id = String(b.id || '').toUpperCase(), slug = String(b.product || ''), p = O.CFG.products[slug];
  const method = String(b.method || '').toLowerCase(), name = String(b.name || '').trim().slice(0, 80), email = normEmail(b.email), utr = String(b.utr || '').trim().toUpperCase();
  if (!O.ID_RE.test(id) || !p) return json(res, 400, { error: 'Invalid order. Please reload the checkout page.' });
  if (!['upi', 'paypal'].includes(method)) return json(res, 400, { error: 'Please choose UPI or PayPal.' });
  if (name.length < 2 || !validEmail(email)) return json(res, 400, { error: 'Please enter your name and a valid email.' });
  if (!/^[A-Z0-9]{10,22}$/.test(utr)) return json(res, 400, { error: method === 'upi' ? 'Please enter the UPI transaction reference (UTR), usually 12 digits.' : 'Please enter the PayPal transaction ID (17 characters).' });
  try {
    if (await O.loadOrder(id)) return json(res, 409, { error: 'This order was already submitted.' });
    const o = { id, product: slug, product_name: p.name, method, amount: method === 'upi' ? p.price : p.price_usd, currency: method === 'upi' ? 'INR' : 'USD', file: p.file, name, email, utr, status: 'pending', created: new Date().toISOString() };
    await O.saveOrder(o, false);
    return json(res, 200, { ok: true, id, status: 'pending' });
  } catch (e) { console.error('order failed', e.message); return json(res, 500, { error: 'Could not save your order. Please try again or email us.' }); }
};
