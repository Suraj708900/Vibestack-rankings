/* VibeStack promo renderer. Reads /promotions.json, shows active in-date promos per placement,
   rotates when several share a slot. Indexes by placement once, so hundreds of promos are fine. */
(function(){
const PLACEMENTS={'homepage-hero':'Homepage hero banner','category-top':'Category top slot','sidebar-card':'Sidebar card','new-this-week':'New-this-week highlight','sitewide-strip':'Sitewide strip'};
const H=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=u=>/^(https?:\/\/|\/|mailto:)/i.test(u||'')?u:'#';
const today=new Date().toISOString().slice(0,10);
const live=p=>p&&p.active!==false&&(!p.start||p.start<=today)&&(!p.end||p.end>=today)&&PLACEMENTS[p.placement];
function html(p,cls){
  const ex=p.example?'<span class="promo-ex">EXAMPLE</span>':'';
  const logo=p.logo?`<img class="promo-logo" src="${H(safeUrl(p.logo))}" alt="" loading="lazy" width="40" height="40">`:'<span class="promo-logo promo-ph">★</span>';
  return `<div class="promo ${cls}" data-id="${H(p.id)}"><span class="promo-label">Sponsored</span>${ex}${logo}<div class="promo-body"><b>${H(p.tool)}</b><span>${H(p.headline)}</span></div><a class="promo-cta" href="${H(safeUrl(p.link))}" ${/^https?:/.test(p.link)?'target="_blank" rel="noopener sponsored"':''}>${H(p.cta||'Learn more')} →</a></div>`;
}
function mount(el,list,cls){
  if(!list.length){el.remove();return}
  // weighted-by-priority order: higher priority first, then rotate
  list.sort((a,b)=>(b.priority||0)-(a.priority||0));
  let i=Math.floor(Math.random()*Math.min(list.length,3));
  const seen=new Set(JSON.parse(sessionStorage.getItem('vs-imp')||'[]'));const imp=p=>{if(seen.has(p.id))return;seen.add(p.id);sessionStorage.setItem('vs-imp',JSON.stringify([...seen]));window.VS_TRACK&&VS_TRACK({kind:'promo',type:'impression',id:p.id})};
  el.addEventListener('click',e=>{const a=e.target.closest('.promo-cta'),pid=el.querySelector('.promo')?.dataset.id;if(a&&pid&&window.VS_TRACK)VS_TRACK({kind:'promo',type:'click',id:pid})});
  const show=()=>{imp(list[i%list.length]);el.innerHTML=html(list[i%list.length],cls)+(list.length>1?`<span class="promo-dots">${i%list.length+1}/${list.length}</span>`:'')};
  show();
  if(list.length>1){let t=setInterval(()=>{i++;show()},8000);el.addEventListener('mouseenter',()=>clearInterval(t));el.addEventListener('mouseleave',()=>{clearInterval(t);t=setInterval(()=>{i++;show()},8000)})}
}
fetch('/promotions.json',{cache:'no-cache'}).then(r=>r.json()).then(d=>{
  const by={};(d.promotions||[]).filter(live).forEach(p=>(by[p.placement]=by[p.placement]||[]).push(p));
  // sitewide strip goes at top of every page
  if(!document.querySelector('[data-promo="sitewide-strip"]')){const s=document.createElement('div');s.dataset.promo='sitewide-strip';document.body.prepend(s)}
  const qcat=new URLSearchParams(location.search).get('c')||'';
  document.querySelectorAll('[data-promo]').forEach(el=>{
    const pl=el.dataset.promo;let list=(by[pl]||[]).slice();
    if(pl==='category-top'){const cat=el.dataset.cat||qcat;const specific=list.filter(p=>p.category&&p.category===cat);list=specific.length?specific:list.filter(p=>!p.category)}
    mount(el,list,'promo-'+pl);
  });
}).catch(()=>document.querySelectorAll('[data-promo]').forEach(e=>e.remove()));
window.VS_PLACEMENTS=PLACEMENTS;
})();
