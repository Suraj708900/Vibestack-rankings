// GET /api/download?token=... streams the purchased file from private Blob (products/...) if the signed token is valid and unexpired.
const { get } = require('@vercel/blob');
const O = require('./_lib/orders');
const { Readable } = require('stream');
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Robots-Tag', 'noindex');
  const t = O.readToken(req.query && req.query.token);
  if (!t || !/^products\/[A-Za-z0-9._\/-]{1,200}$/.test(t.f || '') || t.f.includes('..')) return res.status(403).send('This download link is invalid or has expired. Email kamdevsuraj03@gmail.com with your order ID for a new link.');
  const o = await O.loadOrder(t.o).catch(() => null);
  if (!o || o.status !== 'paid') return res.status(403).send('Order not confirmed.');
  const r = await get(t.f, { access: 'private' }).catch(() => null);
  if (!r || r.statusCode !== 200) return res.status(404).send('The file for this product is being prepared. Email kamdevsuraj03@gmail.com with your order ID and we will send it right away.');
  res.setHeader('Content-Type', r.blob.contentType || 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="${t.f.split('/').pop()}"`);
  Readable.fromWeb(r.stream).pipe(res);
};
