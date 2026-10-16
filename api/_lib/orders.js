// Orders + signed download tokens. Orders: private Blob orders/<id>.json. Files: private Blob products/...
const crypto = require('crypto');
const { put, get, del, list } = require('@vercel/blob');
const CFG = require('../../data/products-config.json');
const ID_RE = /^VS[0-9A-Z]{6,14}$/;
const path = id => `orders/${id}.json`;
const secret = () => { const s = process.env.AUTH_SECRET; if (!s || s.length < 32) throw new Error('AUTH_SECRET missing'); return s; };
const hmac = s => crypto.createHmac('sha256', secret()).update('dl:' + s).digest('base64url');
async function loadOrder(id) {
  if (!ID_RE.test(id)) return null;
  const r = await get(path(id), { access: 'private', useCache: false }).catch(() => null);
  if (!r || r.statusCode !== 200) return null;
  return JSON.parse(await new Response(r.stream).text());
}
const saveOrder = (o, overwrite) => put(path(o.id), JSON.stringify(o), { access: 'private', addRandomSuffix: false, allowOverwrite: !!overwrite, contentType: 'application/json', cacheControlMaxAge: 60 });
const deleteOrder = id => del(path(id));
async function listOrders() {
  const out = []; let cursor;
  do { const r = await list({ prefix: 'orders/', cursor, limit: 1000 }); for (const b of r.blobs) out.push(b.pathname); cursor = r.hasMore ? r.cursor : null; } while (cursor && out.length < 2000);
  const ids = out.map(p => p.slice(7, -5)).filter(i => ID_RE.test(i));
  return (await Promise.all(ids.map(loadOrder))).filter(Boolean).sort((a, b) => b.created.localeCompare(a.created));
}
function makeToken(order, hours) {
  const p = Buffer.from(JSON.stringify({ o: order.id, f: order.file, exp: Math.floor(Date.now() / 1000) + hours * 3600 })).toString('base64url');
  return `${p}.${hmac(p)}`;
}
function readToken(t) {
  const [p, s] = String(t || '').split('.'); if (!p || !s) return null;
  const a = Buffer.from(s), b = Buffer.from(hmac(p)); if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { const d = JSON.parse(Buffer.from(p, 'base64url').toString()); return d.exp > Date.now() / 1000 ? d : null; } catch { return null; }
}
function isAdmin(req) {
  const want = process.env.ADMIN_TOKEN || ''; if (want.length < 24) return false;
  const got = String(req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  const a = crypto.createHash('sha256').update(got).digest(), b = crypto.createHash('sha256').update(want).digest();
  return crypto.timingSafeEqual(a, b);
}
module.exports = { CFG, ID_RE, loadOrder, saveOrder, deleteOrder, listOrders, makeToken, readToken, isAdmin };
