from pathlib import Path
import json,re,html,shutil,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];data=json.loads((root/'editorial/utility-guides-20261102.json').read_text());out=root/'editorial/release';out.mkdir(exist_ok=True)
esc=lambda s:html.escape(str(s),quote=True)
base=(root/'editorial/templates/klap-guide-before.html').read_text()
css='''<style data-blog-media>main.klap-copy{max-width:960px;margin-inline:auto;padding:24px}main.klap-copy p,main.klap-copy li{line-height:1.85}main.klap-copy h1{font-size:clamp(28px,4vw,43px);line-height:1.2;letter-spacing:-.03em}main.klap-copy h2{margin-top:32px}.guide-media{margin:25px 0}.guide-media img,.guide-media video{display:block;width:100%;height:auto;border:1px solid var(--bd2,#ddd);border-radius:16px;background:#111420}.guide-media figcaption{font-size:12px;line-height:1.7;color:var(--tx2,#657085);margin-top:8px}.guide-cta{display:inline-block;border-radius:12px;padding:12px 17px;background:var(--ac,#6950e8);color:var(--ac-tx,#fff)!important;text-decoration:none;font-weight:650}.guide-keywords{font-size:12px;color:var(--tx2,#657085)}.guide-toc{border:1px solid var(--bd2,#ddd);border-radius:16px;padding:17px 22px;background:var(--card,#fafafa)}.guide-toc ol{margin-bottom:0}.guide-related{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.guide-related a{padding:10px 14px;border:1px solid var(--bd2,#ddd);border-radius:10px}@media(max-width:520px){main.klap-copy{padding:16px}.guide-media img,.guide-media video{border-radius:12px}}</style>'''
def media(tool,title):return f'<figure class="guide-media"><img src="/assets/blog-guides-20261102/blog-guide-{tool}.jpg" width="1348" height="926" alt="{esc(title)}: AIUseFlow tool interface" decoding="async"><figcaption>Original AIUseFlow interface screenshot, captured 2 November 2026. The image shows the controls, not a completed user submission.</figcaption></figure>'
def page(d,i):
 slug=d['slug'];url='https://aiuseflow.com/blog/'+slug+'.html';s=base
 # Replace all inherited metadata and schema rather than retaining Klap facts.
 s=re.sub(r'<title>.*?</title>',f'<title>{esc(d["title"])} | AIUseFlow</title>',s,flags=re.S)
 s=re.sub(r'<meta\b[^>]*(?:property|name)="(?:description|og:[^"]+|twitter:[^"]+)"[^>]*>','',s)
 s=re.sub(r'<link\b[^>]*rel="canonical"[^>]*>',f'<link rel="canonical" href="{url}">',s)
 s=re.sub(r'<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>','',s,flags=re.S)
 image='https://aiuseflow.com/assets/blog-guides-20261102/blog-guide-'+d['tool']+'.jpg'
 schema={'@context':'https://schema.org','@type':'BlogPosting','headline':d['title'],'description':d['description'],'image':image,'datePublished':'2026-11-02','dateModified':'2026-11-02','author':{'@type':'Organization','name':'AIUseFlow Editorial','url':'https://aiuseflow.com/about'},'publisher':{'@type':'Organization','name':'AIUseFlow','url':'https://aiuseflow.com/'},'mainEntityOfPage':url,'inLanguage':'en','keywords':[d['keyword']]}
 meta=f'<meta name="description" content="{esc(d["description"])}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(d["title"])}"><meta property="og:description" content="{esc(d["description"])}"><meta property="og:url" content="{url}"><meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{json.dumps(schema)}</script>'+css
 s=s.replace('</head>',meta+'</head>')
 body=f'<main class="klap-copy"><nav aria-label="Breadcrumb"><a href="/blog/">Blog</a> / {esc(d["category"])}</nav><article><h1>{esc(d["title"])}</h1><p class="sub">AIUseFlow Editorial · Published 2 November 2026 · Practical guide</p><p>{esc(d["intro"])}</p>'+media(d['tool'],d['title'])+f'<p><a class="guide-cta" href="/tools/{d["tool"]}/">Open the free tool →</a></p><nav class="guide-toc" aria-label="In this guide"><strong>In this guide</strong><ol>'+''.join(f'<li><a href="#step-{j}">{esc(h)}</a></li>' for j,(h,t) in enumerate(d['sections'],1))+'</ol></nav>'
 for j,(h,t) in enumerate(d['sections'],1):body+=f'<section><h2 id="step-{j}">{esc(h)}</h2><p>{esc(t)}</p></section>'
 body+='<h2>Quick answers</h2>'+''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q,a in d['faq'])
 body+=f'<h2>Source and editorial note</h2><p>This practical workflow is AIUseFlow editorial guidance based on the current tool interface. <a href="{esc(d["source"])}" rel="noopener">Reference documentation</a> was checked on 2 November 2026. Browser limits and recipient requirements can vary. Basic utilities cost ₹0 and do not enroll you in payments.</p><p class="guide-keywords"><strong>Topic:</strong> {esc(d["keyword"])}</p><h2>Continue with a related guide</h2><div class="guide-related">'
 for r in [data[(i+1)%10],data[(i+2)%10]]:body+=f'<a href="/blog/{r["slug"]}.html">{esc(r["title"])}</a>'
 body+='</div><p><a href="/#free-tools">Explore all 50 free tools</a> · <a href="/blog/">All blog posts</a></p></article></main>'
 s=re.sub(r'<main\b[^>]*>.*?</main>',lambda _:body,s,flags=re.S)
 assert len(re.findall(r'<h1\b',s))==1
 for x in re.findall(r'<script\b[^>]*src="[^"]+"[^>]*></script>',base):assert x in s
 p=out/'blog'/f'{slug}.html';p.parent.mkdir(exist_ok=True);p.write_text(s)
 return body
