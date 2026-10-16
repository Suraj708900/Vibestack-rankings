"""Directory pages: /directory/, /directory/<dept>.html, /t/<slug>.html. Called from build.py with its globals.
Data: data/directory.json (tools verified by curl; descriptions from each site's own meta description)."""
import json,os
import photos as PH

TRANCO='https://tranco-list.eu/list/Y8JGG/1000000'
SRC=lambda u,E:f' <a class="src" href="{E(u)}" target="_blank" rel="nofollow noopener" title="Source: {E(u)}" aria-label="Source">&#8599;</a>' if u else ''
def price_short(t,E):
    p=t.get('pricing')
    if not isinstance(p,dict): return 'Pricing: N/A'
    bits=[]
    if p.get('free_plan')=='yes': bits.append('Free plan')
    if p.get('starting_price'): bits.append('From '+p['starting_price'])
    return E(' · '.join(bits)) if bits else 'Pricing: N/A'
def pop_short(t,E):
    p=t.get('popularity')
    if not isinstance(p,dict): return 'Popularity: N/A'
    if p.get('tranco_rank'): return f'<span title="Rank of {E(p["domain"])} in the Tranco top-1M list {p["list_id"]} (research-grade site ranking, not a visitor count)">Top {p["tranco_rank"]:,} sites (Tranco)</span>'
    return f'<span title="{E(p["domain"])} is not in the Tranco top-1M list {p["list_id"]}">Not in Tranco top 1M</span>'
def badges(t,E): return ''.join(f'<span class="bdg">{E(b)}</span>' for b in t.get('badges',[]))
def meta_html(t,E):
    gh=t.get('github'); st=f' · ★ {gh["stars"]:,}' if gh else ''
    return f'<div class="dmeta">{badges(t,E)}<p class="sub">{price_short(t,E)}</p><p class="sub">{pop_short(t,E)}{st}</p></div>'
def detail_html(t,E):
    p=t.get('pricing'); o='<section class="card dsec"><h2>Pricing</h2>'
    if isinstance(p,dict):
        o+=f'<ul class="kv"><li><b>Free plan:</b> {E(p.get("free_plan","unknown"))}</li>'
        o+=(f'<li><b>Lowest listed paid price:</b> {E(p["starting_price"])} ({E(p["currency"])}, per {E(p["period"])})</li>' if p.get('starting_price') else '<li><b>Starting price:</b> N/A</li>')
        o+=f'<li><b>Pricing page:</b> <a href="{E(p["url"])}" target="_blank" rel="nofollow noopener">{E(p["url"])}</a></li><li class="sub">Read from the pricing page on {E(p["checked"])}; prices change, confirm on the official site.</li></ul>'
    else: o+='<p>N/A</p>'
    o+='</section><section class="card dsec"><h2>Key features</h2>'
    o+=('<ul>'+''.join(f'<li>{E(x)}</li>' for x in t['key_features'])+f'</ul><p class="sub">From the official site{SRC(t.get("key_features_source"),E)}</p>' if t.get('key_features') else '<p>N/A</p>')
    o+='</section><section class="card dsec"><h2>Stats & trust</h2><ul class="kv">'
    ps=t.get('published_stats')
    o+='<li><b>Published by the tool:</b> '+(' · '.join(f'&ldquo;{E(x["text"])}&rdquo;{SRC(x["source"],E)}' for x in ps) if isinstance(ps,list) else 'N/A')+'</li>'
    pp=t.get('popularity')
    o+=f'<li><b>Popularity:</b> {pop_short(t,E)} <a class="src" href="{TRANCO}" target="_blank" rel="noopener" title="About the Tranco list">&#9432;</a></li>' if isinstance(pp,dict) else '<li><b>Popularity:</b> N/A</li>'
    gh=t.get('github')
    if gh: o+=f'<li><b>GitHub:</b> ★ {gh["stars"]:,} stars · last updated {E(gh["last_push"])}'+(f' · license {E(gh["license"])}' if gh.get('license') and gh['license']!='NOASSERTION' else '')+f'{SRC(gh["repo"],E)}</li>'
    o+=f'<li class="vline" data-slug="{E(t["slug"])}" hidden></li>'
    o+='</ul>'+(f'<p>{badges(t,E)}</p>' if t.get('badges') else '')+'<p class="sub">Listing stats come from each tool&rsquo;s own website, GitHub and the public Tranco list; we do not estimate traffic.</p></section>'
    return o
