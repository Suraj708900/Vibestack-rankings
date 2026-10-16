/* Tool of the day, compare page, helpful votes, admin vote stats, theme toggle. */
(function(){
const H=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const post=o=>fetch('/api/track',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o),keepalive:true}).catch(()=>{});
let TJ;const tj=()=>TJ||(TJ=fetch('/tools.json').then(r=>r.json()));
const all=d=>{const m={};d.categories.forEach(c=>c.tools.forEach((t,i)=>{const s=slug(t.name);(m[s]=m[s]||{s,t,ranks:[]}).ranks.push([c,i+1])}));return m};
// ---- theme toggle
const root=document.documentElement;let th=localStorage.getItem('vs-theme');if(th)root.dataset.theme=th;
const nav=document.querySelector('header nav');
if(nav){const b=document.createElement('button');b.className='theme-btn';b.setAttribute('aria-label','Toggle light/dark theme');
 const lab=()=>b.textContent=root.dataset.theme==='light'?'🌙':'☀️';lab();
 b.onclick=()=>{root.dataset.theme=root.dataset.theme==='light'?'dark':'light';localStorage.setItem('vs-theme',root.dataset.theme);lab()};nav.appendChild(b)}
// ---- tool of the day (homepage)
if(document.body.dataset.page==='home'){tj().then(d=>{const L=Object.values(all(d)).sort((a,b)=>a.s<b.s?-1:1);
 const day=new Date();const k=day.getFullYear()*10000+(day.getMonth()+1)*100+day.getDate();
 let h=k;h=((h^61)^(h>>>16))*9;h=h^(h>>>4);h=Math.imul(h,0x27d4eb2d);h=h^(h>>>15);const p=L[(h>>>0)%L.length];
 const dom=p.t.url.split('/')[2];const el=document.createElement('section');el.className='card totd';el.id='tool-of-the-day';
 el.innerHTML=`<span class="tag">⭐ AI tool of the day · ${day.toISOString().slice(0,10)}</span><h2 style="margin:.4em 0"><img src="https://www.google.com/s2/favicons?domain=${H(dom)}&sz=64" width="28" height="28" alt="" style="vertical-align:-6px;border-radius:6px;margin-right:8px"><a href="/tools/${p.s}.html">${H(p.t.name)}</a></h2><p class="sub">${p.ranks.map(([c,r])=>`#${r} in ${H(c.name)}`).join(' · ')}</p><p>${H(p.t.verdict)}</p><p class="price">${H(p.t.price)}</p><p><a class="cta-big" href="/go/${p.s}" data-tool="${p.s}" target="_blank" rel="sponsored nofollow noopener">Try ${H(p.t.name)} →</a> <a href="/tools/${p.s}.html">Full review</a></p>`;
 const a=document.querySelector('[data-promo="homepage-hero"]');a?a.after(el):document.querySelector('main').prepend(el)})}
// ---- compare page
const pick=document.getElementById('cmp-pick');
if(pick){const sels=[...pick.querySelectorAll('select')],out=document.getElementById('cmp-out');
 const q=(new URLSearchParams(location.search).get('tools')||'').split(',').filter(Boolean).slice(0,3);q.forEach((s,i)=>sels[i].value=s);
 tj().then(d=>{const M=all(d);
  const draw=()=>{const ch=sels.map(s=>s.value).filter((v,i,a)=>v&&a.indexOf(v)===i&&M[v]);
   const u=new URL(location.href);ch.length?u.searchParams.set('tools',ch.join(',')):u.searchParams.delete('tools');history.replaceState(null,'',u.pathname+u.search.replace(/%2C/g,','));
   if(ch.length<2){out.innerHTML='<p class="sub">Choose at least two tools above.</p>';return}
   const R=ch.map(s=>M[s]);const fr=t=>(t.tags||[]).includes('free-tier')||/free/i.test(t.price)?'Yes (per listing; confirm on official site)':'Not listed';
   const row=(l,f)=>`<tr><th>${l}</th>${R.map(x=>`<td>${f(x)}</td>`).join('')}</tr>`;
   out.innerHTML=`<div style="overflow-x:auto"><table class="tbl cmp-tbl"><tr><th></th>${R.map(x=>`<th><a href="/tools/${x.s}.html">${H(x.t.name)}</a></th>`).join('')}</tr>`
    +row('Category &amp; rank',x=>x.ranks.map(([c,r])=>`#${r} in <a href="/category/${c.id}.html">${H(c.name)}</a>`).join(' · '))+row('Pricing',x=>H(x.t.price))+row('Free tier',x=>fr(x.t))
    +row('Best for',x=>H(x.ranks[0][0].q))+row('Tags',x=>H((x.t.tags||[]).join(', ')))+row('Verdict',x=>H(x.t.verdict))
    +row('Official site',x=>`<a href="/go/${x.s}" data-tool="${x.s}" target="_blank" rel="sponsored nofollow noopener">Visit ${H(x.t.name)} ↗</a>`)+'</table></div><p class="sub">Pricing changes often; always check each official pricing page.</p>'};
  sels.forEach(s=>s.addEventListener('change',draw));draw()})}
