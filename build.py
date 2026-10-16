#!/usr/bin/env python3
"""Static pre-render for SEO. Run: python3 build.py  (also runs automatically on Vercel via buildCommand).
Generates /category/*.html, /tools/*.html, /blog/*.html (+index), sitemap.xml, robots.txt, llms.txt,
and injects meta/OG/canonical into top-level pages. Change BASE when devresources.in is live."""
import json,os,re,html,glob,datetime,subprocess,shutil,urllib.parse
try: import markdown
except ImportError: markdown=None
BASE=os.environ.get('SITE_BASE','https://vibestack-rankings.vercel.app').rstrip('/')
GSC_VERIFICATION=''  # paste Google Search Console token here
GSCM=f'<meta name="google-site-verification" content="{GSC_VERIFICATION}">' if GSC_VERIFICATION else ''
INDEXNOW_KEY='4bc94dce2e8b15bfe59f1ffa5e81787b'
SITE='VibeStack Rankings'; ROOT=os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
E=lambda s:html.escape(str(s),quote=True)
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
d=json.load(open('tools.json')); cats=d['categories']; UPD=d['updated']
NAV='<header><nav><a class="logo" href="/">VibeStack Rankings</a><a href="/">Rankings</a><a href="/new.html">New this week</a><a href="/blog/">Blog</a><a href="/submit.html">Submit a tool</a><a href="/deals/">Deals</a><a href="/featured.html">Get featured</a><a href="https://devresources-showcase.vercel.app" rel="noopener">Showcase</a><a href="/#newsletter">Newsletter</a><button class="sx-btn" data-search aria-label="Search (Ctrl+K)">🔍 Search <kbd>Ctrl K</kbd></button></nav></header>'
FOOT=('<footer><p><b>Affiliate disclosure:</b> some links may be affiliate links, so we may earn a commission at no extra cost to you. Rankings are never sold; sponsored listings are always labeled.</p>'
 '<p><a href="/blog/">Blog</a> · '+' · '.join(f'<a href="/category/{c["id"]}.html">{E(c["name"])}</a>' for c in cats)+'</p>'
 '<p>© 2026 VibeStack Rankings by Suraj Kamdev · <a href="mailto:kamdevsuraj03@gmail.com">kamdevsuraj03@gmail.com</a></p></footer>')
def head(title,desc,path,typ='website',extra=''):
    url=BASE+path
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
     f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">'
     f'<meta property="og:type" content="{typ}"><meta property="og:site_name" content="{SITE}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">'
     f'<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}">'
     f'<link rel="preconnect" href="https://www.google.com"><link rel="dns-prefetch" href="https://www.google.com"><link rel="stylesheet" href="/style.min.css">{GSCM}{extra}</head>')
ld=lambda o:'<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False).replace('</','<\\/')+'</script>'
def share(path,title):
    u=urllib.parse.quote(BASE+path,safe='');t=urllib.parse.quote(title,safe='')
    return (f'<div class="share" aria-label="Share"><span class="sub">Share:</span> <a href="https://twitter.com/intent/tweet?url={u}&text={t}" target="_blank" rel="noopener">X</a> <a href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener">LinkedIn</a> <a href="https://wa.me/?text={t}%20{u}" target="_blank" rel="noopener">WhatsApp</a> <button class="s" data-copy>Copy link</button></div>')
NL=('<section id="post-newsletter" class="card nl-box"><h2>Get the weekly stack</h2><p class="sub">Rank movers and new AI tools for builders, once a week. Free, no spam, unsubscribe anytime.</p>'
 '<form class="bar nlf"><input type="email" name="email" placeholder="you@example.com" required aria-label="Email"><input name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true"><button type="submit">Subscribe</button><span class="nlmsg sub" style="align-self:center"></span></form></section>')
