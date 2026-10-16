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
page('/products.html',f'AI Products by Suraj Kamdev · {SITE}','AI learning kits, business toolkits, prompt libraries, live training and AI receptionist setup in Hindi & English. Launching soon: join the waitlist.',
 '<section class="p-hero"><h1>AI products for learners and small businesses</h1><p class="p-hi" lang="hi">हिंदी और English में, सीधे काम आने वाले AI टूल्स और ट्रेनिंग।</p>'
 '<p class="sub">Our own products, built by Suraj Kamdev. <b>Launching soon — prices indicative.</b> Join the waitlist for early access; nothing is charged now.</p></section>'
 '<div class="sc-grid p-grid">'+''.join(_pcard(p,i<2) for i,p in enumerate(P_LIST))+'</div>'+_FORM+_JS,extra=_LD)
urls.append('/products.html')
_TZ=('<!--products--><section class="showcase p-teaser"><h2>Our own AI products <span class="tag">Launching soon</span></h2><p class="sub">Hindi & English AI kits, toolkits and training from Suraj Kamdev. Prices indicative, join the waitlist for early access.</p><div class="sc-grid">'
 +''.join(f'<article class="card sc-card p-card">{_PH.picture(p[2],p[1])}<div class="sc-body"><h3><a href="/products.html#{p[0]}">{E(p[1])}</a></h3><p class="p-price">{_price(p)}</p><p class="sub l1">{E(p[7])}</p></div></article>' for p in P_LIST[:4])
 +'</div><p class="sc-actions"><a class="cta-aff sm" href="/products.html">See all 7 products →</a></p></section><!--/products-->')
_ix=open('index.html').read(); _ix=re.sub(r'<!--products-->.*?<!--/products-->','',_ix,flags=re.S)
if '<!--/showcase-->' in _ix: _ix=_ix.replace('<!--/showcase-->','<!--/showcase-->'+_TZ,1)
open('index.html','w').write(_ix)
