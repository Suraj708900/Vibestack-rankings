from pathlib import Path
import json,re,hashlib,zipfile,html
B=Path(__file__).resolve().parent; before=B/'before';out=B/'release';out.mkdir(exist_ok=True)
old=json.loads((before/'data/products-config.json').read_text());cfg=json.loads(json.dumps(old))
prices={'ai-learning-kit':(499,5.27),'ai-prompt-library':(349,3.69),'ai-knowledge-membership':(399,4.21),'live-ai-training':(999,10.55),'resume-job-hunt-ai-pack':(699,7.38),'content-creator-ai-pack':(799,8.44),'ai-business-toolkit':(1299,13.71),'freelancer-ai-proposal-kit':(1499,15.82),'vibe-coding-starter-kit':(1799,18.98),'industry-ai-kits':(2499,26.37),'ai-receptionist-setup':(3499,36.93)}
assert len(set(p[0] for p in prices.values()))==11
for slug,(inr,usd) in prices.items():
 assert inr>old['products'][slug]['price'] and usd>old['products'][slug]['price_usd']
 cfg['products'][slug].update(price=inr,price_usd=usd)
def write(f,s):
 p=out/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def price_text(s,slug):
 p=old['products'][slug];n=cfg['products'][slug]
 return s.replace('₹'+format(p['price'],','),'₹'+format(n['price'],',')).replace('$'+str(p['price_usd']),'$'+str(n['price_usd']))
def schema(s):
 def sub(m):
  j=json.loads(m[1]);changed=False
  def walk(o):
   nonlocal changed
   if isinstance(o,dict):
    if o.get('@type')=='Product':
     slug=next((k for k,v in cfg['products'].items() if v['name']==o.get('name')),None)
     if slug and isinstance(o.get('offers'),dict):o['offers']['price']=cfg['products'][slug]['price'];changed=True
    for v in o.values():walk(v)
   elif isinstance(o,list):
    for v in o:walk(v)
  walk(j)
  return '<script type="application/ld+json">'+json.dumps(j,ensure_ascii=False).replace('</','<\\/')+'</script>' if changed else m[0]
 return re.sub(r'<script type="application/ld\+json">(.*?)</script>',sub,s,flags=re.S)
listing=(before/'products.html').read_text()
def card(m):
 a=m[0];slug=re.search(r'\bid="([^"]+)"',a)[1];a=price_text(a,slug)
 # Each detail link keeps its own URL and receives a unique accessible name.
 a=a.replace(f'<a href="/product/{slug}.html">Details, comments &amp; reviews →</a>',f'<a class="p-product-details" href="/product/{slug}.html" aria-label="{html.escape(cfg["products"][slug]["name"],quote=True)}: details, comments and reviews">Details, comments &amp; reviews →</a>')
 a=a.replace('<p class="pe-stats"', '<p title="Live visitor activity for this product" class="pe-stats"')
 for k,label in [('views','👁 — views'),('likes','♥ — likes'),('comments','💬 — comments')]:a=a.replace(f'<span data-k="{k}"></span>',f'<span data-k="{k}">{label}</span>')
 return a
listing=re.sub(r'<article class="card sc-card p-card pe".*?</article>',card,listing,flags=re.S)
write('products.html',schema(listing))
for slug in prices:
 f='product/'+slug+'.html';s=(before/f).read_text();write(f,schema(price_text(s,slug)))
co=(before/'checkout.html').read_text()
m=re.search(r'window.VS_PAY=(.*?);</script>',co,re.S);public=json.loads(m[1]);assert set(public['products'])==set(prices)
for slug,(inr,usd) in prices.items():public['products'][slug].update(price=inr,price_usd=usd)
co=co[:m.start(1)]+json.dumps(public,ensure_ascii=False).replace('</','<\\/')+co[m.end(1):];write('checkout.html',co)
home=(before/'index.html').read_text()
def teaser(m):
 s=m[0];slug=re.search(r'/products.html#([^"\s]+)',s)[1];return price_text(s,slug)
home=re.sub(r'<article[^>]*p-card[^>]*>.*?</article>',teaser,home,flags=re.S);write('index.html',home)
write('data/products-config.json',json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
# Preserve unchanged scripts, URLs, images, descriptions, payment recipients and all product contents.
checks=[]
for p in sorted(out.rglob('*')):
 if not p.is_file() or p.suffix!='.html':continue
 f=str(p.relative_to(out));a=(before/f).read_text();b=p.read_text()
 assert re.findall(r'href="([^"]+)"',a)==re.findall(r'href="([^"]+)"',b),f
 assert re.findall(r'<img\b[^>]*>',a)==re.findall(r'<img\b[^>]*>',b),f
 for tag in re.findall(r'<script\b[^>]*>.*?</script>',a,re.S):
  if 'application/ld+json' not in tag and 'window.VS_PAY=' not in tag:assert tag in b,f
 checks.append(f)
for key in cfg:
 if key!='products':assert cfg[key]==old[key]
for slug,p in cfg['products'].items():
 for key in p:
  if key not in ['price','price_usd']:assert p[key]==old['products'][slug][key]
report={'prices':{k:{'name':cfg['products'][k]['name'],'inr':v[0],'usd':v[1],'unit':cfg['products'][k].get('unit','')} for k,v in prices.items()},'html_pages_checked':checks,'all_links_images_and_nonprice_scripts_preserved':True,'review_links_unique':len(re.findall(r'class="p-product-details"',listing))==11,'activity_counts':'Existing live API, no fabricated or seeded counts','existing_orders_changed':False,'subscriptions_activated':False}
(B/'build-report.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(B/'before-prices.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in before.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(before)))
with zipfile.ZipFile(B/'before-prices.zip') as z:
 assert z.testzip() is None
 for n in z.namelist():assert z.read(n)==(before/n).read_bytes()
print('Built 15 scoped files; backup CRC and byte-for-byte restore verified. 11 prices distinct and increased; all original URLs, scripts, images and product contents preserved.')