counts={}
for i,d in enumerate(data):
 body=page(d,i);counts[d['slug']]=len(re.sub('<[^>]+>',' ',body).split())
# Official media has a direct fallback, no autoplay and no third-party request before video playback.
video='https://assets.klap.app/web-assets/landing/klap-ai-generate.mp4'
klap_media='<section id="klap-product-media"><h2>Klap photos and official product demo</h2><figure class="guide-media"><img src="/assets/blog-guides-20261102/blog-guide-klap.jpg" width="1348" height="926" alt="Klap official website showing its long-video to short-clips workflow" loading="lazy" decoding="async"><figcaption>Screenshot of <a href="https://klap.app/" rel="noopener">Klap’s official website</a>, captured 2 November 2026. Product claims in the screenshot belong to Klap; they are not an AIUseFlow performance guarantee.</figcaption></figure><figure class="guide-media"><video controls playsinline muted preload="none" aria-label="Official Klap clip-generation product demo" poster="/assets/blog-guides-20261102/blog-guide-klap.jpg"><source src="'+video+'" type="video/mp4">Your browser cannot play this video.</video><figcaption>Official visual product demo, hosted by Klap. Playback connects your browser to Klap’s media host. <a href="'+video+'" target="_blank" rel="noopener">Open the official video directly</a>. The demo illustrates the interface; it is not a promise of views, sales or identical results.</figcaption></figure></section>'
for source,target in [('klap-guide-before.html','blog/klap-ai-video-shorts-guide.html'),('klap-listing-before.html','t/klap.html')]:
 s=(root/'editorial/templates'/source).read_text();s=s.replace('</head>',css+'</head>');s=s.replace('</main>',klap_media+'</main>');p=out/target;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
# Add cards without replacing or removing any existing article card.
s=(root/'editorial/templates/blog-index-before.html').read_text()
cards=''.join(f'<a class="card sc-card blog-card" style="text-decoration:none;color:inherit" href="/blog/{d["slug"]}.html"><img src="/assets/blog-guides-20261102/blog-guide-{d["tool"]}.jpg" width="1348" height="926" style="display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;object-position:top;border-radius:14px 14px 0 0" alt="{esc(d["title"])} tool screenshot" loading="lazy" decoding="async"><div class="sc-body"><span class="tag">{esc(d["category"])} · 2 Nov 2026</span><h3>{esc(d["title"])}</h3><p class="sub">{esc(d["description"])}</p></div></a>' for d in data)
assert '<div class="sc-grid">' in s;s=s.replace('<div class="sc-grid">','<div class="sc-grid">'+cards,1);(out/'blog/index.html').write_text(s)
# Keep article media in the same deployment package.
shutil.copytree(root/'assets/blog-guides-20261102',out/'assets/blog-guides-20261102',dirs_exist_ok=True)
(root/'editorial/article-word-counts.json').write_text(json.dumps(counts,indent=2));print(json.dumps({'new_articles':len(data),'word_counts':counts,'klap_media_pages':2,'image_assets':len(list((out/'assets/blog-guides-20261102').glob('*.jpg')))},indent=2))
