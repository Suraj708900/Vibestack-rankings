# Rich tool page body for every tool, from data only (tools.json, affiliates.json, optional tool_details.json).
# Never invents features, pros/cons or codes: optional fields render only when present in tool_details.json.
_AFF=json.load(open('affiliates.json'))['tools']
_DET=json.load(open('tool_details.json')) if os.path.exists('tool_details.json') else {}
_VER=[('n8n','n8n Cloud 14-day free trial','n8n states its Cloud plans come with a 14-day free trial.','https://n8n.io/affiliates/')]
def rich_tool(s,v,rk,alts,rel):
    t=v['t']; dom=t['url'].split('/')[2]; det=_DET.get(s,{}); a=_AFF.get(s,{})
    free='free-tier' in t.get('tags',[]) or 'free' in t.get('price','').lower()
    cta=lambda txt,cls='cta-big':f'<a class="{cls}" href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">{txt}</a>'
    shot=f'<img class="tool-shot" src="{E(det["screenshot"])}" alt="{E(t["name"])} screenshot" loading="lazy">' if det.get('screenshot') else ''
    hero=(f'<section class="tool-hero card"><img src="https://www.google.com/s2/favicons?domain={dom}&sz=128" width="72" height="72" alt="{E(t["name"])} logo" style="border-radius:14px">'
      f'<div><h1 style="margin:.1em 0">{E(t["name"])}</h1><p class="sub">Ranked {rk}</p><p>{E(t["verdict"])}</p>{cta("Try "+E(t["name"])+" →")}</div>{shot}</section>')
    feats=det.get('features') or []
    fh='<ul>'+''.join(f'<li>{E(x)}</li>' for x in feats)+'</ul>' if feats else '<p>'+''.join(f'<span class=tag>{E(x)}</span>' for x in t.get('tags',[]))+'</p><p class="sub">Detailed feature list coming soon; see the official site for the full feature set.</p>'
    pricing=(f'<div class="card"><h2>Pricing &amp; free plan</h2><p class="price">Pricing: {E(t["price"])}</p><p><b>Free plan:</b> {"Yes, a free tier is listed (confirm limits on the official pricing page)." if free else "No free tier listed in our data; check the official pricing page."}</p></div>')
    if a.get('status')=='active' and a.get('discount_code'):
        promo=f'<p>{E(a.get("discount_text",""))}</p><p><code>{E(a["discount_code"])}</code> <button data-code="{E(a["discount_code"])}" data-code-id="{s}">Copy code</button></p>'+(f'<p class="sub">Valid until {E(a["end"])}</p>' if a.get('end') else '')
    else: promo='<p><b>Verified discount code not available yet.</b> We never post unverified codes.</p>'
    promo+=''.join(f'<p>✅ {E(n)}: {E(x)} <span class="sub">Source: <a href="{E(u)}" rel="noopener nofollow" target="_blank">{E(u.split("/")[2])}</a></span></p>' for k,n,x,u in _VER if k==s)
    promo=f'<div class="card promo-box"><h2>Deals &amp; discount</h2>{promo}<p><a href="/deals/{s}.html">All {E(t["name"])} deal notes →</a></p></div>'
    pros,cons=det.get('pros') or [],det.get('cons') or []
    pc=('<div class="grid"><div class="card"><h2>Pros</h2><ul>'+''.join(f'<li>{E(x)}</li>' for x in pros)+'</ul></div><div class="card"><h2>Cons</h2><ul>'+''.join(f'<li>{E(x)}</li>' for x in cons)+'</ul></div></div>') if (pros or cons) else \
       f'<div class="card"><h2>Pros &amp; cons</h2><p><b>Why we picked it:</b> {E(t["verdict"])}</p><p class="sub">A detailed pros/cons breakdown has not been written yet.</p></div>'
    return (f'<p class="sub"><a href="/">Rankings</a> › <a href="/category/{v["ranks"][0][0]["id"]}.html">{E(v["ranks"][0][0]["name"])}</a> › {E(t["name"])}</p>'
      +hero+share(f'/tools/{s}.html',t["name"]+' review · '+SITE)
      +f'<div class="card"><h2>Features</h2>{fh}</div>'+pricing+promo+pc
      +('<h2>Alternatives</h2><ul>'+''.join(f'<li><a href="/tools/{slug(x["name"])}.html">{E(x["name"])}</a>: {E(x["verdict"])} <a class="sub" href="/compare.html?tools={s},{slug(x["name"])}">compare</a></li>' for x in alts)+'</ul>' if alts else '')
      +('<h2>Related guides</h2><ul>'+''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in rel)+'</ul>' if rel else '')
      +f'<div id="vote" data-vote="{s}"></div><div class="card cta-end"><h2>Ready to try {E(t["name"])}?</h2>{cta("Try "+E(t["name"])+" free →" if free else "Try "+E(t["name"])+" →")}</div><aside data-promo="sidebar-card"></aside>')
