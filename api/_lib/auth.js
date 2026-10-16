// Shared account helpers. Users live in the project's private Vercel Blob store as users/<sha256(email)>.json.
const crypto = require('crypto');
const { put, get, del } = require('@vercel/blob');
const COOKIE = 'vs_session', MAX_AGE = 30 * 24 * 3600;
const secret = () => { const s = process.env.AUTH_SECRET; if (!s || s.length < 32) throw new Error('AUTH_SECRET missing'); return s; };
const b64u = b => Buffer.from(b).toString('base64url');
const hmac = s => crypto.createHmac('sha256', secret()).update(s).digest('base64url');
const keyFor = email => crypto.createHash('sha256').update(email).digest('hex');
const path = k => `users/${k}.json`;
const normEmail = e => String(e || '').trim().toLowerCase();
const validEmail = e => e.length <= 254 && /^[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$/.test(e);

function hashPassword(pw) {
  const salt = crypto.randomBytes(16);
  const h = crypto.scryptSync(pw, salt, 64, { N: 16384, r: 8, p: 1 });
  return `scrypt$16384$8$1$${salt.toString('base64')}$${h.toString('base64')}`;
}
function verifyPassword(pw, stored) {
  try {
    const [alg, N, r, p, s, h] = String(stored).split('$'); if (alg !== 'scrypt') return false;
    const want = Buffer.from(h, 'base64');
    const got = crypto.scryptSync(pw, Buffer.from(s, 'base64'), want.length, { N: +N, r: +r, p: +p });
    return crypto.timingSafeEqual(got, want);
  } catch { return false; }
}
const DUMMY = hashPassword(crypto.randomBytes(12).toString('hex')); // equalize timing for unknown emails

async function loadUser(k) {
  const r = await get(path(k), { access: 'private', useCache: false }).catch(() => null);
  if (!r || r.statusCode !== 200) return null;
  return JSON.parse(await new Response(r.stream).text());
}
async function saveUser(u) {
  await put(path(u.k), JSON.stringify(u), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json', cacheControlMaxAge: 60 });
}
async function deleteUser(k) { await del(path(k)); }

function sign(u) {
  const p = b64u(JSON.stringify({ k: u.k, v: u.sv || 1, exp: Math.floor(Date.now() / 1000) + MAX_AGE }));
  return `${p}.${hmac(p)}`;
}
function readSession(req) {
  const m = String(req.headers.cookie || '').match(/(?:^|;\s*)vs_session=([^;]+)/); if (!m) return null;
  const [p, sig] = m[1].split('.'); if (!p || !sig) return null;
  const a = Buffer.from(sig), b = Buffer.from(hmac(p)); if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { const s = JSON.parse(Buffer.from(p, 'base64url').toString()); return s.exp > Date.now() / 1000 ? s : null; } catch { return null; }
}
async function currentUser(req) {
  const s = readSession(req); if (!s) return null;
  const u = await loadUser(s.k); return u && (u.sv || 1) === s.v ? u : null;
}
const setCookie = (res, val, age) => res.setHeader('Set-Cookie', `${COOKIE}=${val}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${age}`);

// Basic rate limiting: per-IP sliding window in function memory (best effort per instance) + per-account lockout stored on the user record.
const hits = new Map();
function rateLimited(req, bucket, max, windowMs) {
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'x';
  const k = bucket + ':' + ip, now = Date.now(), arr = (hits.get(k) || []).filter(t => now - t < windowMs);
  arr.push(now); hits.set(k, arr); if (hits.size > 5000) hits.clear();
  return arr.length > max;
}
function sameOrigin(req) {
  const o = req.headers.origin; if (!o) return true;
  try { return new URL(o).host === req.headers.host; } catch { return false; }
}
const json = (res, code, obj) => { res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Robots-Tag', 'noindex'); res.status(code).json(obj); };
const publicUser = u => ({ name: u.name, email: u.email, created: u.created, saved: u.saved || [] });
module.exports = { normEmail, validEmail, keyFor, hashPassword, verifyPassword, DUMMY, loadUser, saveUser, deleteUser, sign, setCookie, currentUser, rateLimited, sameOrigin, json, publicUser, MAX_AGE };
