# /products page + homepage teaser for Suraj's own paid offerings (UPI / PayPal checkout via /checkout.html; prices in data/products-config.json).
_PCF=json.load(open(os.path.join(ROOT,'data','products-config.json')))['products']
P_LIST=[(k,v['name'],v.get('cover','c-'+k),v['price'],v['price'],v.get('unit',''),v.get('tagline',''),v.get('description','')) for k,v in _PCF.items()]
_inr=lambda n:'₹'+format(n,',')
_wa=(json.load(open(os.path.join(ROOT,'data','products-config.json'))).get('whatsapp') or '').strip()
_wa=re.sub(r'\D','',_wa)
_PC=json.load(open(os.path.join(ROOT,'data','products-config.json')))['products']
_usd=lambda v:'$'+(f'{v:,.2f}'.rstrip('0').rstrip('.') if v%1 else f'{int(v):,}')
def _price(p):
    c=_PC[p[0]]; u=f' {c["unit"]}' if c.get('unit') else ''
    return f'{_inr(c["price"])}{u} <span class="sub">· {_usd(c["price_usd"])} USD via PayPal</span>'
def _pcard(p,eager=False):
    wa=(f' <a class="btn-ghost p-wa" href="https://wa.me/{_wa}?text={urllib.parse.quote("Hi, I am interested in "+p[1])}" target="_blank" rel="noopener">Ask on WhatsApp</a>' if _wa else '')
    return (f'<article class="card sc-card p-card" id="{p[0]}"><div class="ph">{_PH.picture(p[2],p[1],eager)}<span class="ph-ov"></span><span class="rank-badge listed">Paid</span></div>'
      f'<div class="sc-body"><h3>{E(p[1])}</h3><p class="p-hi" >{E(p[6])}</p><p class="p-price">{_price(p)}</p><p class="sub">{E(p[7])}</p>'
      f'<p class="sub p-incl">Paid product · guide book included</p>'
      f'<p class="p-cta p-pay"><a class="cta-aff sm" href="/checkout.html?p={p[0]}&amp;m=upi">Buy now — {_inr(_PC[p[0]]["price"])} · Pay with UPI</a> <a class="btn-ghost p-pp" href="/checkout.html?p={p[0]}&amp;m=paypal">Pay with PayPal — {_usd(_PC[p[0]]["price_usd"])} USD</a>{wa}</p></div></article>')
_LD=ld({'@context':'https://schema.org','@graph':[{'@type':'Product','name':p[1],'description':p[7],'image':BASE+f'/img/photos/{p[2]}-1600.webp','url':BASE+f'/products.html#{p[0]}','brand':{'@type':'Brand','name':SITE},
  'offers':{'@type':'Offer','priceCurrency':'INR','price':_PC[p[0]]['price'],'availability':'https://schema.org/InStock','url':BASE+f'/checkout.html?p={p[0]}'}} for p in P_LIST]})

# ---- AI Free / AI Plus tool sections (verified pricing only) ----
import directory_build as _DB
_DD=json.load(open('data/directory.json')); _DN=_DD['departments']; _DT={t['slug']:t for t in _DD['tools']}
_TDET=json.load(open('tool_details.json'))
_CATDEP={'coding-agents':'coding-agents','app-builders':'app-builders','databases':'databases-backend','hosting':'hosting','ai-apis':'ai-apis-models','agent-frameworks':'automation-agents','video':'video','voice':'audio-voice'}
_CUR={}
for _c in cats:
    for _t in _c['tools']:
        _s=slug(_t['name']); _CUR.setdefault(_s,(_t,_c['id']))
def _cur_free(s):
    v=(_TDET.get(s) or {}).get('free_plan','')
    if not v.lower().startswith('yes'): return None if not v.lower().startswith('no') else False
    if re.search(r'credit',v,re.I) and not re.search(r'plan|tier|open source|forever',v,re.I): return None  # trial credits only
    return True
