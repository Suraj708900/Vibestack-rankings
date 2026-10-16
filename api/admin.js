// Admin orders API (Authorization: Bearer ADMIN_TOKEN). GET list; POST {action:'paid'|'delete', id}.
const { json } = require('./_lib/auth');
const O = require('./_lib/orders');
async function email(o, link) {
  const key = process.env.RESEND_API_KEY, from = process.env.RESEND_FROM; // RESEND_FROM only set once a sending domain is verified
  if (!key || !from) return { sent: false, reason: 'No verified Resend sending domain configured (RESEND_FROM).' };
  const r = await fetch('https://api.resend.com/emails', { method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to: [o.email], subject: `Your download: ${o.product_name} (order ${o.id})`,
      text: `Hi ${o.name},\n\nThanks for your payment of ${o.currency} ${o.amount} for ${o.product_name}. Your download link (valid ${O.CFG.download_hours} hours):\n${link}\n\nOrder: ${o.id}\nQuestions? Reply to this email.\n\nVibeStack Rankings / Suraj Kamdev` }) });
  return r.ok ? { sent: true } : { sent: false, reason: `Resend error ${r.status}` };
}
module.exports = async (req, res) => {
  res.setHeader('X-Robots-Tag', 'noindex');
  if (!O.isAdmin(req)) return json(res, 401, { error: 'Unauthorized.' });
  try {
    if (req.method === 'GET') return json(res, 200, { orders: await O.listOrders() });
    if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed.' });
    const b = typeof req.body === 'object' && req.body ? req.body : {};
    const o = await O.loadOrder(String(b.id || '')); if (!o) return json(res, 404, { error: 'Order not found.' });
    if (b.action === 'delete') { await O.deleteOrder(o.id); return json(res, 200, { ok: true, deleted: o.id }); }
    if (b.action === 'paid') {
      const host = req.headers['x-forwarded-host'] || req.headers.host;
      const link = `https://${host}/api/download?token=${O.makeToken(o, O.CFG.download_hours)}`;
      const mail = await email(o, link).catch(e => ({ sent: false, reason: e.message }));
      o.status = 'paid'; o.paid_at = new Date().toISOString(); o.emailed = mail.sent; await O.saveOrder(o, true);
      return json(res, 200, { ok: true, order: o, link, email: mail });
    }
    return json(res, 400, { error: 'Invalid action.' });
  } catch (e) { console.error('admin failed', e.message); return json(res, 500, { error: 'Server error.' }); }
};
