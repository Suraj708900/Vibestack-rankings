# /products page + homepage teaser for Suraj's own offerings (pre-launch waitlist; no payments, no reviews).
P_LIST=[
 ('ai-learning-kit','AI Learning Kit','p-4050315',199,999,'','AI सीखें, अपनी भाषा में','Hindi & English AI learning PDFs, videos, ready prompts and practical examples. Separate kits for students, job seekers and small business owners.'),
 ('ai-business-toolkit','AI Business Toolkit','p-6693655',499,1999,'','दुकान और बिज़नेस के लिए AI','WhatsApp reply templates, marketing prompts, quotation templates and customer follow-up systems for shops, clinics, salons and restaurants.'),
 ('ai-prompt-library','AI Prompt Library','p-1181244',99,499,'','1,000 तक काम के prompts','500–1,000 useful prompts across jobs, study, marketing, business and content.'),
 ('live-ai-training','Live AI Training','p-4144923',299,2999,' per person','लाइव सीखें, Google Meet पर','Live Google Meet sessions, for example “Learn to use AI in your business in 2 hours”.'),
 ('ai-receptionist-setup','AI Receptionist Setup','p-8867482',3000,15000,'+','आपके बिज़नेस का 24×7 AI रिसेप्शनिस्ट','Website chatbot, customer FAQ, lead collection and automated replies, set up for you. Optional monthly maintenance.'),
 ('ai-knowledge-membership','AI Knowledge Membership','p-3756679',99,499,'/month','हर हफ्ते नए AI टूल्स और ट्यूटोरियल','Weekly new AI tools, tutorials, templates and updates.'),
 ('industry-ai-kits','Industry-Specific AI Kits','p-3184465',999,4999,'','आपके पेशे के लिए तैयार AI वर्कफ़्लो','Ready-to-use AI workflow kits for doctors, real-estate agents, teachers, shopkeepers and agencies.'),
]
_inr=lambda n:'₹'+format(n,',')
_wa=(json.load(open(os.path.join(ROOT,'data','products-config.json'))).get('whatsapp') or '').strip()
_wa=re.sub(r'\D','',_wa)
def _price(p): return f'{_inr(p[3])}–{_inr(p[4])}{p[5]}'
def _pcard(p,eager=False):
    wa=(f' <a class="btn-ghost p-wa" href="https://wa.me/{_wa}?text={urllib.parse.quote("Hi, I am interested in "+p[1])}" target="_blank" rel="noopener">Ask on WhatsApp</a>' if _wa else '')
    return (f'<article class="card sc-card p-card" id="{p[0]}"><div class="ph">{_PH.picture(p[2],p[1],eager)}<span class="ph-ov"></span><span class="rank-badge listed">Launching soon</span></div>'
      f'<div class="sc-body"><h3>{E(p[1])}</h3><p class="p-hi" lang="hi">{E(p[6])}</p><p class="p-price">{_price(p)} <span class="sub">indicative</span></p><p class="sub">{E(p[7])}</p>'
      f'<p class="p-cta"><a class="cta-aff sm" href="/products.html#waitlist" data-product="{p[0]}">Join waitlist / Get early access →</a>{wa}</p></div></article>')
_opts=''.join(f'<option value="{p[0]}">{E(p[1])}</option>' for p in P_LIST)
_FORM=(f'<section class="card p-form" id="waitlist"><h2>Join the waitlist</h2><p class="sub">Get early access and launch pricing first. <span lang="hi">लॉन्च होते ही आपको सबसे पहले बताएंगे।</span> No payment now. We only use this to contact you about the product you pick.</p>'
 f'<form id="pf" novalidate><label>Product<select name="product" required>{_opts}</select></label><label>Name<input name="name" required maxlength="80" autocomplete="name"></label>'
 '<label>Email<input type="email" name="email" required maxlength="254" autocomplete="email"></label><label>WhatsApp (optional)<input name="whatsapp" inputmode="tel" maxlength="20" placeholder="+91…" autocomplete="tel"></label>'
 '<input name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">'
 '<label class="p-consent"><input type="checkbox" name="consent" required> I agree to be contacted about this product (see <a href="/privacy">Privacy</a>).</label>'
 '<button type="submit" class="cta-aff">Get early access</button><p id="pmsg" class="sub" role="status"></p></form></section>')
