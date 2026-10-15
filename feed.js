/* LinkedIn-STYLE feed cards (not LinkedIn content). Picks N posts from feed.json based on today's date,
   so the section changes every day without redeploying. Usage: <div data-feed="/feed.json" data-count="3"></div> */
(function(){
const H=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
document.querySelectorAll('[data-feed]').forEach(el=>{
 fetch(el.dataset.feed,{cache:'no-cache'}).then(r=>r.json()).then(d=>{
  const ps=d.posts||[],n=Math.min(+el.dataset.count||3,ps.length),day=Math.floor(Date.now()/864e5),base=el.dataset.base||location.origin;
  const pick=Array.from({length:n},(_,i)=>ps[(day*n+i)%ps.length]);
  el.innerHTML=`<div class="feed-head"><h2>Builder tips &amp; tool spotlights</h2><span class="sub">Changes daily · ${new Date().toDateString()}</span></div><div class="feed-grid">`+pick.map(p=>{
   const url=/^https?:/.test(p.link)?p.link:base+p.link;
   return `<article class="feed-card"><div class="feed-top">${p.logo?`<img src="${H(p.logo)}" alt="" width="40" height="40" loading="lazy">`:'<span class="feed-av">VS</span>'}<div><b>VibeStack Rankings</b><div class="sub" style="font-size:12px">${H(p.type)}</div></div></div><h3>${H(p.title)}</h3><p>${H(p.body)}</p><div class="feed-act"><a href="${H(url)}" ${/^https?:/.test(p.link)?'target="_blank" rel="noopener"':''}>Read more →</a><a class="feed-share" target="_blank" rel="noopener" href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}">Share on LinkedIn</a></div></article>`}).join('')+'</div>';
 }).catch(()=>el.remove());
});})();
