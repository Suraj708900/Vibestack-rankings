// /api/auth/{signup,login,logout,me}
const A = require('./_lib/auth');
const GENERIC = 'Invalid email or password.';
module.exports = async (req, res) => {
  const action = String((req.query && req.query.action) || '');
  try {
    if (action === 'me') { const u = await A.currentUser(req); return A.json(res, 200, { user: u ? { name: u.name, email: u.email, saved: u.saved || [] } : null }); }
    if (req.method !== 'POST') return A.json(res, 405, { error: 'Method not allowed.' });
    if (!A.sameOrigin(req)) return A.json(res, 403, { error: 'Forbidden.' });
    const b = typeof req.body === 'object' && req.body ? req.body : {};
    if (action === 'logout') { A.setCookie(res, '', 0); return A.json(res, 200, { ok: true }); }
    if (action === 'signup') {
      if (A.rateLimited(req, 'signup', 5, 60 * 60e3)) return A.json(res, 429, { error: 'Too many attempts. Try again later.' });
      const name = String(b.name || '').trim().slice(0, 80), email = A.normEmail(b.email), pw = String(b.password || ''), confirm = String(b.confirm || '');
      if (!name || !A.validEmail(email)) return A.json(res, 400, { error: 'Please enter your name and a valid email.' });
      if (pw.length < 8 || pw.length > 200) return A.json(res, 400, { error: 'Password must be 8 to 200 characters.' });
      if (pw !== confirm) return A.json(res, 400, { error: 'Passwords do not match.' });
      const k = A.keyFor(email);
      if (await A.loadUser(k)) return A.json(res, 400, { error: 'Could not create account. If you already have one, log in instead.' });
      const u = { k, name, email, pw: A.hashPassword(pw), created: new Date().toISOString(), saved: [], sv: 1, fails: 0, lockUntil: 0 };
      await A.saveUser(u); A.setCookie(res, A.sign(u), A.MAX_AGE);
      return A.json(res, 200, { ok: true, user: { name, email } });
    }
    if (action === 'login') {
      if (A.rateLimited(req, 'login', 10, 15 * 60e3)) return A.json(res, 429, { error: 'Too many attempts. Try again later.' });
      const email = A.normEmail(b.email), pw = String(b.password || '');
      const u = A.validEmail(email) ? await A.loadUser(A.keyFor(email)) : null;
      if (!u) { A.verifyPassword(pw, A.DUMMY); return A.json(res, 401, { error: GENERIC }); }
      if (u.lockUntil && u.lockUntil > Date.now()) return A.json(res, 429, { error: 'Too many attempts. Try again later.' });
      if (!A.verifyPassword(pw, u.pw)) {
        u.fails = (u.fails || 0) + 1; if (u.fails >= 8) { u.lockUntil = Date.now() + 15 * 60e3; u.fails = 0; }
        await A.saveUser(u); return A.json(res, 401, { error: GENERIC });
      }
      if (u.fails || u.lockUntil) { u.fails = 0; u.lockUntil = 0; await A.saveUser(u); }
      A.setCookie(res, A.sign(u), A.MAX_AGE); return A.json(res, 200, { ok: true, user: { name: u.name, email: u.email } });
    }
    return A.json(res, 404, { error: 'Not found.' });
  } catch (e) { console.error('auth error', e.message); return A.json(res, 500, { error: 'Something went wrong. Please try again.' }); }
};