SCRIPTS='<script src="/site.min.js" defer></script><script src="/promos.min.js" defer></script><script src="/feed.min.js" defer></script><script defer src="/_vercel/insights/script.js"></script><script defer src="/_vercel/speed-insights/script.js"></script>'
def page(path,title,desc,body,typ='website',extra='',bodyattr=''):
    full=os.path.join(ROOT,path.lstrip('/')); full=full+'index.html' if full.endswith('/') else full
    os.makedirs(os.path.dirname(full),exist_ok=True)
    open(full,'w').write(head(title,desc,path,typ,extra)+f'<body{bodyattr}>'+NAV+'<main>'+body+'</main>'+FOOT+SCRIPTS+'</body></html>')
urls=[]
# tools
tools={}
for c in cats:
    for i,t in enumerate(c['tools']):
        s=slug(t['name']); tools.setdefault(s,{'t':t,'ranks':[]})['ranks'].append((c,i+1))
def tcard(t,i):
    return f'<div class="card"><span class="rank">#{i}</span><h3 style="margin:.4em 0"><img src="https://www.google.com/s2/favicons?domain={t["url"].split("/")[2]}&sz=64" width="22" height="22" alt="" loading="lazy" decoding="async" style="vertical-align:-4px;border-radius:5px;margin-right:6px"><a href="/tools/{slug(t["name"])}.html">{E(t["name"])}</a></h3><p>{E(t["verdict"])}</p><div class="price">{E(t["price"])}</div><p style="margin:.5em 0 0"><a href="/go/{slug(t["name"])}" data-tool="{slug(t["name"])}" target="_blank" rel="sponsored nofollow noopener">Official site ↗</a></p></div>'
# blog parse
posts=[]
for f in sorted(glob.glob('content/blog/*.md')):
    raw=open(f).read(); fm,body=raw.split('\n---\n',1); meta=dict(l.split(': ',1) for l in fm.strip().splitlines())
    meta['slug']=os.path.basename(f)[:-3]; meta['md']=body; posts.append(meta)
