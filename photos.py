"""Cinematic stock photos (Unsplash / Pexels free licenses), downloaded to /img/photos/<key>-{480,960,1600}.webp.
Themes per category/department, rotated by slug. Credits: /credits.html. Used by build.py, tool_rich.py, directory_build.py."""
import html,zlib,json,os,datetime
E=lambda s:html.escape(str(s),quote=True)
CREDIT={"u-1753998943918-dd2dfc4ee6ed":"Rob Wingate","u-1518933165971-611dbc9c412d":"Irvan Smith","u-1774371386885-f21e309e146d":"gaspifilms",
 "p-37880101":"Alicia Christin Gerald","p-37607989":"Rafael Minguet Delgado","p-5380584":"Tima Miroshnichenko","p-38486967":"Ann H","p-33050961":"Atahan Demir",
 "p-3165335":"Lucie Liz","p-8937358":"Thirdman","p-30494308":"Jamie Kimball","p-8386440":"Tara Winstead","p-7387935":"Steve A Johnson","p-30111699":"Noland Live","p-8132809":"Anna Pou","p-6549865":"Tima Miroshnichenko"}
THEMES={
 'code':['u-1753998943918-dd2dfc4ee6ed','u-1518933165971-611dbc9c412d','p-16018144','p-36571389','p-34258667'],
 'apps':['p-16313501','p-28550000','p-7180971','p-9553909'],
 'db':['p-5480781','p-37730211','p-5050305','p-1148820'],
 'host':['p-1148820','p-39808538','p-7562085','p-586087'],
 'ai':['p-35445090','p-6985265','p-7130552','p-33839920'],
 'agents':['p-8294557','p-8294605','p-8438865','p-8294608'],
 'video':['u-1641499303047-5f1c5cd5b305','u-1761499930744-1d689014c9a6','p-33475987','p-38059008','p-32610376'],
 'audio':['u-1774371386885-f21e309e146d','u-1709846485906-30b28e7ed651','p-10854606','p-6878179','p-7301210'],
 'data':['p-5466250','p-265087','p-7567527','p-7180971'],
 'work':['p-38041122','p-5827789','p-5712533','p-3873742'],
}
MAP={'coding-agents':'code','ides':'code','developer-tools':'code','vibe-coding':'code','app-builders':'apps','design':'apps','image':'video',
 'databases':'db','databases-backend':'db','hosting':'host','ai-apis':'ai','ai-apis-models':'ai','chatbots':'ai','agent-frameworks':'agents','automation-agents':'agents',
 'video':'video','voice':'audio','audio-voice':'audio','data-analytics':'data','marketing-seo':'data','productivity':'work','writing':'work','research':'work','education':'work'}
BLOG={'ai-agent-hosting-options':'p-11086520','ai-api-pricing-guide':'p-5466250','ai-tools-for-solo-founders':'p-3873742','best-ai-app-builders':'p-28550000',
 'best-ai-code-editor-2026':'p-36571389','best-ai-coding-agents':'p-34258667','best-ai-tools-for-beginners-to-build-apps':'p-8937358','best-ai-tools-for-game-developers':'p-33050961',
 'best-ai-video-generators':'u-1761499930744-1d689014c9a6','best-ai-voice-tools':'u-1774371386885-f21e309e146d','best-database-for-side-projects':'p-37730211',
 'best-free-ai-tools-for-developers':'p-37880101','best-mcp-servers-for-cursor':'p-5050305','claude-code-tutorial-for-beginners':'p-177598','claude-code-vs-codex':'p-7988113',
 'claude-vs-gpt-for-coding':'p-33839920','cursor-rules-examples':'p-270348','cursor-vs-claude-code':'u-1753998943918-dd2dfc4ee6ed','free-ai-image-generators-for-indie-games':'p-3165335',
 'free-hosting-for-side-projects':'p-1148820','github-copilot-vs-cursor':'p-3861972','how-to-build-a-saas-with-ai':'p-30494308','how-to-build-an-ai-agent':'p-8294557',
 'how-to-deploy-a-vibe-coded-app':'p-586087','how-to-vibe-code-an-app':'p-32601817','mcp-explained':'p-39808538','neon-vs-supabase':'p-5480781','openrouter-guide':'p-7130552',
 'prompt-tips-for-coding-agents':'p-5380584','supabase-vs-firebase':'p-4033964','vibe-coding-security-checklist':'p-38486967','vibe-coding-tools-list':'p-37607989','windsurf-vs-cursor':'p-9553909','best-ai-agent-builders-2026':'p-8386440','best-ai-image-generators-2026':'p-7387935','best-ai-tools-for-streamers-and-gamers':'p-30111699','best-ai-music-generators':'p-8132809','best-ai-research-tools':'p-6549865','best-ai-chatbots-2026':'p-15940006','best-ai-ui-design-tools':'p-3471423','best-ai-customer-support-agents':'p-7709109','best-tools-to-run-llms-locally':'p-33798621','best-ai-avatar-video-generators':'p-29708241'}
