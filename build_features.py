# Extra pages for VibeStack features (compare, embed docs). exec()'d from build.py before sitemap write;
# uses build.py globals: page, urls, tools, cats, slug, E, ld, share, BASE, SITE, d.
def _free(t): return 'free-tier' in t.get('tags',[]) or 'free' in t.get('price','').lower()
def _row(s):
    v=tools[s]; t=v['t']
    return {'s':s,'n':t['name'],'cat':', '.join(f'#{r} in {c["name"]}' for c,r in v['ranks']),'catH':' · '.join(f'#{r} in <a href="/category/{c["id"]}.html">{E(c["name"])}</a>' for c,r in v['ranks']),
            'price':t['price'],'free':'Yes (per listing; confirm on official site)' if _free(t) else 'Not listed','best':c_q(v),'verdict':t['verdict'],'tags':', '.join(t.get('tags',[]))}
def c_q(v): return v['ranks'][0][0]['q']
def _table(sl):
    rs=[_row(s) for s in sl]
    hdr='<tr><th></th>'+''.join(f'<th><a href="/tools/{r["s"]}.html">{E(r["n"])}</a></th>' for r in rs)+'</tr>'
    rows=[('Category & rank','catH',1),('Pricing','price',0),('Free tier','free',0),('Best for','best',0),('Tags','tags',0),('Verdict','verdict',0)]
    body=''.join('<tr><th>'+lab+'</th>'+''.join(f'<td>{r[k] if raw else E(r[k])}</td>' for r in rs)+'</tr>' for lab,k,raw in rows)
    body+='<tr><th>Official site</th>'+''.join(f'<td><a href="/go/{r["s"]}" data-tool="{r["s"]}" target="_blank" rel="sponsored nofollow noopener">Visit {E(r["n"])} ↗</a></td>' for r in rs)+'</tr>'
    return '<div style="overflow-x:auto"><table class="tbl cmp-tbl">'+hdr+body+'</table></div>'
PAIRS=[('cursor','windsurf'),('cursor','github-copilot'),('claude-code','openai-codex'),('lovable','bolt'),('supabase','firebase'),('vercel','netlify'),('openai-api','anthropic-api'),('claude-code','cursor')]
PAIRS=[p for p in PAIRS if all(x in tools for x in p)]
cmp_links=''.join(f'<li><a href="/compare/{a}-vs-{b}.html">{E(tools[a]["t"]["name"])} vs {E(tools[b]["t"]["name"])}</a></li>' for a,b in PAIRS)
opts=''.join(f'<option value="{s}">{E(v["t"]["name"])}</option>' for s,v in sorted(tools.items(),key=lambda x:x[1]['t']['name'].lower()))
page('/compare.html',f'Compare AI tools side by side · {SITE}','Pick 2 or 3 AI tools and compare category rank, pricing notes, free tier, best use and our verdict side by side. Shareable links.',
 '<p class="sub"><a href="/">Rankings</a> › Compare</p><h1>Compare AI tools</h1><p class="sub">Pick 2–3 tools. The URL updates so you can share the comparison.</p>'
 +'<div class="bar" id="cmp-pick">'+''.join(f'<select data-cmp="{i}" aria-label="Tool {i+1}"><option value="">{"— optional third tool —" if i==2 else "Choose a tool"}</option>{opts}</select>' for i in range(3))+'<button class="s" data-copy>Copy link</button></div>'
 +'<div id="cmp-out"><p class="sub">Choose at least two tools above.</p></div><h2>Popular comparisons</h2><ul>'+cmp_links+'</ul>')