pbycat={}
for p in posts: pbycat.setdefault(p['category'],[]).append(p)
# categories
for c in cats:
    path=f'/category/{c["id"]}.html'; urls.append(path)
    names=', '.join(t['name'] for t in c['tools'][:3])
    title=f'Best {c["name"]} for vibe coders ({UPD[:4]}): {names}'
    desc=f'{c["q"]} Our ranked picks: '+', '.join(t['name'] for t in c['tools'])+'. Honest verdicts, pricing notes, official links.'
    top=c['tools'][0]; names=', '.join(t['name'] for t in c['tools'])
    faq_pairs=[
      (c['q'], f'Our ranked picks are {names}. Top pick: {top["name"]} — {top["verdict"]} Pricing note: {top["price"]}.'),
      (f'What is the #1 pick in {c["name"]} right now?', f'{top["name"]}. {top["verdict"]} See the official site for current pricing ({top["price"]}).'),
      (f'Which tools in {c["name"]} have a free tier?', 
        ('These picks mention a free tier: '+', '.join(t['name'] for t in c['tools'] if 'free-tier' in t.get('tags',[]) or 'free' in t.get('price','').lower())+'. Always confirm on the official pricing page.')
        if any('free-tier' in t.get('tags',[]) or 'free' in t.get('price','').lower() for t in c['tools'])
        else 'Check each official pricing page — free tiers change often. We only note free when the tool tags or price field say so.'),
    ]
    faq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_pairs]}
    il={"@context":"https://schema.org","@type":"ItemList","name":c['name'],"itemListElement":[{"@type":"ListItem","position":i+1,"name":t['name'],"url":BASE+f'/tools/{slug(t["name"])}.html'} for i,t in enumerate(c['tools'])]}
    rel=''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in pbycat.get(c['id'],[]))
    faq_html='<section class="faq" aria-labelledby="faq-h"><h2 id="faq-h">FAQ</h2>'+''.join(
      f'<details class="faq-item"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q,a in faq_pairs)+'</section>'
    body=(f'<p class="sub"><a href="/">Rankings</a> › {E(c["name"])}</p><h1>{E(c["name"])}</h1><p class="sub">{E(c["q"])} Updated {UPD}.</p>'
      +share(path,title)+'<div data-promo="category-top" data-cat="'+c['id']+'"></div><div class="grid">'+''.join(tcard(t,i+1) for i,t in enumerate(c['tools']))+'</div>'
      +faq_html+(f'<h2>Guides</h2><ul>{rel}</ul>' if rel else '')+'<h2>Other categories</h2><p>'+' · '.join(f'<a href="/category/{x["id"]}.html">{E(x["name"])}</a>' for x in cats if x is not c)+'</p><aside data-promo="sidebar-card"></aside>')
    page(path,title,desc,body,extra=ld(faq)+ld(il))
# tool pages
for s,v in tools.items():
    t=v['t']; path=f'/tools/{s}.html'; urls.append(path)
    rk=' · '.join(f'#{r} in <a href="/category/{c["id"]}.html">{E(c["name"])}</a>' for c,r in v['ranks'])
    alts=[x for c,_ in v['ranks'] for x in c['tools'] if x['name']!=t['name']][:5]
    rel=[p for c,_ in v['ranks'] for p in pbycat.get(c['id'],[])][:4]
    dom=t['url'].split('/')[2]
    sw={"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"applicationCategory":"DeveloperApplication","description":t['verdict']}
    body=(f'<p class="sub"><a href="/">Rankings</a> › <a href="/category/{v["ranks"][0][0]["id"]}.html">{E(v["ranks"][0][0]["name"])}</a> › {E(t["name"])}</p>'
      f'<h1><img src="https://www.google.com/s2/favicons?domain={dom}&sz=64" width="40" height="40" alt="" style="vertical-align:middle;border-radius:8px"> {E(t["name"])}</h1>'
      f'<p class="sub">Ranked {rk}</p>'+share(path,t["name"]+' review · '+SITE)+f'<div class="card"><h2>Verdict</h2><p>{E(t["verdict"])}</p><p class="price">Pricing: {E(t["price"])} (always check the official pricing page)</p>'
      f'<p>{"".join(f"<span class=tag>{E(x)}</span>" for x in t["tags"])}</p><p><a href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">Visit {E(t["name"])} ↗</a></p></div>'
      +('<h2>Alternatives</h2><ul>'+''.join(f'<li><a href="/tools/{slug(a["name"])}.html">{E(a["name"])}</a>: {E(a["verdict"])}</li>' for a in alts)+'</ul>' if alts else '')
      +('<h2>Related guides</h2><ul>'+''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in rel)+'</ul>' if rel else '')+'<aside data-promo="sidebar-card"></aside>')
    page(path,f'{t["name"]}: review, pricing notes & alternatives · {SITE}',f'{t["name"]}: {t["verdict"]} Ranked {", ".join(f"#{r} in {c["name"]}" for c,r in v["ranks"])}.',body,extra=ld(sw))

# deals (only real, cited offers; codes only when Suraj adds them to affiliates.json)
AFF=json.load(open('affiliates.json'))['tools']
def offer_html(s,a):
    if a.get('status')=='active' and a.get('discount_code'):
        return (f'<div class="card"><h3>{E(a["name"])}</h3><p>{E(a.get("discount_text",""))}</p><p><code>{E(a["discount_code"])}</code> <button data-code="{E(a["discount_code"])}" data-code-id="{s}">Copy code</button></p>'
          +(f'<p class="sub">Valid {E(a.get("start",""))} to {E(a.get("end",""))}</p>' if a.get('end') else '')+f'<a href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">Use on {E(a["name"])} ↗</a></div>')
    return ''
VERIFIED=[('n8n','n8n Cloud 14-day free trial','n8n states its Cloud plans come with a 14-day free trial.','https://n8n.io/affiliates/')]
codes=''.join(offer_html(s,a) for s,a in AFF.items())
db=('<h1>AI tool deals &amp; discount codes</h1><p class="sub">We only list offers we can verify on a public page, with the source linked. No invented codes or percentages. Last checked '+UPD+'.</p>'
  +'<h2>Verified public offers</h2><div class="grid">'+''.join(f'<div class="card"><h3><a href="/tools/{s}.html">{E(n)}</a></h3><p>{E(t)}</p><p class="sub">Source: <a href="{E(u)}" rel="noopener nofollow" target="_blank">{E(u.split("/")[2])}</a></p><a href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">Visit ↗</a></div>' for s,n,t,u in VERIFIED)+'</div>'
  +'<h2>Exclusive codes</h2>'+(f'<div class="grid">{codes}</div>' if codes else '<p class="card">No exclusive codes yet. When we get a real code from a tool\'s partner program it will appear here with its terms. Makers: <a href="/featured.html">get in touch</a>.</p>')
  +'<h2>Pricing, free trial &amp; alternatives by tool</h2><ul>'+''.join(f'<li><a href="/deals/{s}.html">{E(a["name"])} discount code, pricing &amp; free trial</a></li>' for s,a in AFF.items())+'</ul>')
page('/deals/',f'AI tool deals, discount codes & free trials · {SITE}','Verified deals, free trials and pricing notes for AI coding, app-builder, video and voice tools. Only real offers with sources.',db); urls.append('/deals/')
for s,a in AFF.items():
    if s not in tools: continue
    t=tools[s]['t']; v=tools[s]; path=f'/deals/{s}.html'; urls.append(path)
    alts=[x for c,_ in v['ranks'] for x in c['tools'] if x['name']!=t['name']][:5]
    ver=[x for x in VERIFIED if x[0]==s]; code=offer_html(s,a)
    dtxt=(f'Yes: {a["discount_text"]} (code shown below).' if code else f'We have not verified any public {t["name"]} discount code. Codes found on coupon sites are often fake or expired; we only list codes we can confirm.')
    faq=[(f'Is there a {t["name"]} discount code?',dtxt),
         (f'How much does {t["name"]} cost?',f'Our note: {t["price"]}. Prices change, so check the official {t["name"]} pricing page before buying.'),
         (f'Does {t["name"]} have a free trial or free tier?',(ver[0][2] if ver else ('Our listing tags it with a free tier; confirm on the official site.' if ('free-tier' in t.get('tags',[]) or 'free' in t.get('price','').lower()) else 'Check the official pricing page; we only state free tiers we can confirm.'))),
         (f'What are the best {t["name"]} alternatives?',', '.join(x['name'] for x in alts)+'. See the ranked comparison pages for verdicts.' if alts else 'See our category rankings.')]
    fl={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',x)}} for q,x in faq]}
    body=(f'<p class="sub"><a href="/deals/">Deals</a> › {E(t["name"])}</p><h1>{E(t["name"])} discount code, pricing, free trial &amp; alternatives</h1>'+share(path,t["name"]+' deals & pricing · '+SITE)
      +(code or '<div class="card"><p><b>No verified discount code right now.</b> We never publish made-up codes.</p></div>')
      +''.join(f'<div class="card"><h3>{E(n)}</h3><p>{E(x)}</p><p class="sub">Source: <a href="{E(u)}" rel="noopener nofollow" target="_blank">{E(u.split("/")[2])}</a></p></div>' for _,n,x,u in ver)
      +f'<div class="card"><h2>Pricing</h2><p>{E(t["price"])}</p><p>{E(t["verdict"])}</p><p><a href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">Check current {E(t["name"])} pricing ↗</a> · <a href="/tools/{s}.html">Full review</a></p></div>'
      +('<h2>Alternatives</h2><ul>'+''.join(f'<li><a href="/tools/{slug(x["name"])}.html">{E(x["name"])}</a> (<a href="/deals/{slug(x["name"])}.html">deals</a>): {E(x["verdict"])}</li>' for x in alts)+'</ul>' if alts else '')
      +'<h2>FAQ</h2>'+''.join(f'<h3>{E(q)}</h3><p>{E(x)}</p>' for q,x in faq))
    page(path,f'{t["name"]} discount code, pricing & free trial (2026) · {SITE}',f'Is there a {t["name"]} discount code? Honest answer, pricing notes, free trial info and the best {t["name"]} alternatives.',body,extra=ld(fl))
# blog
for p in posts:
    path=f'/blog/{p["slug"]}.html'; urls.append(path)
    md=p['md']; faqs=[]
    if '## FAQ' in md:
        for q,a in re.findall(r'### (.+?)\n(.+?)(?=\n###|\Z)',md.split('## FAQ',1)[1],re.S): faqs.append((q.strip(),a.strip()))
    htmlbody=markdown.markdown(md,extensions=['extra']) if markdown else '<p>'+E(md)+'</p>'
    words=len(md.split())
    art={"@context":"https://schema.org","@type":"Article","headline":p['title'],"description":p['description'],"datePublished":p['date'],"dateModified":p['date'],
         "author":{"@type":"Person","name":"Suraj Kamdev"},"publisher":{"@type":"Organization","name":SITE,"url":BASE},"mainEntityOfPage":BASE+path,"keywords":p['keyword'],"wordCount":words}
    extra=ld(art)+(ld({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub(r'\[(.+?)\]\(.+?\)',r'\1',a)}} for q,a in faqs]}) if faqs else '')
    extra+=f'<meta property="article:published_time" content="{p["date"]}">'
    more=[x for x in posts if x is not p and x['category']==p['category']]+[x for x in posts if x is not p and x['category']!=p['category']]
    c=next((c for c in cats if c['id']==p['category']),None)
    body=(f'<p class="sub"><a href="/blog/">Blog</a>{f" › <a href=/category/{c["id"]}.html>{E(c["name"])}</a>" if c else ""}</p><article class="post"><h1>{E(p["title"])}</h1><p class="sub">By Suraj Kamdev · {p["date"]} · {max(1,words//220)} min read</p>'
      +share(path,p['title'])+htmlbody+share(path,p['title'])+'</article>'+NL+'<div data-promo="sidebar-card"></div><h2>Related posts</h2><ul>'+''.join(f'<li><a href="/blog/{x["slug"]}.html">{E(x["title"])}</a></li>' for x in more[:5])+'</ul>'
      +(f'<p>See the full ranking: <a href="/category/{c["id"]}.html">{E(c["name"])}</a>.</p>' if c else ''))
    page(path,p['title'],p['description'],body,typ='article',extra=extra,bodyattr=' data-page="post"')
