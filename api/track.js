// Counts promo impressions/clicks and tool clicks. Storage: free Vercel Blob store (one tiny private blob per event,
// aggregated by /api/stats via list()). No personal data is stored: only kind, type, id and a timestamp.
const { put } = require('@vercel/blob');
const OK_KIND = ['promo', 'tool', 'code', 'vote', 'link'], OK_TYPE = ['impression', 'click', 'copy', 'up', 'down'];
module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  let b = req.body || {};
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
  const kind = String(b.kind || ''), type = String(b.type || ''), id = String(b.id || '');
  if (!OK_KIND.includes(kind) || !OK_TYPE.includes(type) || !/^[a-z0-9-]{1,60}$/.test(id)) return res.status(400).json({ ok: false });
  if ((kind === 'tool' && type !== 'click') || ((kind === 'code' || kind === 'link') && type !== 'copy') || (kind === 'promo' && !['impression', 'click'].includes(type)) || (kind === 'vote' && !['up', 'down'].includes(type)) || (kind !== 'vote' && ['up', 'down'].includes(type))) return res.status(400).json({ ok: false });
  const ua = String(req.headers['user-agent'] || '');
  if (/bot|crawl|spider|preview|headless/i.test(ua)) return res.status(204).end();
  if (!process.env.BLOB_READ_WRITE_TOKEN) { console.log('track', kind, type, id); return res.status(202).json({ ok: true, stored: false }); }
  const day = new Date().toISOString().slice(0, 10);
  try {
    await put(`ev/${day}/${kind}/${type}/${id}/${Date.now()}${Math.random().toString(36).slice(2, 7)}`, '1',
      { access: 'private', addRandomSuffix: false, contentType: 'text/plain' });
    return res.status(204).end();
  } catch (e) { console.error('track failed', e.message); return res.status(202).json({ ok: true, stored: false }); }
};
