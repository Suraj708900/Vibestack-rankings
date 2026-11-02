from pathlib import Path
import json,re
B=Path(__file__).resolve().parent;stage=B/'staging';stage.mkdir(exist_ok=True)
for p in (B/'release').rglob('*'):
 if not p.is_file():continue
 f=p.relative_to(B/'release');d=p.read_text()
 if p.suffix=='.html':d=d.replace('<head>','<head><base href="https://aiuseflow.com/"><meta name="robots" content="noindex,nofollow">',1)
 q=stage/f;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(d)
check='''<?php
require $_SERVER['DOCUMENT_ROOT'].'/api/_boot.php';
header('Content-Type: application/json');header('Cache-Control: no-store');header('X-Robots-Tag: noindex');
$out=[];foreach(vs_products_cfg()['products'] as $k=>$p){$out[$k]=['price'=>$p['price'],'price_usd'=>$p['price_usd']];}
echo json_encode(['prices'=>$out]);
'''
(stage/'check-prices.php').write_text(check)
expected=json.loads((B/'build-report.json').read_text())['prices']
qa='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Product pricing QA</title><style>body{font:16px system-ui;background:#101120;color:#fff;padding:24px}iframe{background:#fff;display:block;width:1280px;height:900px;border:0;margin:20px 0}.pass{color:#71eba2}.fail{color:#ff9090}pre{white-space:pre-wrap}</style></head><body><h1>Product pricing QA</h1><button id="run">Run checks</button><pre id="result">Ready</pre><div id="frames"></div><script>
const expected=EXPECTED;const rows=[];let passed=0,failed=0;const frames=document.querySelector('#frames');
function check(name,ok){rows.push({name,passed:!!ok});ok?passed++:failed++;document.querySelector('#result').textContent=JSON.stringify({passed,failed,checks:rows},null,2);}
function iframe(path,width=1280){return new Promise((res,rej)=>{let f=document.createElement('iframe');f.style.width=width+'px';f.src=path;f.onload=()=>res(f);f.onerror=rej;frames.append(f)})}
document.querySelector('#run').onclick=async()=>{document.querySelector('#run').disabled=true;try{
let f=await iframe('products.html');await new Promise(r=>setTimeout(r,1500));let d=f.contentDocument;let cards=[...d.querySelectorAll('article.p-card.pe')];check('All 11 products retained',cards.length===11);
for(const [slug,p] of Object.entries(expected)){let c=d.getElementById(slug);let price=c.querySelector('.p-price').textContent;check(p.name+' listing, review URL and live activity',price.includes('₹'+p.inr.toLocaleString('en-IN'))&&price.includes('$'+p.usd)&&c.querySelector('a.p-product-details').getAttribute('href')==='/product/'+slug+'.html'&&c.querySelector('.pe-stats').dataset.peSlug===slug&&c.querySelectorAll('.pe-stats [data-k]').length===3);}
check('Original 22 checkout links retained',d.querySelectorAll('.p-grid a[href^="/checkout.html"]').length===22);check('No fabricated engagement values',![...d.querySelectorAll('.pe-stats')].some(e=>/3330|2460|1567/.test(e.textContent)));
f.remove();
for(const [slug,p] of Object.entries(expected)){f=await iframe('product/'+slug+'.html');d=f.contentDocument;check(p.name+' detail price, checkout and review section',d.querySelector('main').textContent.includes('₹'+p.inr.toLocaleString('en-IN'))&&d.querySelector('main').textContent.includes('$'+p.usd)&&d.querySelector('#pe')?.dataset.peSlug===slug&&d.querySelectorAll('a[href*="/checkout.html?p='+slug+'"]').length===2);f.remove();}
f=await iframe('checkout.html?p=ai-learning-kit&m=paypal');await new Promise(r=>setTimeout(r,500));d=f.contentDocument;check('AI Learning Kit checkout ₹499 / $5.27',d.querySelector('#co-app').textContent.includes('₹499')&&d.querySelector('#co-app').textContent.includes('$5.27'));let pp=d.querySelector('[data-p="paypal"] a');let u=new URL(pp.href);check('Actual PayPal link uses amount 5.27 and USD',u.searchParams.get('amount')==='5.27'&&u.searchParams.get('currency_code')==='USD');check('All checkout prices match new catalog',Object.entries(expected).every(([k,p])=>f.contentWindow.VS_PAY.products[k].price===p.inr&&f.contentWindow.VS_PAY.products[k].price_usd===p.usd));f.remove();
f=await iframe('products.html',390);await new Promise(r=>setTimeout(r,1500));d=f.contentDocument;check('Mobile layout fits width',d.documentElement.scrollWidth<=392);check('All mobile card prices and detail links available',d.querySelectorAll('.p-product-details').length===11&&d.querySelectorAll('.pe-stats').length===11);f.remove();
}catch(e){check('QA execution: '+e.message,false)}document.body.dataset.done='true';};
</script></body></html>'''.replace('EXPECTED',json.dumps(expected))
(stage/'qa.html').write_text(qa)
print('Stage and QA prepared')