VOTEJS='<script>(function(){var l=document.querySelector(".vline");if(!l)return;fetch("/api/stats?days=30").then(function(r){return r.json()}).then(function(d){var v=d.votes&&d.votes[l.dataset.slug];if(v&&(v.up+v.down)>0){l.innerHTML="<b>Reader votes (30 days):</b> "+v.up+" of "+(v.up+v.down)+" found it helpful";l.hidden=false}}).catch(function(){})})()</script>'
def run(g):
    E,page,urls,BASE,SITE=g['E'],g['page'],g['urls'],g['BASE'],g['SITE']
    D=json.load(open('data/directory.json')); DN=D['departments']; T=D['tools']
    A=json.load(open('affiliates.json'))['tools']
    # /go/ fallback data (affiliates.json still wins in api/go.js)
    AL=D.get('aliases',{}); U={t['slug']:t['url'] for t in T}
    json.dump({**{a:U[b] for a,b in AL.items() if b in U},**U},open('data/go-directory.json','w'),separators=(',',':'))
    json.dump([[t['name'],t['slug'],t['department'],t['description'][:160],t['logo'],PH.pick(t['department'],t['slug']),1 if PH.offer(A.get(t['slug'])) else 0,meta_html(t,g['E'])] for t in T],open('data/directory-index.json','w'),separators=(',',':'),ensure_ascii=False)
    by={}
    for t in T: by.setdefault(t['department'],[]).append(t)
    order=sorted(by,key=lambda k:-len(by[k]))
    CSS='<style>.dmeta{margin:.4em 0}.dmeta p{margin:.15em 0;font-size:.82em}.bdg{display:inline-block;font-size:.72em;padding:2px 8px;margin:0 4px 4px 0;border-radius:99px;border:1px solid #7c5cff66;background:#7c5cff1a}.dsec{margin-top:14px}.dsec ul{padding-left:1.1em}.kv{list-style:none;padding-left:0!important}.kv li{margin:.35em 0;overflow-wrap:anywhere}a.src{text-decoration:none;opacity:.6;font-size:.85em}a.src:hover{opacity:1}@media(max-width:600px){.dsec{padding:12px}}.dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}.dcard{display:flex;gap:12px;align-items:flex-start;text-decoration:none;color:inherit}.dcard img{border-radius:8px;flex:none}.dcard p{margin:.3em 0 0;font-size:.9em}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.chips a,.chips button{padding:4px 10px;border:1px solid #333a4d;border-radius:99px;background:none;color:inherit;cursor:pointer;font:inherit;text-decoration:none}.chips .on{border-color:#7c5cff;background:#7c5cff33}</style>'
    def card(t): return (f'<article class="card sc-card dcard2">'+PH.banner(t['department'],t['slug'],t['logo'],t['name'])
                         +f'<div class="sc-body"><h3><a href="/t/{t["slug"]}.html">{E(t["name"])}</a></h3><p class="sub l1">{E(t["description"][:140])}</p>{meta_html(t,E)}{PH.cta(t["slug"],t["name"],A.get(t["slug"]),"cta-aff sm")}</div></article>')
    chips=lambda cur:'<nav class="chips" aria-label="Departments"><a href="/directory/"'+(' class="on"' if cur is None else '')+'>All</a>'+''.join(f'<a href="/directory/{k}.html"'+(' class="on"' if k==cur else '')+f'>{E(DN[k])} ({len(by[k])})</a>' for k in order)+'</nav>'
    # browse page (client-side filter/search/pagination over data/directory-index.json)
    js='''<script>(function(){var D=[],dep="",q="",n=48,DN=%s,g=document.getElementById("dg"),m=document.getElementById("dm"),i=document.getElementById("dq"),f=document.getElementById("df");
function H(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function R(){var L=D.filter(function(t){return(!dep||t[2]==dep)&&(!q||(t[0]+" "+t[3]+" "+DN[t[2]]).toLowerCase().indexOf(q)>=0)});
g.innerHTML=L.slice(0,n).map(function(t){return'<article class="card sc-card dcard2"><div class="ph"><picture><source type="image/webp" srcset="/img/photos/'+t[5]+'-480.webp 480w, /img/photos/'+t[5]+'-960.webp 960w" sizes="(max-width:600px) 100vw, 480px"><img class="ph-img" src="/img/photos/'+t[5]+'-480.webp" width="960" height="540" alt="" loading="lazy" decoding="async"></picture><span class="ph-ov"></span><img class="ph-logo" src="'+t[4]+'" width="56" height="56" alt="'+H(t[0])+' logo" loading="lazy"></div><div class="sc-body"><h3><a href="/t/'+t[1]+'.html">'+H(t[0])+'</a></h3><p class="sub l1">'+H(t[3])+'</p><a class="cta-aff sm" href="/go/'+t[1]+'" data-tool="'+t[1]+'" target="_blank" rel="sponsored nofollow noopener">'+(t[6]?'Get Deal →':'Visit Official Site →')+'</a></div></article>'}).join("");
m.style.display=L.length>n?"":"none";document.getElementById("dc").textContent=L.length+" tools"}
i.oninput=function(){q=i.value.trim().toLowerCase();n=48;R()};f.onchange=function(){dep=f.value;n=48;R()};m.onclick=function(){n+=48;R()};
var p=new URLSearchParams(location.search);if(p.get("q")){i.value=p.get("q");q=i.value.toLowerCase()}if(p.get("d")){f.value=p.get("d");dep=f.value}
fetch("/data/directory-index.json").then(function(r){return r.json()}).then(function(j){D=j;R()})})()</script>'''%json.dumps(DN)
    opts=''.join(f'<option value="{k}">{E(DN[k])} ({len(by[k])})</option>' for k in order)
    body=(CSS+f'<p class="sub"><a href="/">Rankings</a> › Directory</p><h1>AI tool directory: {len(T)} tools by department</h1>'
      f'<p class="sub">Every listing links to a verified, live official site (checked {D["updated"]}). Descriptions come from each tool\'s own site. Looking for opinionated picks? See our <a href="/">curated rankings</a>.</p>'
      +chips(None)+f'<div class="bar"><input id="dq" type="search" placeholder="Search {len(T)} AI tools…" aria-label="Search tools"><select id="df" aria-label="Department"><option value="">All departments</option>{opts}</select> <span id="dc" class="sub" style="align-self:center"></span></div>'
      +'<div class="sc-grid" id="dg">'+''.join(card(t) for t in T[:48])+'</div><p style="text-align:center"><button id="dm">Load more</button></p>'+js)
    page('/directory/',f'AI tool directory: {len(T)} AI tools by department · {SITE}',f'Browse {len(T)} AI tools across {len(by)} departments: coding agents, app builders, hosting, image, video, voice, writing and more. Verified official links.',body); urls.append('/directory/')
    for k in order:
        L=by[k]; path=f'/directory/{k}.html'; urls.append(path)
        il={"@context":"https://schema.org","@type":"ItemList","name":DN[k],"itemListElement":[{"@type":"ListItem","position":i+1,"name":t['name'],"url":BASE+f'/t/{t["slug"]}.html'} for i,t in enumerate(L)]}
        extra=' <a href="/hosting/hostinger.html">Hostinger overview</a>.' if k=='hosting' else ''
        page(path,f'{DN[k]} AI tools ({len(L)}) · {SITE}',f'{len(L)} {DN[k].lower()} tools with verified official links: '+', '.join(t['name'] for t in L[:6])+'…',
             CSS+f'<p class="sub"><a href="/directory/">Directory</a> › {E(DN[k])}</p><h1>{E(DN[k])} ({len(L)})</h1>'+chips(k)+(f'<p class="sub">{extra}</p>' if extra else '')+'<div class="sc-grid">'+''.join(card(t) for t in L)+'</div>'+g['ld'](il))
    for t in T:
        s=t['slug']; path=f'/t/{s}.html'; urls.append(path); a=A.get(s,{})
        code=a.get('discount_code') if a.get('status')=='active' and a.get('discount_code') else ''
        price=t.get('pricing','')
        rel=[x for x in by[t['department']] if x['slug']!=s][:6]
        body=(CSS+f'<p class="sub"><a href="/directory/">Directory</a> › <a href="/directory/{t["department"]}.html">{E(DN[t["department"]])}</a></p>'
          +'<section class="tool-hero card">'+PH.banner(t['department'],s,t['logo'],t['name'],eager=True,sizes='(max-width:900px) 100vw, 1100px')+f'<div class="tool-hero-body"><h1>{E(t["name"])}</h1>'
          f'<p>{E(t["description"])}</p><p class="sub">Source: {E(t["description_source"])}. Link verified live on {t["verified"]}.</p>'+PH.cta(s,t['name'],a)+'</div></section>'
          +(f'<p><b>Our full review:</b> <a href="{t["curated_page"]}">{E(t["name"])} ranking & verdict</a></p>' if t['curated_page'] else '')
          +detail_html(t,E)+PH.dealbox(s,t['name'],a)
          +('<h2>More in '+E(DN[t['department']])+'</h2><div class="sc-grid">'+''.join(card(x) for x in rel)+'</div>' if rel else ''))
        ld_={"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"description":t['description'],"applicationCategory":DN[t['department']]}
        page(path,f'{t["name"]}: {DN[t["department"]]} AI tool · {SITE}',t['description'][:155],body+PH.sticky(s,t['name'],a)+VOTEJS+g['ld'](ld_))
    for a,b in AL.items():  # merged duplicates: keep old URLs working
        if b in U:
            os.makedirs('t',exist_ok=True)
            open(f't/{a}.html','w').write(f'<!doctype html><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}/t/{b}.html"><meta http-equiv="refresh" content="0;url=/t/{b}.html"><a href="/t/{b}.html">Moved here</a>')
    hosting(g)
def hosting(g):
    p='hosting_build.py'
    if os.path.exists(p): exec(open(p).read(),{'g':g})
