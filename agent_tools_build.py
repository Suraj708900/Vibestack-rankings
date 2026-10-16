# /agent-tools.html + homepage teaser. Data: data/agent-tools.json (stars/license fetched from the GitHub REST API; nothing invented).
_AT=json.load(open('data/agent-tools.json')); _ATL=_AT['tools']
_fs=lambda n:(f'{n/1000:.1f}k'.replace('.0k','k') if n>=1000 else str(n)) if isinstance(n,int) else 'N/A'
_ATTABS=[('all','All Tools'),('mcp','MCP Servers'),('cli','CLI'),('security','Security'),('dev','Developer'),('data','Data'),('web','Web & Browser'),('ops','Cloud & Ops')]
_TC=['#7c5cff','#20d3c2','#ff7ab6','#ffb547','#5aa9ff','#7be37b']
def _atcode(t,op=False):
    tabs=[(k,l,t.get(k)) for k,l in (('install','Install'),('config','MCP config')) if t.get(k)]
    src=f'<p class="at-rsrc">Source: <a href="{E(t.get("readme") or t["url"])}" target="_blank" rel="noopener">README</a> · {E(t["repo"])}</p>'
    if not tabs: return f'<div class="at-code at-none"><span>No install or config snippet in the README.</span> <a href="{E(t["url"])}" target="_blank" rel="noopener">See repo ↗</a></div>'
    return ('<details class="at-code"'+(' open' if op else '')+'><summary>Show setup code</summary><div class="at-cbox"><div class="at-ctabs">'
     +''.join(f'<button type="button" data-ct="{k}"{" class=on" if j==0 else ""}>{l}</button>' for j,(k,l,_) in enumerate(tabs))
     +'<button type="button" class="at-copy">Copy</button></div>'
     +''.join(f'<pre data-cp="{k}"{"" if j==0 else " hidden"}><code>{E(v)}</code></pre>' for j,(k,_,v) in enumerate(tabs))
     +'</div>'+src+'</details>')
def _atcard(t,i):
    n=E(t['name']); tags=' '.join(t['tags'])
    go=f'<a class="at-btn" href="/go/{t["brand"]}" data-tool="{t["brand"]}" target="_blank" rel="sponsored nofollow noopener">Official site ↗</a>' if t['brand'] else ''
    return (f'<article class="at-card" data-tags="{tags}"><div class="at-top"><img src="https://github.com/{E(t["owner"])}.png?size=80" width="40" height="40" alt="{n} logo" loading="lazy" decoding="async">'
     f'<div class="at-id"><h3>{n}</h3><p class="at-tag" style="color:{_TC[i%len(_TC)]}">{E(t["tagline"])}</p></div>'
     f'<div class="at-badges"><span title="GitHub stars"><b>{_fs(t["stars"])}</b>STARS</span><span title="License from GitHub"><b>{E(t["license"] or "N/A")}</b>LICENSE</span></div></div>'
     f'<p class="at-desc">{E(t["description"])}</p>'+_atcode(t,i==0)+f'<div class="at-foot"><span class="at-kind">{"MCP server" if "mcp" in t["tags"] else "CLI"}{" · CLI" if "mcp" in t["tags"] and "cli" in t["tags"] else ""}</span>'
     f'<a class="at-btn pri" href="{E(t["url"])}" target="_blank" rel="noopener">GitHub repo ↗</a>{go}</div></article>')
_ATJS=('<script>document.addEventListener("click",e=>{const b=e.target.closest(".at-ctabs button");if(!b)return;const box=b.closest(".at-cbox");'
 'if(b.classList.contains("at-copy")){const p=box.querySelector("pre:not([hidden])");navigator.clipboard.writeText(p.innerText).then(()=>{b.textContent="Copied";b.classList.add("ok");setTimeout(()=>{b.textContent="Copy";b.classList.remove("ok")},1600)});return}'
 'box.querySelectorAll("[data-ct]").forEach(x=>x.classList.toggle("on",x===b));box.querySelectorAll("pre").forEach(p=>p.hidden=p.dataset.cp!==b.dataset.ct)})</script>')