urls.append('/blog/')
page('/blog/',f'Blog: guides for vibe coders and AI builders · {SITE}','Practical, honest guides on AI coding agents, app builders, databases, hosting, AI APIs, agents, video and voice tools.',
  '<h1>Blog</h1><p class="sub">Practical guides for vibe coders and builders. No invented stats; prices always point to official pages.</p><div class="grid">'
  +''.join(f'<a class="card" style="text-decoration:none;color:inherit" href="/blog/{p["slug"]}.html"><span class="tag">{E(next((c["name"] for c in cats if c["id"]==p["category"]),""))}</span><h3>{E(p["title"])}</h3><p class="sub">{E(p["description"])}</p></a>' for p in sorted(posts,key=lambda x:x['title']))
  +'</div><div data-feed="/feed.json" data-count="3"></div>',
  extra=ld({"@context":"https://schema.org","@type":"Blog","name":SITE+" Blog","url":BASE+"/blog/"}))
posts_by_new=sorted(posts,key=lambda p:(p['date'],os.path.getmtime(f"content/blog/{p['slug']}.md")),reverse=True)
LATEST='<section class="latest"><h2>Latest from the blog</h2><div class="grid">'+''.join(f'<a class="card" style="text-decoration:none;color:inherit" href="/blog/{p["slug"]}.html"><h3 style="margin:.2em 0">{E(p["title"])}</h3><p class="sub">{E(p["description"])}</p></a>' for p in posts_by_new[:6])+'</div><p><a href="/blog/">All guides →</a></p></section>'
urls.append('/submit.html')
page('/submit.html',f'Submit a tool · {SITE}','Suggest an AI tool for VibeStack Rankings. Rankings are editorial and never sold.',
 '<h1>Submit a tool</h1><p class="sub">Know an AI tool vibe coders should know about? Send it in. Every submission is reviewed; rankings are editorial and never sold. Want a paid, clearly labelled placement instead? See <a href="/featured.html">Get featured</a>.</p>'
 '<div class="card"><h2>What to include</h2><ul><li>Tool name and official link</li><li>Which category it fits ('+', '.join(E(c['name']) for c in cats)+')</li><li>One or two sentences on what it is best for</li><li>Pricing model (free tier? link to the pricing page)</li><li>Are you the maker? (fine, just tell us)</li></ul>'
 '<p><a class="promo-cta" style="display:inline-block" href="mailto:kamdevsuraj03@gmail.com?subject=Tool%20submission%3A%20&body=Tool%20name%3A%0AOfficial%20link%3A%0ACategory%3A%0ABest%20for%3A%0APricing%3A%0AAre%20you%20the%20maker%3F%3A">Email your submission →</a></p></div>'
 '<h2>Popular guides</h2><ul>'+''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in posts_by_new[:5])+'</ul>')
