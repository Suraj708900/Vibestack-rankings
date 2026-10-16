// Aggregates the last N days (default 7, max 30) of events from Blob into counts. Cached at the edge for 5 min
// so list() operations stay well inside the free tier.
const { list } = require('@vercel/blob');
module.exports = async (req, res) => {
  const days = Math.min(30, Math.max(1, parseInt((req.query && req.query.days) || '7', 10) || 7));
  const out = { days, since: null, promos: {}, tools: {}, aff: {}, codes: {}, stored: !!process.env.BLOB_READ_WRITE_TOKEN, truncated: false };
  res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');
  if (!out.stored) return res.status(200).json(out);
  let ops = 0;
  try {
    for (let d = 0; d < days; d++) {
      const day = new Date(Date.now() - d * 864e5).toISOString().slice(0, 10); out.since = day;
      let cursor;
      do {
        const r = await list({ prefix: `ev/${day}/`, cursor, limit: 1000 }); ops++;
        for (const bl of r.blobs) {
          const [, , kind, type, id] = bl.pathname.split('/');
          if (kind === 'promo') { const p = out.promos[id] = out.promos[id] || { impressions: 0, clicks: 0 }; p[type === 'click' ? 'clicks' : 'impressions']++; }
          else if (kind === 'tool' && type === 'click') out.tools[id] = (out.tools[id] || 0) + 1;
          else if (kind === 'aff') out.aff[id] = (out.aff[id] || 0) + 1;
          else if (kind === 'code') out.codes[id] = (out.codes[id] || 0) + 1;
        }
        cursor = r.hasMore ? r.cursor : undefined;
        if (ops >= 40) { out.truncated = true; cursor = undefined; d = days; }
      } while (cursor);
    }
  } catch (e) { out.error = 'stats unavailable'; console.error(e.message); }
  return res.status(200).json(out);
};
