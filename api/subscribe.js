// Vercel serverless function: adds an email to the Resend audience.
// Needs env vars RESEND_API_KEY (full access) and RESEND_AUDIENCE_ID.
module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  let b = req.body || {};
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = Object.fromEntries(new URLSearchParams(b)); } }
  if (b.company) return res.status(200).json({ ok: true }); // honeypot
  const email = String(b.email || '').trim().toLowerCase();
  if (!/^[^\s@]{1,64}@[^\s@]{1,255}\.[a-z]{2,}$/.test(email)) return res.status(400).json({ ok: false, error: 'Please enter a valid email.' });
  const key = process.env.RESEND_API_KEY, aud = process.env.RESEND_AUDIENCE_ID;
  if (!key || !aud) return res.status(500).json({ ok: false, error: 'Signup not configured yet.' });
  const r = await fetch(`https://api.resend.com/audiences/${aud}/contacts`, {
    method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, unsubscribed: false })
  });
  if (!r.ok) return res.status(502).json({ ok: false, error: 'Could not subscribe right now.' });
  return res.status(200).json({ ok: true });
};