_FREE=[];_PLUS=[];_SKIP=[]
for s in sorted(set(_DT)|set(_CUR)):
    t=_DT.get(s); p=(t or {}).get('pricing'); p=p if isinstance(p,dict) else {}
    cf=_cur_free(s) if s in _CUR else None
    if cf is False and p.get('free_plan')=='yes': _SKIP.append(s); continue  # conflicting sources
    if p.get('free_plan')=='yes' or cf is True: _FREE.append(s)
    elif p.get('starting_price') and cf is not True and not ((_TDET.get(s) or {}).get('free_plan','').lower().startswith('yes')): _PLUS.append(s)
def _tcard(s,hide):
    t=_DT.get(s)
    if t: name,dep,logo,desc,href=t['name'],t['department'],t['logo'],t['description'],f'/t/{s}.html'
    else:
        ct,cid=_CUR[s]; name,dep,logo,desc,href=ct['name'],_CATDEP.get(cid,'ai-apis-models'),f'/img/tools/{s}-logo.webp',ct.get('verdict',''),f'/tools/{s}.html'
    if s in _CUR and t: href=f'/t/{s}.html'
    pr=_DB.price_short(t,E) if t else 'Pricing: N/A'
    if s in _FREE and 'Free plan' not in pr: pr=('Free plan · '+pr) if pr!='Pricing: N/A' else 'Free plan'
    return (f'<article class="card sc-card dcard2 pt-card{" sc-more" if hide else ""}" data-dep="{dep}">'+_PH.banner(dep,s,logo,name)
      +f'<div class="sc-body"><h3><a href="{href}">{E(name)}</a></h3><p class="sub l1">{E(desc[:140])}</p><p class="p-price sm">{pr}</p>{_PH.cta(s,name,_AFFT.get(s),"cta-aff sm")}</div></article>')
def _tsec(id_,title,lead,L):
    deps={}
    for s in L: d=(_DT.get(s) or {}).get('department') or _CATDEP.get(_CUR[s][1],'ai-apis-models'); deps[d]=deps.get(d,0)+1
    chips='<nav class="chips pt-chips" aria-label="Departments"><button class="on" data-dep="">All ('+str(len(L))+')</button>'+''.join(f'<button data-dep="{k}">{E(_DN.get(k,k))} ({n})</button>' for k,n in sorted(deps.items(),key=lambda x:-x[1]))+'</nav>'
    return (f'<section class="pt-sec" id="{id_}"><h2>{title}</h2><p class="sub">{lead}</p>{chips}<div class="sc-grid pt-grid">'+''.join(_tcard(s,i>=24) for i,s in enumerate(L))
      +f'</div><p class="sc-actions"><button class="btn-ghost pt-more">Show more</button></p></section>')
_TOOLSEC=('<section class="pt-wrap"><div class="pt-tabs" role="tablist"><a href="#ai-free" class="on" data-tab="ai-free" role="tab">AI Free <span class="tag">'+str(len(_FREE))+'</span></a><a href="#ai-plus" data-tab="ai-plus" role="tab">AI Plus <span class="tag">'+str(len(_PLUS))+'</span></a></div>'
 '<p class="sub">Third-party AI tools from our directory, grouped by pricing we verified on each tool\'s official pricing page. Tools with unknown pricing are not listed here. Prices change: always check the official site.</p>'
 +_tsec('ai-free','AI Free: tools with a free plan','A free plan was found on the official pricing page (paid upgrades may exist).',_FREE)
 +_tsec('ai-plus','AI Plus: paid AI tools','A paid starting price was found and no free plan was detected on the official pricing page.',_PLUS)+'</section>')