_JS='''<script>(function(){var f=document.getElementById('pf');if(!f)return;var m=document.getElementById('pmsg');
document.querySelectorAll('[data-product]').forEach(function(a){a.addEventListener('click',function(){f.product.value=a.getAttribute('data-product');setTimeout(function(){f.name.focus()},300)})});
var h=location.hash.slice(1);if(h&&f.product.querySelector('option[value="'+h+'"]'))f.product.value=h;
f.addEventListener('submit',function(e){e.preventDefault();if(!f.reportValidity())return;var b=f.querySelector('button');b.disabled=true;m.textContent='Saving…';
fetch('/api/interest',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:f.product.value,name:f.name.value,email:f.email.value,whatsapp:f.whatsapp.value,company:f.company.value,consent:f.consent.checked})})
.then(function(r){return r.json().then(function(j){return[r.ok,j]})}).then(function(x){if(x[0]){m.textContent='Thanks! You are on the waitlist. धन्यवाद!';f.reset()}else{m.textContent=x[1].error||'Could not save, please try again.'}})
.catch(function(){m.textContent='Network error, please try again.'}).finally(function(){b.disabled=false})})})();</script>'''
_LD=ld({'@context':'https://schema.org','@graph':[{'@type':'Product','name':p[1],'description':p[7],'image':BASE+f'/img/photos/{p[2]}-1600.webp','url':BASE+f'/products.html#{p[0]}','brand':{'@type':'Brand','name':SITE},
  'offers':{'@type':'AggregateOffer','priceCurrency':'INR','lowPrice':p[3],'highPrice':p[4],'availability':'https://schema.org/PreOrder','url':BASE+f'/products.html#{p[0]}'}} for p in P_LIST]})

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

page('/products.html',f'AI Products by Suraj Kamdev · {SITE}','AI learning kits, business toolkits, prompt libraries, live training and AI receptionist setup in Hindi & English. Launching soon: join the waitlist.',
 '<section class="p-hero"><h1>AI products for learners and small businesses</h1><p class="p-hi" lang="hi">हिंदी और English में, सीधे काम आने वाले AI टूल्स और ट्रेनिंग।</p>'
 '<p class="sub">Our own products, built by Suraj Kamdev. <b>Launching soon — prices indicative.</b> Join the waitlist for early access; nothing is charged now.</p></section>'
 '<div class="sc-grid p-grid">'+''.join(_pcard(p,i<2) for i,p in enumerate(P_LIST))+'</div>'+_FORM+_JS+_TOOLSEC+_TJS,extra=_LD)
print('products: AI Free',len(_FREE),'AI Plus',len(_PLUS),'skipped-conflict',_SKIP)
urls.append('/products.html')
_TZ=('<!--products--><section class="showcase p-teaser"><h2>Our own AI products <span class="tag">Launching soon</span></h2><p class="sub">Hindi & English AI kits, toolkits and training from Suraj Kamdev. Prices indicative, join the waitlist for early access.</p><div class="sc-grid">'
 +''.join(f'<article class="card sc-card p-card">{_PH.picture(p[2],p[1])}<div class="sc-body"><h3><a href="/products.html#{p[0]}">{E(p[1])}</a></h3><p class="p-price">{_price(p)}</p><p class="sub l1">{E(p[7])}</p></div></article>' for p in P_LIST[:4])
 +'</div><p class="sc-actions"><a class="cta-aff sm" href="/products.html">See all 7 products →</a></p></section><!--/products-->')
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
