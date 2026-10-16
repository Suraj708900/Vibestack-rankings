"""Directory pages: /directory/, /directory/<dept>.html, /t/<slug>.html. Called from build.py with its globals.
Data: data/directory.json (tools verified by curl; descriptions from each site's own meta description)."""
import json,os
import photos as PH
def run(g):
    E,page,urls,BASE,SITE=g['E'],g['page'],g['urls'],g['BASE'],g['SITE']
    D=json.load(open('data/directory.json')); DN=D['departments']; T=D['tools']
    A=json.load(open('affiliates.json'))['tools']
    # /go/ fallback data (affiliates.json still wins in api/go.js)
    AL=D.get('aliases',{}); U={t['slug']:t['url'] for t in T}
    json.dump({**{a:U[b] for a,b in AL.items() if b in U},**U},open('data/go-directory.json','w'),separators=(',',':'))
    json.dump([[t['name'],t['slug'],t['department'],t['description'][:160],t['logo'],PH.pick(t['department'],t['slug']),1 if PH.offer(A.get(t['slug'])) else 0] for t in T],open('data/directory-index.json','w'),separators=(',',':'),ensure_ascii=False)
    by={}
    for t in T: by.setdefault(t['department'],[]).append(t)
    order=sorted(by,key=lambda k:-len(by[k]))
    CSS='<style>.dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}.dcard{display:flex;gap:12px;align-items:flex-start;text-decoration:none;color:inherit}.dcard img{border-radius:8px;flex:none}.dcard p{margin:.3em 0 0;font-size:.9em}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.chips a,.chips button{padding:4px 10px;border:1px solid #333a4d;border-radius:99px;background:none;color:inherit;cursor:pointer;font:inherit;text-decoration:none}.chips .on{border-color:#7c5cff;background:#7c5cff33}</style>'
    def card(t): return (f'<article class="card sc-card dcard2">'+PH.banner(t['department'],t['slug'],t['logo'],t['name'])
                         +f'<div class="sc-body"><h3><a href="/t/{t["slug"]}.html">{E(t["name"])}</a></h3><p class="sub l1">{E(t["description"][:140])}</p>{PH.cta(t["slug"],t["name"],A.get(t["slug"]),"cta-aff sm")}</div></article>')
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
          +'<div class="card" style="margin-top:14px"><h2>Pricing & deals</h2>'
          +(f'<p>{E(price)}</p>' if price else '<p>Pricing not yet verified by us. Check the official site for current plans and any free tier.</p>')
          +'</div>'+PH.dealbox(s,t['name'],a)
          +('<h2>More in '+E(DN[t['department']])+'</h2><div class="sc-grid">'+''.join(card(x) for x in rel)+'</div>' if rel else ''))
        ld_={"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"description":t['description'],"applicationCategory":DN[t['department']]}
        page(path,f'{t["name"]}: {DN[t["department"]]} AI tool · {SITE}',t['description'][:155],body+PH.sticky(s,t['name'],a)+g['ld'](ld_))
    for a,b in AL.items():  # merged duplicates: keep old URLs working
        if b in U:
            os.makedirs('t',exist_ok=True)
            open(f't/{a}.html','w').write(f'<!doctype html><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}/t/{b}.html"><meta http-equiv="refresh" content="0;url=/t/{b}.html"><a href="/t/{b}.html">Moved here</a>')
    hosting(g)
def hosting(g):
    p='hosting_build.py'
    if os.path.exists(p): exec(open(p).read(),{'g':g})