# search index
six=[{"y":"category","t":c['name'],"d":c['q'],"u":f"/category/{c['id']}.html","k":' '.join(t['name'] for t in c['tools'])} for c in cats]
six+=[{"y":"tool","t":v['t']['name'],"d":v['t']['verdict'],"u":f"/tools/{s_}.html","k":' '.join(v['t']['tags'])+' '+' '.join(c['name'] for c,_ in v['ranks'])} for s_,v in tools.items()]
six+=[{"y":"guide","t":p['title'],"d":p['description'],"u":f"/blog/{p['slug']}.html","k":p['keyword']} for p in posts_by_new]
six+=[{"y":"page","t":t_,"d":d_,"u":u_} for t_,d_,u_ in [("Get featured","Sponsored placements","/featured.html"),("Submit a tool","Suggest a tool for the rankings","/submit.html"),("New this week","Notable AI releases","/new.html"),("Blog","All guides","/blog/"),("Showcase","Gallery of tool logos and designs","https://devresources-showcase.vercel.app")]]
json.dump(six,open('search-index.json','w'),ensure_ascii=False,separators=(',',':'))
# trending (editor picks fallback; site.js swaps in real click data when there is enough)
picks=[(c,c['tools'][0]) for c in cats][:6]
TREND=('<section id="trending" class="trending"><h2>Editor\'s picks this week</h2><p class="sub">Our current #1 pick per use-case, chosen by us (not view counts). This switches to real click-based trends once there is enough data.</p><div class="grid">'
 +''.join(f'<a class="card" style="text-decoration:none;color:inherit" href="/tools/{slug(t["name"])}.html"><span class="tag">{E(c["name"])}</span><h3 style="margin:.4em 0"><img src="https://www.google.com/s2/favicons?domain={t["url"].split("/")[2]}&sz=64" width="22" height="22" alt="" loading="lazy" decoding="async" style="vertical-align:-4px;border-radius:5px;margin-right:6px">{E(t["name"])}</h3><p class="sub">{E(t["verdict"])}</p></a>' for c,t in picks)+'</div></section>')