def src_url(k):
    s,i=k.split('-',1)
    return f'https://unsplash.com/' if s=='u' else f'https://www.pexels.com/photo/{i}/'
def site(k): return 'Unsplash' if k.startswith('u-') else 'Pexels'
def credit(k): return (f'Photo by {CREDIT[k]} on {site(k)}' if k in CREDIT else f'Photo via {site(k)}')
import os as _os,json as _json
try: BRAND=_json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'data','brand-images.json')))
except Exception: BRAND={}
def pick(theme_key,slug):
    if slug in BRAND and slug!=theme_key: return 'b-'+slug
    L=THEMES[MAP.get(theme_key,'ai')]; return L[zlib.crc32(slug.encode())%len(L)]
def picture(k,alt='',eager=False,sizes='(max-width:600px) 100vw, 480px',cls='ph-img'):
    b=f'/img/photos/{k}'
    return (f'<picture><source type="image/webp" srcset="{b}-480.webp 480w, {b}-960.webp 960w, {b}-1600.webp 1600w" sizes="{sizes}">'
            f'<img class="{cls}" src="{b}-960.webp" width="960" height="540" alt="{E(alt)}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async"></picture>')
def banner(theme_key,slug,logo,name,eager=False,sizes='(max-width:600px) 100vw, 480px',badge=''):
    k=pick(theme_key,slug); br=BRAND.get(slug) if k.startswith('b-') else None
    if br=='logo': logo=''
    return (f'<div class="ph{" ph-brand" if br else ""}">{picture(k,"",eager,sizes)}<span class="ph-ov"></span>'
            +(f'<img class="ph-logo" src="{E(logo)}" width="56" height="56" alt="{E(name)} logo" loading="{"eager" if eager else "lazy"}" decoding="async">' if logo else '')
            +badge+'</div>')
# affiliate/deal helpers
NOW=datetime.datetime.now(datetime.timezone.utc)
def _exp(x):
    try: return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
    except Exception: return None
def offer(a):
    """Return dict with code/text/expires if a real, active, unexpired offer exists in an affiliates.json entry."""
    if not a or a.get('status')!='active' or not (a.get('discount_code') or a.get('discount_text')): return None
    ex=a.get('expires_at') or ''; d=_exp(ex) if ex else None
    if d and d<=NOW: return None
    return {'code':a.get('discount_code',''),'text':a.get('discount_text',''),'expires':ex if d else ''}
def cta(slug,name,a=None,cls='cta-aff'):
    o=offer(a); lab='Get Deal →' if o else 'Visit Official Site →'
    return f'<a class="{cls}" href="/go/{slug}" data-tool="{slug}" data-deal-cta target="_blank" rel="sponsored nofollow noopener" aria-label="{E(lab[:-2]+" for "+name)}">{lab}</a>'
GO='https://vibestack-rankings.vercel.app/go/'
def dealbox(slug,name,a=None):
    o=offer(a)
    timer=f'<p class="deal-timer" data-expires="{E(o["expires"])}">Ends in <b class="cd">…</b></p>' if o and o['expires'] else ''
    if o and o['code']:
        codeh=(f'<div class="deal-code-row"><code class="deal-code">{E(o["code"])}</code><button class="btn-copy" data-copy-code="{E(o["code"])}" data-code-id="{slug}">Copy Code</button></div>')
    else: codeh='<p class="deal-none">Verified code not available yet.</p>'
    return (f'<section class="card deal-box" data-deal="{slug}"><h2>Deal &amp; discount</h2>'+(f'<p>{E(o["text"])}</p>' if o and o['text'] else '')+codeh+timer
            +f'<div class="deal-actions">{cta(slug,name,a)}<button class="btn-ghost" data-copy-link="{GO}{slug}" data-link-id="{slug}">Copy Link</button></div></section>')
def sticky(slug,name,a=None):
    return f'<div class="sticky-cta" role="region" aria-label="Quick link"><span>{E(name)}</span>{cta(slug,name,a)}</div>'
def voteline(slug): return f'<p class="vote-line" data-vote-line="{slug}"></p>'
PRODUCT_PHOTOS={'p-4050315','p-6693655','p-1181244','p-4144923','p-8867482','p-3756679','p-3184465'}
def credits_rows():
    keys=sorted({k for L in THEMES.values() for k in L}|set(BLOG.values())|PRODUCT_PHOTOS)
    return keys
