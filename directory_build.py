"""Directory pages: /directory/, /directory/<dept>.html, /t/<slug>.html. Called from build.py with its globals.
Data: data/directory.json (tools verified by curl; descriptions from each site's own meta description)."""
import json,os
def run(g):
    E,page,urls,BASE,SITE=g['E'],g['page'],g['urls'],g['BASE'],g['SITE']
    D=json.load(open('data/directory.json')); DN=D['departments']; T=D['tools']
    A=json.load(open('affiliates.json'))['tools']
    # /go/ fallback data (affiliates.json still wins in api/go.js)
    json.dump({t['slug']:t['url'] for t in T},open('data/go-directory.json','w'),separators=(',',':'))
    json.dump([[t['name'],t['slug'],t['department'],t['description'][:160],t['logo']] for t in T],open('data/directory-index.json','w'),separators=(',',':'),ensure_ascii=False)
    by={}
    for t in T: by.setdefault(t['department'],[]).append(t)
    order=sorted(by,key=lambda k:-len(by[k]))
    CSS='<style>.dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}.dcard{display:flex;gap:12px;align-items:flex-start;text-decoration:none;color:inherit}.dcard img{border-radius:8px;flex:none}.dcard p{margin:.3em 0 0;font-size:.9em}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.chips a,.chips button{padding:4px 10px;border:1px solid #333a4d;border-radius:99px;background:none;color:inherit;cursor:pointer;font:inherit;text-decoration:none}.chips .on{border-color:#7c5cff;background:#7c5cff33}.shot{width:100%;max-width:640px;height:auto;border-radius:12px;border:1px solid #222838}</style>'
    def card(t): return (f'<a class="card dcard" href="/t/{t["slug"]}.html"><img src="{t["logo"]}" width="40" height="40" alt="" loading="lazy" decoding="async">'
                         f'<span><b>{E(t["name"])}</b><p class="sub">{E(t["description"][:140])}</p></span></a>')
    chips=lambda cur:'<nav class="chips" aria-label="Departments"><a href="/directory/"'+(' class="on"' if cur is None else '')+'>All</a>'+''.join(f'<a href="/directory/{k}.html"'+(' class="on"' if k==cur else '')+f'>{E(DN[k])} ({len(by[k])})</a>' for k in order)+'</nav>'
    # browse page (client-side filter/search/pagination over data/directory-index.json)
    js='''<script>(function(){var D=[],dep="",q="",n=48,DN=%s,g=document.getElementById("dg"),m=document.getElementById("dm"),i=document.getElementById("dq"),f=document.getElementById("df");
function H(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function R(){var L=D.filter(function(t){return(!dep||t[2]==dep)&&(!q||(t[0]+" "+t[3]+" "+DN[t[2]]).toLowerCase().indexOf(q)>=0)});
g.innerHTML=L.slice(0,n).map(function(t){return'<a class="card dcard" href="/t/'+t[1]+'.html"><img src="'+t[4]+'" width="40" height="40" alt="" loading="lazy" decoding="async"><span><b>'+H(t[0])+'</b><p class="sub">'+H(t[3])+'</p></span></a>'}).join("");
m.style.display=L.length>n?"":"none";document.getElementById("dc").textContent=L.length+" tools"}
i.oninput=function(){q=i.value.trim().toLowerCase();n=48;R()};f.onchange=function(){dep=f.value;n=48;R()};m.onclick=function(){n+=48;R()};
var p=new URLSearchParams(location.search);if(p.get("q")){i.value=p.get("q");q=i.value.toLowerCase()}if(p.get("d")){f.value=p.get("d");dep=f.value}
fetch("/data/directory-index.json").then(function(r){return r.json()}).then(function(j){D=j;R()})})()</script>'''%json.dumps(DN)
    opts=''.join(f'<option value="{k}">{E(DN[k])} ({len(by[k])})</option>' for k in order)
    body=(CSS+f'<p class="sub"><a href="/">Rankings</a> › Directory</p><h1>AI tool directory: {len(T)} tools by department</h1>'
      f'<p class="sub">Every listing links to a verified, live official site (checked {D["updated"]}). Descriptions come from each tool\'s own site. Looking for opinionated picks? See our <a href="/">curated rankings</a>.</p>'
      +chips(None)+f'<div class="bar"><input id="dq" type="search" placeholder="Search {len(T)} AI tools…" aria-label="Search tools"><select id="df" aria-label="Department"><option value="">All departments</option>{opts}</select> <span id="dc" class="sub" style="align-self:center"></span></div>'
      +'<div class="dgrid" id="dg">'+''.join(card(t) for t in T[:48])+'</div><p style="text-align:center"><button id="dm">Load more</button></p>'+js)
    page('/directory/',f'AI tool directory: {len(T)} AI tools by department · {SITE}',f'Browse {len(T)} AI tools across {len(by)} departments: coding agents, app builders, hosting, image, video, voice, writing and more. Verified official links.',body); urls.append('/directory/')
    for k in order:
        L=by[k]; path=f'/directory/{k}.html'; urls.append(path)
        il={"@context":"https://schema.org","@type":"ItemList","name":DN[k],"itemListElement":[{"@type":"ListItem","position":i+1,"name":t['name'],"url":BASE+f'/t/{t["slug"]}.html'} for i,t in enumerate(L)]}
        extra=' <a href="/hosting/hostinger.html">Hostinger overview</a>.' if k=='hosting' else ''
        page(path,f'{DN[k]} AI tools ({len(L)}) · {SITE}',f'{len(L)} {DN[k].lower()} tools with verified official links: '+', '.join(t['name'] for t in L[:6])+'…',
             CSS+f'<p class="sub"><a href="/directory/">Directory</a> › {E(DN[k])}</p><h1>{E(DN[k])} ({len(L)})</h1>'+chips(k)+(f'<p class="sub">{extra}</p>' if extra else '')+'<div class="dgrid">'+''.join(card(t) for t in L)+'</div>'+g['ld'](il))
    for t in T:
        s=t['slug']; path=f'/t/{s}.html'; urls.append(path); a=A.get(s,{})
        code=a.get('discount_code') if a.get('status')=='active' and a.get('discount_code') else ''
        price=t.get('pricing','')
        rel=[x for x in by[t['department']] if x['slug']!=s][:6]
        body=(CSS+f'<p class="sub"><a href="/directory/">Directory</a> › <a href="/directory/{t["department"]}.html">{E(DN[t["department"]])}</a></p>'
          f'<h1><img src="{t["logo"]}" width="48" height="48" alt="{E(t["name"])} logo" style="vertical-align:middle;border-radius:10px;margin-right:10px">{E(t["name"])}</h1>'
          f'<p>{E(t["description"])}</p><p class="sub">Source: {E(t["description_source"])}. Link verified live on {t["verified"]}.</p>'
          f'<p><a class="btn" href="/go/{s}" data-tool="{s}" target="_blank" rel="sponsored nofollow noopener">Visit {E(t["name"])} ↗</a></p>'
          +(f'<p><b>Our full review:</b> <a href="{t["curated_page"]}">{E(t["name"])} ranking & verdict</a></p>' if t['curated_page'] else '')
          +(f'<img class="shot" src="{t["screenshot"]}" alt="{E(t["name"])} preview image" loading="lazy" decoding="async">' if t['screenshot'] else '')
          +'<div class="card" style="margin-top:14px"><h2>Pricing & deals</h2>'
          +(f'<p>{E(price)}</p>' if price else '<p>Pricing not yet verified by us. Check the official site for current plans and any free tier.</p>')
          +(f'<p>Promo code: <code>{E(code)}</code></p>' if code else '<p>Verified code not available yet.</p>')+'</div>'
          +('<h2>More in '+E(DN[t['department']])+'</h2><div class="dgrid">'+''.join(card(x) for x in rel)+'</div>' if rel else ''))
        ld_={"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"description":t['description'],"applicationCategory":DN[t['department']]}
        page(path,f'{t["name"]}: {DN[t["department"]]} AI tool · {SITE}',t['description'][:155],body+g['ld'](ld_))
    hosting(g)
def hosting(g):
    p='hosting_build.py'
    if os.path.exists(p): exec(open(p).read(),{'g':g})