// ---- helpful votes (tool pages)
const v=document.querySelector('[data-vote]');
if(v){const s=v.dataset.vote,key='vs-vote-'+s;v.className='card vote';
 v.innerHTML='<b>Was this pick helpful?</b> <button data-v="up" aria-label="Helpful">👍 Yes</button> <button data-v="down" aria-label="Not helpful">👎 No</button> <span class="sub vmsg"></span>';
 const msg=v.querySelector('.vmsg');let cnt={up:0,down:0};
 const show=()=>{const n=cnt.up+cnt.down;msg.textContent=(localStorage.getItem(key)?'Thanks for voting! ':'')+(n?`${cnt.up} of ${n} readers found this helpful (last 30 days).`:'')};
 if(localStorage.getItem(key))v.querySelectorAll('button').forEach(b=>b.disabled=true);
 fetch('/api/stats?days=30').then(r=>r.json()).then(j=>{cnt=Object.assign({up:0,down:0},(j.votes||{})[s]);show()}).catch(()=>{});
 v.addEventListener('click',e=>{const b=e.target.closest('button[data-v]');if(!b||localStorage.getItem(key))return;localStorage.setItem(key,b.dataset.v);cnt[b.dataset.v]++;
  post({kind:'vote',type:b.dataset.v,id:s});v.querySelectorAll('button').forEach(x=>x.disabled=true);show()});show()}
// ---- admin stats: votes table
if(location.pathname==='/admin-stats.html'){const box=document.createElement('section');box.innerHTML='<h2>Helpful votes (30 days)</h2><div id="votes-tbl" class="sub">Loading…</div>';document.querySelector('main').appendChild(box);
 fetch('/api/stats?days=30').then(r=>r.json()).then(j=>{const e=Object.entries(j.votes||{}).sort((a,b)=>(b[1].up+b[1].down)-(a[1].up+a[1].down));
  document.getElementById('votes-tbl').innerHTML=e.length?'<table class="tbl"><tr><th>Tool</th><th>👍</th><th>👎</th><th>% helpful</th></tr>'+e.map(([k,x])=>`<tr><td><a href="/tools/${H(k)}.html">${H(k)}</a></td><td>${x.up}</td><td>${x.down}</td><td>${Math.round(100*x.up/(x.up+x.down))}%</td></tr>`).join('')+'</table>':'No votes yet.'}).catch(()=>{document.getElementById('votes-tbl').textContent='Stats unavailable.'})}
})();
/* staggered scroll reveal (skipped for reduced motion / no IntersectionObserver) */
(function(){if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
document.documentElement.classList.add('js-rv');
const io=new IntersectionObserver(es=>{let k=0;es.forEach(e=>{if(e.isIntersecting){const el=e.target;el.style.transitionDelay=(Math.min(k++,6)*70)+'ms';el.classList.add('in');io.unobserve(el)}})},{rootMargin:'0px 0px -5% 0px'});
const scan=()=>document.querySelectorAll('main .card:not(.rv)').forEach(el=>{el.classList.add('rv');if(el.getBoundingClientRect().top<innerHeight){el.classList.add('in');el.style.transition='none'}else io.observe(el)});scan();
new MutationObserver(scan).observe(document.querySelector('main')||document.body,{childList:true,subtree:true});
setTimeout(()=>document.querySelectorAll('.rv:not(.in)').forEach(el=>{const r=el.getBoundingClientRect();if(r.top<innerHeight)el.classList.add('in')}),1500)})();
