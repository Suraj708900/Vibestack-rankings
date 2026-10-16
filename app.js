const H=(s)=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const SL=n=>n.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');let PM={},CP={};
const PIC=(k,lazy=1)=>k?`<picture><source type="image/webp" srcset="/img/photos/${k}-480.webp 480w, /img/photos/${k}-960.webp 960w" sizes="(max-width:600px) 100vw, 480px"><img class="ph-img" src="/img/photos/${k}-480.webp" width="960" height="540" alt="" ${lazy?'loading="lazy"':''} decoding="async"></picture>`:'';
const card=(t,i,c)=>{const s=SL(t.name),m=PM[s]||[];return `<article class="card sc-card"><div class="ph">${PIC(m[0])}<span class="ph-ov"></span>${m[1]?`<img class="ph-logo" src="${m[1]}" width="56" height="56" alt="${H(t.name)} logo" loading="lazy">`:''}<span class="rank-badge r${i+1}" title="Editorial rank">#${i+1}</span></div><div class="sc-body">${c?`<span class="tag">${H(c)}</span>`:''}<h3><a href="/tools/${s}.html">${H(t.name)}</a></h3><p class="sub">${H(t.verdict)}</p><div class="price">${H(t.price)}</div>${m[2]||`<a class="cta-aff sm" href="/go/${s}" data-tool="${s}" target="_blank" rel="sponsored nofollow noopener">Visit Official Site →</a>`}<p class="vote-line" data-vote-line="${s}"></p></div></article>`};
Promise.all([fetch('/tools.json').then(r=>r.json()),fetch('/data/photo-map.json').then(r=>r.json()).catch(()=>({})),fetch('/data/cat-photos.json').then(r=>r.json()).catch(()=>({}))]).then(([d,pm,cp])=>{PM=pm;CP=cp;
 const el=document.getElementById('app'),p=document.body.dataset.page;
 if(p==='home'){
  const sel=document.getElementById('cat');d.categories.forEach(c=>sel.insertAdjacentHTML('beforeend',`<option value="${c.id}">${c.name}</option>`));
  const draw=()=>{const q=document.getElementById('q').value.toLowerCase(),cv=sel.value,free=document.getElementById('free').checked;const act=q||cv||free;document.querySelectorAll('.showcase').forEach(x=>x.hidden=!!act);if(!act){el.innerHTML='';return}
   el.innerHTML=d.categories.filter(c=>!cv||c.id===cv).map(c=>{const ts=c.tools.map((t,i)=>[t,i]).filter(([t])=>(!q||(t.name+t.verdict+t.tags.join(' ')).toLowerCase().includes(q))&&(!free||t.tags.includes('free-tier')||/free/i.test(t.price)));
    return ts.length?`<section class="cat"><h2><a href="/category/${c.id}.html">${c.name} →</a></h2><p class="sub">${H(c.q)}</p><div class="sc-grid">${ts.map(([t,i])=>card(t,i)).join('')}</div></section>`:''}).join('')||'<p>No matches.</p>'};
  ['q','cat','free'].forEach(i=>document.getElementById(i).addEventListener('input',draw));draw();
  document.getElementById('cats').innerHTML=d.categories.map(c=>`<a class="card cat-tile" href="/category/${c.id}.html"><div class="ph">${PIC(CP[c.id])}<span class="ph-ov"></span></div><span class="cat-tile-t"><b>${c.name}</b><span class="sub">${c.tools.length} ranked picks</span></span></a>`).join('');
 }else if(p==='category'){
  const c=d.categories.find(c=>c.id===new URLSearchParams(location.search).get('c'))||d.categories[0];document.title=c.name+' · VibeStack Rankings';
  el.innerHTML=`<h1>${c.name}</h1><p class="sub">${H(c.q)} Updated ${d.updated}.</p><div class="sc-grid">${c.tools.map((t,i)=>card(t,i)).join('')}</div><h3>Other categories</h3><p>${d.categories.map(x=>`<a href="/category/${x.id}.html">${x.name}</a>`).join(' · ')}</p>`;
 }else if(p==='new'){
  el.innerHTML=d.news.map(n=>`<div class="card" style="margin-bottom:10px"><span class="tag">${n.date}</span><h3 style="margin:.4em 0">${H(n.title)}</h3><a href="${n.url}" target="_blank" rel="noopener">Source: ${H(n.source)} ↗</a></div>`).join('');
 }});