urls.append('/compare.html')
for a,b in PAIRS:
    A,B=tools[a]['t']['name'],tools[b]['t']['name']; path=f'/compare/{a}-vs-{b}.html'; urls.append(path)
    page(path,f'{A} vs {B}: side-by-side comparison · {SITE}',f'{A} vs {B} compared: category rank, pricing notes, free tier, best use and our verdict, side by side.',
     f'<p class="sub"><a href="/">Rankings</a> › <a href="/compare.html">Compare</a> › {E(A)} vs {E(B)}</p><h1>{E(A)} vs {E(B)}</h1>'+share(path,f'{A} vs {B} · {SITE}')
     +_table([a,b])+f'<p class="sub">Pricing changes often; always check each official pricing page. <a href="/compare.html?tools={a},{b}">Add a third tool →</a></p><h2>More comparisons</h2><ul>{cmp_links}</ul>')
# embed docs
catopts=' · '.join(f'<code>{c["id"]}</code>' for c in cats)
snip=E(f'<div data-vibestack-embed="coding-agents" data-count="3"></div>\n<script src="{BASE}/embed.js" async></script>')
page('/embed.html',f'Embed a Top picks widget · {SITE}','Free embeddable widget: show our current top AI tool picks for any category on your site with one copy-paste snippet.',
 '<p class="sub"><a href="/">Rankings</a> › Embed</p><h1>Embed our top picks</h1><p class="sub">Show a live “Top picks” card for any category on your blog or docs. It updates automatically when our rankings change. Free; just keep the credit link.</p>'
 +'<div class="card"><div class="bar"><select id="emb-cat" aria-label="Category">'+''.join(f'<option value="{c["id"]}">{E(c["name"])}</option>' for c in cats)+'</select><select id="emb-n" aria-label="Count"><option>3</option><option>5</option></select><select id="emb-th" aria-label="Theme"><option value="dark">Dark</option><option value="light">Light</option></select></div>'
 +f'<h2>Snippet</h2><pre id="emb-code" style="white-space:pre-wrap;overflow-x:auto"><code>{snip}</code></pre><button class="s" id="emb-copy">Copy snippet</button><h2>Preview</h2><div id="emb-prev"><div data-vibestack-embed="coding-agents" data-count="3"></div></div></div>'
 +f'<h2>Options</h2><ul><li><code>data-vibestack-embed</code>: category id, one of {catopts}</li><li><code>data-count</code>: 1–5 picks (default 3)</li><li><code>data-theme</code>: <code>dark</code> (default) or <code>light</code></li></ul>',
 extra='<script src="/embed.js" defer></script>')
urls.append('/embed.html')
ters=shutil.which('terser') or ('/tmp/blobt/node_modules/.bin/terser' if os.path.exists('/tmp/blobt/node_modules/.bin/terser') else None)
if not (ters and subprocess.run([ters,'features.js','-c','-m','-o','features.min.js']).returncode==0): shutil.copy('features.js','features.min.js')
# homepage showcase: every category as premium cards (photo + logo + rank badge + verdict + CTA + real vote line)
import photos as PH
_AFFT=json.load(open('affiliates.json'))['tools']
def _sc(c):
    out=''
    for i,t in enumerate(c['tools']):
        s=slug(t['name']); lg=f'/img/tools/{s}-logo.webp'
        out+=(f'<article class="card sc-card">'+PH.banner(c['id'],s,lg,t['name'],badge=f'<span class="rank-badge r{i+1}" title="Editorial rank">#{i+1}</span>')
          +f'<div class="sc-body"><h3><a href="/tools/{s}.html">{E(t["name"])}</a></h3><p class="sub">{E(t["verdict"])}</p>{PH.cta(s,t["name"],_AFFT.get(s),"cta-aff sm")}{PH.voteline(s)}</div></article>')
    return f'<section class="showcase" id="sc-{c["id"]}"><h2>{E(c["name"])}</h2><p class="sub">{E(c["q"])}</p><div class="sc-grid">{out}</div><p><a href="/category/{c["id"]}.html">Full {E(c["name"])} ranking →</a></p></section>'