# admin stats page
page('/admin-stats.html',f'Stats · {SITE}','Promo and tool click stats.','''<h1>Stats</h1><p class="sub">Promo impressions, clicks and CTR, plus outbound tool clicks. Data comes from <code>/api/stats</code> (free Vercel Blob store). Impressions count once per promo per browser session; bots are ignored. Cached for 5 minutes.</p>
<div class="bar"><select id="days"><option value="1">Last 24h</option><option value="7" selected>Last 7 days</option><option value="30">Last 30 days</option></select><button id="rf">Refresh</button><span id="st" class="sub" style="align-self:center"></span></div>
<h2>Promos</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Promo</th><th>Placement</th><th>Impressions</th><th>Clicks</th><th>CTR</th></tr></thead><tbody id="pt"></tbody></table></div>
<h2>Trending tools (outbound clicks)</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>#</th><th>Tool</th><th>Clicks</th></tr></thead><tbody id="tt"></tbody></table></div>
<h2>Outbound /go/ clicks (affiliate links)</h2><p class="sub">Clicks per /go/&lt;slug&gt; link. Conversions and commissions are only visible in each affiliate network's dashboard (Impact, PartnerStack, Rewardful, etc.).</p><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Link</th><th>Clicks</th></tr></thead><tbody id="at"></tbody></table></div>
<h2>Discount code copies</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Tool</th><th>Copies</th></tr></thead><tbody id="ct"></tbody></table></div>
<script>
const H=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function load(){const d=document.getElementById('days').value;document.getElementById('st').textContent='Loading…';
 const [s,p]=await Promise.all([fetch('/api/stats?days='+d).then(r=>r.json()),fetch('/promotions.json').then(r=>r.json())]);
 const meta={};(p.promotions||[]).forEach(x=>meta[x.id]=x);
 const ids=[...new Set([...Object.keys(s.promos||{}),...Object.keys(meta)])];
 document.getElementById('pt').innerHTML=ids.map(id=>{const c=(s.promos||{})[id]||{impressions:0,clicks:0},m=meta[id]||{};return [id,m,c]}).sort((a,b)=>b[2].impressions-a[2].impressions).map(([id,m,c])=>`<tr><td>${H(m.tool||id)}${m.example?' <span class=tag>EXAMPLE</span>':''}<div class=sub>${H(id)}</div></td><td>${H(m.placement||'')}</td><td>${c.impressions}</td><td>${c.clicks}</td><td>${c.impressions?(100*c.clicks/c.impressions).toFixed(1)+'%':'–'}</td></tr>`).join('');
 const t=Object.entries(s.tools||{}).sort((a,b)=>b[1]-a[1]);
 const rows=(o,n)=>{const e=Object.entries(o||{}).sort((a,b)=>b[1]-a[1]);return e.length?e.map(([id,c])=>`<tr><td>/go/${H(id)}</td><td>${c}</td></tr>`).join(''):`<tr><td colspan=2 class=sub>${n}</td></tr>`};document.getElementById('at').innerHTML=rows(s.aff,'No /go/ clicks yet.');document.getElementById('ct').innerHTML=rows(s.codes,'No code copies yet.');
 document.getElementById('tt').innerHTML=t.length?t.map(([id,n],i)=>`<tr><td>${i+1}</td><td><a href="/tools/${H(id)}.html">${H(id)}</a></td><td>${n}</td></tr>`).join(''):'<tr><td colspan=3 class=sub>No clicks recorded yet.</td></tr>';
 document.getElementById('st').textContent=s.stored?('Updated '+new Date().toLocaleTimeString()+(s.truncated?' (truncated)':'')):'Storage not configured: counts are not being saved.'}
document.getElementById('rf').onclick=load;document.getElementById('days').onchange=load;load();
</script>''',extra='<meta name="robots" content="noindex,nofollow">')
# minify assets
def minify():
    css=open('style.css').read();css=re.sub(r'/\*.*?\*/','',css,flags=re.S);css=re.sub(r'\s+',' ',css);css=re.sub(r'\s*([{}:;,>])\s*',r'\1',css).replace(';}','}')
    open('style.min.css','w').write(css.strip())
    ters=shutil.which('terser') or ('/tmp/blobt/node_modules/.bin/terser' if os.path.exists('/tmp/blobt/node_modules/.bin/terser') else None)
    for f in ['site','promos','feed','app']:
        if ters and subprocess.run([ters,f+'.js','-c','-m','-o',f+'.min.js']).returncode==0: continue
        shutil.copy(f+'.js',f+'.min.js')