_TJS=r"""<script>(function(){var secs=document.querySelectorAll('.pt-sec');function apply(sec){var d=sec.dataset.dep||'',lim=+(sec.dataset.lim||24),n=0,tot=0;sec.querySelectorAll('.pt-card').forEach(function(c){var ok=!d||c.dataset.dep===d;if(ok)tot++;var show=ok&&n<lim;if(show)n++;c.classList.toggle('sc-more',!show);c.style.display=show?'':'none'});var b=sec.querySelector('.pt-more');b.style.display=tot>n?'':'none';b.textContent='Show more ('+(tot-n)+')'}
secs.forEach(function(sec){sec.querySelectorAll('.pt-chips button').forEach(function(b){b.onclick=function(){sec.querySelectorAll('.pt-chips button').forEach(function(x){x.classList.toggle('on',x===b)});sec.dataset.dep=b.dataset.dep;sec.dataset.lim=24;apply(sec)}});sec.querySelector('.pt-more').onclick=function(){sec.dataset.lim=(+(sec.dataset.lim||24))+24;apply(sec)};apply(sec)});
function tab(){var h=location.hash==='#ai-plus'?'ai-plus':'ai-free';document.querySelectorAll('.pt-tabs a').forEach(function(a){a.classList.toggle('on',a.dataset.tab===h)})}window.addEventListener('hashchange',tab);tab()})();</script>"""

page('/products.html',f'AI Products by Suraj Kamdev · {SITE}','AI learning kits, business toolkits, prompt libraries, live training and AI receptionist setup. Pay by UPI or PayPal; guide book included.',
 '<section class="p-hero"><h1>AI products for learners and small businesses</h1><p class="p-hi">Practical AI tools and training, in plain English.</p>'
 '<p class="sub">Our own products, built by Suraj Kamdev. All products are paid; each includes its guide book. Pay by UPI (India) or PayPal (international), then submit your transaction ID and we email your download link after confirming the payment.</p></section>'
 '<div class="sc-grid p-grid">'+''.join(_pcard(p,i<2) for i,p in enumerate(P_LIST))+'</div>'+_TOOLSEC+_TJS,extra=_LD)
print('products: AI Free',len(_FREE),'AI Plus',len(_PLUS),'skipped-conflict',_SKIP)
urls.append('/products.html')
_TZ=('<!--products--><section class="showcase p-teaser"><h2>Our own AI products <span class="tag">Paid</span></h2><p class="sub">AI kits, toolkits and guides from Suraj Kamdev. Pay by UPI or PayPal; guide book included.</p><div class="sc-grid">'
 +''.join(f'<article class="card sc-card p-card">{_PH.picture(p[2],p[1])}<div class="sc-body"><h3><a href="/products.html#{p[0]}">{E(p[1])}</a></h3><p class="p-price">{_price(p)}</p><p class="sub l1">{E(p[7])}</p></div></article>' for p in P_LIST[:4])
 +f'</div><p class="sc-actions"><a class="cta-aff sm" href="/products.html">See all {len(P_LIST)} products →</a></p></section><!--/products-->')
_ix=open('index.html').read(); _ix=re.sub(r'<!--products-->.*?<!--/products-->','',_ix,flags=re.S)
if '<!--/showcase-->' in _ix: _ix=_ix.replace('<!--/showcase-->','<!--/showcase-->'+_TZ,1)
open('index.html','w').write(_ix)

# ---- pricing pills map (verified data only) + /go/<slug>?to=pricing whitelist ----
_PM={};_GP={}
for s_ in sorted(set(_DT)|set(_CUR)):
    t=_DT.get(s_); p=(t or {}).get('pricing'); p=p if isinstance(p,dict) else {}
    det=_TDET.get(s_) or {}
    purl=p.get('url') or next((u for u in det.get('source',[]) if 'pricing' in u.lower()),'')
    cf=_cur_free(s_) if s_ in _CUR else None
    free=1 if (s_ in _FREE) else (0 if (s_ in _PLUS or cf is False) else None)
    price=p.get('starting_price','') if s_!='anthropic-api' else ''
    paid=1 if price else None
    if free is None and paid is None and not purl: continue
    if purl.startswith('https://'): _GP[s_]=purl
    _PM[s_]=[free,paid,re.sub(r'\s+',' ',price).strip()[:28],1 if s_ in _GP else 0]
json.dump(_PM,open('data/pricing-map.json','w'),separators=(',',':'),ensure_ascii=False)
json.dump(_GP,open('data/go-pricing.json','w'),separators=(',',':'))
print('pricing-map',len(_PM),'pricing urls',len(_GP))
