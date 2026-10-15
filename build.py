#!/usr/bin/env python3
"""Static pre-render for SEO. Run: python3 build.py  (also runs automatically on Vercel via buildCommand).
Generates /category/*.html, /tools/*.html, /blog/*.html (+index), sitemap.xml, robots.txt, llms.txt,
and injects meta/OG/canonical into top-level pages. Change BASE when devresources.in is live."""
import json,os,re,html,glob,datetime
try: import markdown
except ImportError: markdown=None
BASE=os.environ.get('SITE_BASE','https://vibestack-rankings.vercel.app').rstrip('/')
SITE='VibeStack Rankings'; ROOT=os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
E=lambda s:html.escape(str(s),quote=True)
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
d=json.load(open('tools.json')); cats=d['categories']; UPD=d['updated']
NAV='<header><nav><a class="logo" href="/">VibeStack Rankings</a><a href="/">Rankings</a><a href="/new.html">New this week</a><a href="/blog/">Blog</a><a href="/featured.html">Get featured</a><a href="https://devresources-showcase.vercel.app" rel="noopener">Showcase</a><a href="/#newsletter">Newsletter</a></nav></header>'
FOOT=('<footer><p><b>Affiliate disclosure:</b> some links may be affiliate links, so we may earn a commission at no extra cost to you. Rankings are never sold; sponsored listings are always labeled.</p>'
 '<p><a href="/blog/">Blog</a> · '+' · '.join(f'<a href="/category/{c["id"]}.html">{E(c["name"])}</a>' for c in cats)+'</p>'
 '<p>© 2026 VibeStack Rankings by Suraj Kamdev · <a href="mailto:kamdevsuraj03@gmail.com">kamdevsuraj03@gmail.com</a></p></footer>')
def head(title,desc,path,typ='website',extra=''):
    url=BASE+path
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
     f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">'
     f'<meta property="og:type" content="{typ}"><meta property="og:site_name" content="{SITE}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">'
     f'<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}">'
     f'<link rel="stylesheet" href="/style.css">{extra}</head>')
ld=lambda o:'<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False).replace('</','<\\/')+'</script>'
SCRIPTS='<script src="/promos.js" defer></script><script src="/feed.js" defer></script>'
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
    return f'<div class="card"><span class="rank">#{i}</span><h3 style="margin:.4em 0"><a href="/tools/{slug(t["name"])}.html">{E(t["name"])}</a></h3><p>{E(t["verdict"])}</p><div class="price">{E(t["price"])}</div><p style="margin:.5em 0 0"><a href="{E(t["url"])}" target="_blank" rel="noopener sponsored">Official site ↗</a></p></div>'
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
    faq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":c['q'],"acceptedAnswer":{"@type":"Answer","text":f'Our top pick is {c["tools"][0]["name"]}: {c["tools"][0]["verdict"]}'}}]}
    il={"@context":"https://schema.org","@type":"ItemList","name":c['name'],"itemListElement":[{"@type":"ListItem","position":i+1,"name":t['name'],"url":BASE+f'/tools/{slug(t["name"])}.html'} for i,t in enumerate(c['tools'])]}
    rel=''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in pbycat.get(c['id'],[]))
    body=(f'<p class="sub"><a href="/">Rankings</a> › {E(c["name"])}</p><h1>{E(c["name"])}</h1><p class="sub">{E(c["q"])} Updated {UPD}.</p>'
      '<div data-promo="category-top" data-cat="'+c['id']+'"></div><div class="grid">'+''.join(tcard(t,i+1) for i,t in enumerate(c['tools']))+'</div>'
      +(f'<h2>Guides</h2><ul>{rel}</ul>' if rel else '')+'<h2>Other categories</h2><p>'+' · '.join(f'<a href="/category/{x["id"]}.html">{E(x["name"])}</a>' for x in cats if x is not c)+'</p><aside data-promo="sidebar-card"></aside>')
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
      f'<p class="sub">Ranked {rk}</p><div class="card"><h2>Verdict</h2><p>{E(t["verdict"])}</p><p class="price">Pricing: {E(t["price"])} (always check the official pricing page)</p>'
      f'<p>{"".join(f"<span class=tag>{E(x)}</span>" for x in t["tags"])}</p><p><a href="{E(t["url"])}" target="_blank" rel="noopener sponsored">Visit {E(t["name"])} ↗</a></p></div>'
      +('<h2>Alternatives</h2><ul>'+''.join(f'<li><a href="/tools/{slug(a["name"])}.html">{E(a["name"])}</a>: {E(a["verdict"])}</li>' for a in alts)+'</ul>' if alts else '')
      +('<h2>Related guides</h2><ul>'+''.join(f'<li><a href="/blog/{p["slug"]}.html">{E(p["title"])}</a></li>' for p in rel)+'</ul>' if rel else '')+'<aside data-promo="sidebar-card"></aside>')
    page(path,f'{t["name"]}: review, pricing notes & alternatives · {SITE}',f'{t["name"]}: {t["verdict"]} Ranked {", ".join(f"#{r} in {c["name"]}" for c,r in v["ranks"])}.',body,extra=ld(sw))
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
      +htmlbody+'</article><div data-promo="sidebar-card"></div><h2>Keep reading</h2><ul>'+''.join(f'<li><a href="/blog/{x["slug"]}.html">{E(x["title"])}</a></li>' for x in more[:5])+'</ul>'
      +(f'<p>See the full ranking: <a href="/category/{c["id"]}.html">{E(c["name"])}</a>.</p>' if c else ''))
    page(path,p['title'],p['description'],body,typ='article',extra=extra)
urls.append('/blog/')
page('/blog/',f'Blog: guides for vibe coders and AI builders · {SITE}','Practical, honest guides on AI coding agents, app builders, databases, hosting, AI APIs, agents, video and voice tools.',
  '<h1>Blog</h1><p class="sub">Practical guides for vibe coders and builders. No invented stats; prices always point to official pages.</p><div class="grid">'
  +''.join(f'<a class="card" style="text-decoration:none;color:inherit" href="/blog/{p["slug"]}.html"><span class="tag">{E(next((c["name"] for c in cats if c["id"]==p["category"]),""))}</span><h3>{E(p["title"])}</h3><p class="sub">{E(p["description"])}</p></a>' for p in sorted(posts,key=lambda x:x['title']))
  +'</div><div data-feed="/feed.json" data-count="3"></div>',
  extra=ld({"@context":"https://schema.org","@type":"Blog","name":SITE+" Blog","url":BASE+"/blog/"}))
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
            urls.insert(0,'/')
        elif f!='category.html': urls.append(path)
    open(f,'w').write(s)
today=datetime.date.today().isoformat()
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)+'</urlset>\n')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /admin-promos.html\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')
open('llms.txt','w').write(f'# {SITE}\n\n> Opinionated, ranked AI tools for vibe coders and builders, with honest verdicts, pricing notes (always pointing to official pricing) and official links. Sponsored placements are always labelled and never affect rankings.\n\n## Rankings\n'
 +''.join(f'- [{c["name"]}]({BASE}/category/{c["id"]}.html): {c["q"]} Picks: {", ".join(t["name"] for t in c["tools"])}\n' for c in cats)
 +'\n## Guides\n'+''.join(f'- [{p["title"]}]({BASE}/blog/{p["slug"]}.html): {p["description"]}\n' for p in posts)
 +f'\n## Data\n- [tools.json]({BASE}/tools.json): full ranking data\n')
print(f'built {len(cats)} categories, {len(tools)} tools, {len(posts)} posts, {len(urls)} sitemap urls')