minify()
# inject meta into hand-written top-level pages + prerender homepage list
TOP={'index.html':('/','VibeStack Rankings: AI tools for vibe coders, ranked','Ranked AI tools for vibe coders and builders: coding agents, app builders, databases, hosting, AI APIs, agents, video and voice. Honest verdicts and official links.'),
 'new.html':('/new.html','New this week in AI for builders · VibeStack Rankings','Notable AI releases for builders this week, every item linked to its source.'),
 'featured.html':('/featured.html','Get your AI tool featured · VibeStack Rankings','Sponsored placements on VibeStack Rankings: homepage hero, category top slot, sidebar, new-this-week and sitewide strip. Always labelled.'),
 'thanks.html':('/thanks.html','Thanks · VibeStack Rankings','Thanks for subscribing.'),
 'category.html':('/category.html','Categories · VibeStack Rankings','Ranked AI tool categories for vibe coders.'),
 'admin-promos.html':(None,None,None)}
for f,(path,title,desc) in TOP.items():
    s=open(f).read(); s=re.sub(r'<!--seo-->.*?<!--/seo-->','',s,flags=re.S)
    s=re.sub(r'<header><nav>.*?</nav></header>',NAV,s,count=1,flags=re.S)
    if path:
        h=head(title,desc,path); tags=re.search(r'<link rel="canonical".*?(?=<link rel="stylesheet")',h).group(0)
        noidx='<meta name="robots" content="noindex">' if f=='thanks.html' else ''
        s=s.replace('</title>','</title><!--seo-->'+tags+noidx+'<!--/seo-->',1)
        if f=='index.html':
            s=s.replace('</head>','<!--seo-->'+ld({"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":BASE})+'<!--/seo--></head>',1)
            pre='<!--seo-->'+''.join(f'<section class="cat"><h2><a href="/category/{c["id"]}.html">{E(c["name"])} →</a></h2><p class="sub">{E(c["q"])}</p><div class="grid">'+''.join(tcard(t,i+1) for i,t in enumerate(c['tools']))+'</div></section>' for c in cats)+'<!--/seo-->'
            s=re.sub(r'<div id="app">.*?</div><div data-feed','<div id="app">'+pre+'</div><div data-feed',s,count=1,flags=re.S)
            s=re.sub(r'<!--latest-->.*?<!--/latest-->','',s,flags=re.S);s=re.sub(r'<!--trend-->.*?<!--/trend-->','',s,flags=re.S)
            s=s.replace('<div class="grid" id="cats"','<!--trend-->'+TREND+'<!--/trend--><div class="grid" id="cats"',1)
            s=s.replace('<div data-feed','<!--latest-->'+LATEST+'<!--/latest--><div data-feed',1)
            urls.insert(0,'/')
        elif f!='category.html': urls.append(path)
    s=s.replace('href="/style.css"','href="/style.min.css"')
    for js in ['app','promos','feed']: s=s.replace(f'src="/{js}.js"',f'src="/{js}.min.js"')
    s=re.sub(r'<!--rt-->.*?<!--/rt-->','',s,flags=re.S)
    s=s.replace('</body>','<!--rt--><script src="/site.min.js" defer></script><script defer src="/_vercel/insights/script.js"></script><script defer src="/_vercel/speed-insights/script.js"></script><!--/rt--></body>',1)
    if 'preconnect' not in s: s=s.replace('<link rel="stylesheet"','<link rel="preconnect" href="https://www.google.com"><link rel="stylesheet"',1)
    if GSCM and 'google-site-verification' not in s: s=s.replace('</head>',GSCM+'</head>',1)
    open(f,'w').write(s)
