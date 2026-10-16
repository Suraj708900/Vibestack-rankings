// /api/account: GET profile + saved tools; POST {action:'save'|'unsave', slug}; DELETE {password} deletes the account.
const A = require('./_lib/auth');
module.exports = async (req, res) => {
  try {
    const u = await A.currentUser(req);
    if (!u) return A.json(res, 401, { error: 'Please log in.' });
    if (req.method === 'GET') return A.json(res, 200, A.publicUser(u));
    if (!A.sameOrigin(req)) return A.json(res, 403, { error: 'Forbidden.' });
    const b = typeof req.body === 'object' && req.body ? req.body : {};
    if (req.method === 'POST') {
      const slug = String(b.slug || '').toLowerCase();
      if (!/^[a-z0-9-]{1,60}$/.test(slug)) return A.json(res, 400, { error: 'Invalid tool.' });
      const s = new Set(u.saved || []);
      if (b.action === 'save') { if (s.size >= 500) return A.json(res, 400, { error: 'Save limit reached.' }); s.add(slug); }
      else if (b.action === 'unsave') s.delete(slug); else return A.json(res, 400, { error: 'Invalid action.' });
      u.saved = [...s]; await A.saveUser(u); return A.json(res, 200, { saved: u.saved });
    }
    if (req.method === 'DELETE') {
      if (!A.verifyPassword(String(b.password || ''), u.pw)) return A.json(res, 401, { error: 'Invalid password.' });
      await A.deleteUser(u.k); A.setCookie(res, '', 0); return A.json(res, 200, { ok: true, deleted: true });
    }
    return A.json(res, 405, { error: 'Method not allowed.' });
  } catch (e) { console.error('account error', e.message); return A.json(res, 500, { error: 'Something went wrong. Please try again.' }); }
};