def _sc_coding(c):
    cur=[slug(t['name']) for t in c['tools']]; html_=''; n=0
    for i,t in enumerate(c['tools']):
        s=slug(t['name']); n+=1
        html_+=(f'<article class="card sc-card">'+PH.banner(c['id'],s,f'/img/tools/{s}-logo.webp',t['name'],badge=f'<span class="rank-badge r{i+1}" title="Editorial rank">#{i+1}</span>')
          +f'<div class="sc-body"><h3><a href="/tools/{s}.html">{E(t["name"])}</a></h3><p class="sub l1">{E(t["verdict"])}</p>{PH.cta(s,t["name"],_AFFT.get(s),"cta-aff sm")}{PH.voteline(s)}</div></article>')
    DD=json.load(open('data/directory.json'))['tools']; seen=set(cur)|{slug(t['name']) for cc in cats for t in cc['tools'] if cc['id']=='coding-agents'}
    extra=sorted([t for t in DD if t['department'] in ('coding-agents','ides') and t['slug'] not in seen and not t.get('curated_page')],key=lambda t:t['name'].lower())
    for t in extra[:60-n]:
        n+=1; s=t['slug']; hid=' sc-more' if n>12 else ''
        html_+=(f'<article class="card sc-card{hid}">'+PH.banner('coding-agents',s,t['logo'],t['name'],badge=f'<span class="rank-badge listed" title="Listed order, not an editorial ranking">Listed #{n}</span>')
          +f'<div class="sc-body"><h3><a href="/t/{s}.html">{E(t["name"])}</a></h3><p class="sub l1">{E(t["description"][:110])}</p>{PH.cta(s,t["name"],_AFFT.get(s),"cta-aff sm")}</div></article>')
    return (f'<section class="showcase" id="sc-{c["id"]}"><h2>{E(c["name"])}: top 5 picks + {n-len(cur)} more listed</h2><p class="sub">{E(c["q"])} #1–#{len(cur)} are our editorial ranking; "Listed" cards are alphabetical directory listings, not ranked.</p>'
      f'<div class="sc-grid" data-more-grid>{html_}</div><p class="sc-actions"><button class="btn-ghost" data-show-more>Show more ({n-12})</button> <a href="/directory/coding-agents.html">Browse all coding agents in the directory →</a></p></section>')
SC='<!--showcase-->'+''.join(_sc_coding(c) if c['id']=='coding-agents' else _sc(c) for c in cats)+'<!--/showcase-->'
json.dump({slug(t['name']):[PH.pick(c['id'],slug(t['name'])),f'/img/tools/{slug(t["name"])}-logo.webp',PH.cta(slug(t['name']),t['name'],_AFFT.get(slug(t['name'])),'cta-aff sm')] for c in cats for t in c['tools']},open('data/photo-map.json','w'),separators=(',',':'))
json.dump({c['id']:PH.pick(c['id'],c['id']) for c in cats},open('data/cat-photos.json','w'))
_ix=open('index.html').read()
_ix=re.sub(r'<!--showcase-->.*?<!--/showcase-->','',_ix,flags=re.S)
if '<!--/trend-->' in _ix: _ix=_ix.replace('<!--/trend-->','<!--/trend-->'+SC,1)
open('index.html','w').write(_ix)
# photo credits
_rows=''.join(f'<li><a href="/img/photos/{k}-1600.webp">{k}</a>: {E(PH.credit(k))} · <a href="{PH.src_url(k)}" rel="noopener nofollow" target="_blank">source</a> · {"Unsplash License" if k.startswith("u-") else "Pexels License"}</li>' for k in PH.credits_rows())
page('/credits.html',f'Photo credits · {SITE}','Credits and licenses for the stock photography used on VibeStack Rankings.',
 '<h1>Photo credits</h1><p class="sub">Category and blog photos are free-license stock images from <a href="https://unsplash.com/license" rel="noopener nofollow">Unsplash (Unsplash License)</a> and <a href="https://www.pexels.com/license/" rel="noopener nofollow">Pexels (Pexels License)</a>, downloaded and resized locally. Tool logos belong to their respective owners. Where we know the photographer it is named; thank you to all of them.</p><ul>'+_rows+'</ul>')
urls.append('/credits.html')