today=datetime.date.today().isoformat()
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)+'</urlset>\n')
open(INDEXNOW_KEY+'.txt','w').write(INDEXNOW_KEY)
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /admin-promos.html\nDisallow: /admin-stats.html\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')
news=d.get('news',[])
open('llms.txt','w').write(f'# {SITE}\n\n> Opinionated, ranked AI tools for vibe coders and builders, with honest verdicts, pricing notes (always pointing to official pricing) and official links. Sponsored placements are always labelled and never affect rankings.\n\n## Rankings\n'
 +''.join(f'- [{c["name"]}]({BASE}/category/{c["id"]}.html): {c["q"]} Picks: {", ".join(t["name"] for t in c["tools"])}\n' for c in cats)
 +('\n## New this week\n'+''.join(f'- [{n["title"]}]({n["url"]}) ({n["date"]}, via {n["source"]})\n' for n in news) if news else '')
 +'\n## Guides\n'+''.join(f'- [{p["title"]}]({BASE}/blog/{p["slug"]}.html): {p["description"]}\n' for p in posts)
 +f'\n## Data\n- [tools.json]({BASE}/tools.json): full ranking data\n- [New this week page]({BASE}/new.html)\n')
print(f'built {len(cats)} categories, {len(tools)} tools, {len(posts)} posts, {len(urls)} sitemap urls')