_N=len(_ATL); _STARS=sum(t['stars'] for t in _ATL if isinstance(t['stars'],int)); _NMCP=sum('mcp' in t['tags'] for t in _ATL); _NLIC=sum(1 for t in _ATL if t['license'])
_fd=_AT['fetched'][:10]
_ATSTATS=[(str(_N),'Open-source tools'),(_fs(_STARS),'Combined GitHub stars'),(str(_NMCP),'MCP servers'),(f'{_NLIC}/{_N}','OSI license on GitHub')]
_stats=''.join(f'<div class="at-stat"><b>{v}</b><span>{l}</span></div>' for v,l in _ATSTATS)
_body=(f'<section class="at-hero"><span class="at-pill">◆ Open Source · Curated by VibeStack</span><h1 class="at-h1">Agent Tools</h1>'
 f'<p class="at-lead">Open-source CLI tools and MCP servers that give AI agents programmatic control of your stack. <b>Every tool here is open source</b> and linked to its official repo.</p>'
 f'<p class="at-built">Built for <span>Cursor</span>, <span>Claude Code</span>, and any MCP-compatible agent. Install, configure in your agent, and let it work.</p>'
 f'<div class="at-stats">{_stats}</div><p class="at-src">Stars and licenses from the GitHub API, fetched {_fd}. N/A means GitHub reports no standard license.</p></section>'
 '<div class="at-tabs" role="tablist">'+''.join(f'<button role="tab" data-at="{k}"{" class=on" if k=="all" else ""}>{l}</button>' for k,l in _ATTABS)+'</div>'
 '<div class="at-grid" id="atg">'+''.join(_atcard(t,i) for i,t in enumerate(_ATL))+'</div>'+_ATJS+
 '<script>document.querySelectorAll(".at-tabs button").forEach(b=>b.onclick=()=>{document.querySelectorAll(".at-tabs button").forEach(x=>x.classList.toggle("on",x===b));const k=b.dataset.at;document.querySelectorAll("#atg .at-card").forEach(c=>c.hidden=k!=="all"&&!c.dataset.tags.split(" ").includes(k))})</script>')
_ATLD=ld({"@context":"https://schema.org","@type":"ItemList","name":"Agent Tools: open-source MCP servers and CLIs","itemListElement":[{"@type":"ListItem","position":i+1,"name":t['name'],"url":t['url']} for i,t in enumerate(_ATL)]})
page('/agent-tools.html',f'Agent Tools: {_N} open-source MCP servers & CLIs for AI agents · {SITE}',f'{_N} open-source MCP servers and CLI tools that give Cursor, Claude Code and other AI agents programmatic control. Real GitHub stars and licenses.',_body,extra=_ATLD,bodyattr=' class="at-page"')
urls.append('/agent-tools.html')
_top=sorted(_ATL,key=lambda t:-t['stars'])[:6]
_ATZ=('<!--agenttools--><section class="at-teaser"><span class="at-pill">◆ Open Source · Curated by VibeStack</span><h2>Agent Tools</h2><p class="sub">'+str(_N)+' open-source MCP servers and CLIs for Cursor, Claude Code and any MCP-compatible agent.</p>'
 '<div class="at-grid">'+''.join(_atcard(t,i) for i,t in enumerate(_top))+'</div>'+_ATJS+'<p class="sc-actions"><a class="cta-aff sm" href="/agent-tools.html">See all '+str(_N)+' agent tools →</a></p></section><!--/agenttools-->')
_ix=open('index.html').read(); _ix=re.sub(r'<!--agenttools-->.*?<!--/agenttools-->','',_ix,flags=re.S)
for _m in ('<!--/products-->','<!--/showcase-->','<div class="grid" id="cats"'):
    if _m in _ix: _ix=_ix.replace(_m,(_m+_ATZ) if _m.startswith('<!--') else (_ATZ+_m),1); break
open('index.html','w').write(_ix)
print('agent tools:',_N)
