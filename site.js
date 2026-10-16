/* Sitewide: Ctrl/Cmd+K search, tool-click tracking, trending upgrade, gentle newsletter CTA. */
(function(){
const H=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const beacon=(o)=>{try{const b=JSON.stringify(o);navigator.sendBeacon?navigator.sendBeacon('/api/track',new Blob([b],{type:'application/json'})):fetch('/api/track',{method:'POST',headers:{'Content-Type':'application/json'},body:b,keepalive:true})}catch(e){}};
window.VS_TRACK=beacon;
// ---- search
let idx=null,box,inp,list,sel=0,items=[];
function build(){
 box=document.createElement('div');box.className='sx';box.hidden=true;
 box.innerHTML='<div class="sx-panel" role="dialog" aria-label="Search"><input class="sx-in" placeholder="Search tools, categories, guides…" aria-label="Search" autocomplete="off"><div class="sx-list" role="listbox"></div><div class="sx-foot">↑↓ to move · Enter to open · Esc to close</div></div>';
 document.body.appendChild(box);inp=box.querySelector('.sx-in');list=box.querySelector('.sx-list');
 box.addEventListener('click',e=>{if(e.target===box)close()});
 inp.addEventListener('input',run);
 inp.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){sel=Math.min(sel+1,items.length-1);paint();e.preventDefault()}else if(e.key==='ArrowUp'){sel=Math.max(sel-1,0);paint();e.preventDefault()}else if(e.key==='Enter'&&items[sel]){location.href=items[sel].u}else if(e.key==='Escape')close()});
}
function score(d,q){const t=d.t.toLowerCase(),k=(d.t+' '+d.d+' '+(d.k||'')).toLowerCase();let s=0;for(const w of q){if(t.startsWith(w))s+=6;else if(t.includes(w))s+=4;else if(k.includes(w))s+=1;else return 0}return s+(d.y==='tool'?0.5:0)}
function run(){const q=inp.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
 items=!q.length?idx.filter(d=>d.y!=='tool').slice(0,8):idx.map(d=>[score(d,q),d]).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]).slice(0,12).map(x=>x[1]);sel=0;paint()}
function paint(){list.innerHTML=items.length?items.map((d,i)=>`<a class="sx-it${i===sel?' on':''}" href="${H(d.u)}" role="option"><span class="tag">${H(d.y)}</span> <b>${H(d.t)}</b><span class="sub">${H(d.d)}</span></a>`).join(''):'<p class="sub" style="padding:12px">No results. Try "database", "video" or "free".</p>'}
async function open(){if(!box)build();box.hidden=false;inp.focus();if(!idx){try{idx=await fetch('/search-index.json').then(r=>r.json())}catch(e){idx=[]}}run()}
function close(){box.hidden=true}
window.VS_SEARCH=open;
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();box&&!box.hidden?close():open()}else if(e.key==='/'&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();open()}});
document.querySelectorAll('[data-search]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();open()}));
// ---- tool click tracking (outbound official links)
document.addEventListener('click',e=>{const a=e.target.closest('a[data-tool]');if(a)beacon({kind:'tool',type:'click',id:a.dataset.tool})});
// ---- copy link buttons
document.addEventListener('click',e=>{const b=e.target.closest('[data-copy]');if(!b)return;e.preventDefault();navigator.clipboard&&navigator.clipboard.writeText(location.href.split('#')[0]).then(()=>{b.textContent='Copied ✓';setTimeout(()=>b.textContent='Copy link',1500)})});
// ---- trending: replace editor picks with real click data when there is enough
const tr=document.getElementById('trending');
if(tr)fetch('/api/stats?days=7').then(r=>r.json()).then(s=>{const t=Object.entries(s.tools||{}).sort((a,b)=>b[1]-a[1]);const total=t.reduce((n,x)=>n+x[1],0);if(total<10)return;
 fetch('/search-index.json').then(r=>r.json()).then(ix=>{const by={};ix.filter(d=>d.y==='tool').forEach(d=>by[d.u.split('/').pop().replace('.html','')]=d);
  const top=t.filter(([id])=>by[id]).slice(0,6);if(top.length<3)return;
  tr.querySelector('h2').textContent='Trending this week';tr.querySelector('.sub').textContent='Ranked by real outbound clicks on this site in the last 7 days.';
  fetch('/data/photo-map.json').then(r=>r.json()).catch(()=>({})).then(pm=>{tr.querySelector('.sc-grid').innerHTML=top.map(([id,n],i)=>{const m=pm[id]||[];return `<article class="card sc-card"><div class="ph">${m[0]?`<picture><source type="image/webp" srcset="/img/photos/${m[0]}-480.webp 480w, /img/photos/${m[0]}-960.webp 960w" sizes="(max-width:600px) 100vw, 480px"><img class="ph-img" src="/img/photos/${m[0]}-480.webp" width="960" height="540" alt="" loading="lazy" decoding="async"></picture>`:''}<span class="ph-ov"></span>${m[1]?`<img class="ph-logo" src="${m[1]}" width="56" height="56" alt="" loading="lazy">`:''}<span class="rank-badge">#${i+1}</span></div><div class="sc-body"><h3><a href="${by[id].u}">${H(by[id].t)}</a></h3><p class="sub">${n} click${n>1?'s':''} this week</p>${m[2]||''}</div></article>`}).join('')})})}).catch(()=>{});
// ---- gentle newsletter CTA: blog posts only, after 60% scroll, once per 14 days, never if subscribed
const KEY='vs-nl-cta';
if(document.body.dataset.page==='post'&&!localStorage.getItem('vs-subscribed')&&Date.now()-(+localStorage.getItem(KEY)||0)>14*864e5){
 const onS=()=>{const h=document.documentElement;if((h.scrollTop+innerHeight)/h.scrollHeight<0.6)return;removeEventListener('scroll',onS);
  localStorage.setItem(KEY,Date.now());const c=document.createElement('div');c.className='nl-pop';
  c.innerHTML='<button class="nl-x" aria-label="Close">×</button><b>Enjoying this guide?</b><p class="sub" style="margin:.3em 0 .6em">Get the weekly stack: rank movers and new tools, once a week.</p><a class="promo-cta" href="#post-newsletter">Subscribe free</a>';
  document.body.appendChild(c);c.querySelector('.nl-x').onclick=()=>c.remove();c.querySelector('a').onclick=()=>c.remove()};
 addEventListener('scroll',onS,{passive:true});
}
// newsletter forms with class .nlf
document.addEventListener('submit',e=>{const f=e.target;if(!f.matches('.nlf'))return;e.preventDefault();const m=f.querySelector('.nlmsg');
 fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value,company:f.company.value})}).then(r=>r.json()).then(j=>{m.textContent=j.ok?"You're in! 🎉":j.error;if(j.ok){f.reset();localStorage.setItem('vs-subscribed','1')}}).catch(()=>m.textContent='Something went wrong.')});
})();

document.addEventListener('click',e=>{const b=e.target.closest('[data-code]');if(!b)return;const c=b.dataset.code;navigator.clipboard&&navigator.clipboard.writeText(c);b.textContent='Copied ✓';setTimeout(()=>b.textContent='Copy code',1500);try{window.VS_TRACK&&VS_TRACK({kind:'code',type:'copy',id:b.dataset.codeId||'unknown'})}catch(_){}});
