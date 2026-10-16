const H=(s)=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const card=(t,i,c)=>`<div class="card"><span class="rank">#${i+1}</span>${c?` <span class="tag">${H(c)}</span>`:''}<h3 style="margin:.4em 0"><a href="/go/${t.name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}" data-tool="${t.name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}" target="_blank" rel="sponsored nofollow noopener">${H(t.name)} ↗</a></h3><p>${H(t.verdict)}</p><div class="price">${H(t.price)}</div><div style="margin-top:8px">${t.tags.map(x=>`<span class="tag">${H(x)}</span>`).join('')}</div></div>`;
fetch('/tools.json').then(r=>r.json()).then(d=>{
 const el=document.getElementById('app'),p=document.body.dataset.page;
 if(p==='home'){
  const sel=document.getElementById('cat');d.categories.forEach(c=>sel.insertAdjacentHTML('beforeend',`<option value="${c.id}">${c.name}</option>`));
  const draw=()=>{const q=document.getElementById('q').value.toLowerCase(),cv=sel.value,free=document.getElementById('free').checked;
   el.innerHTML=d.categories.filter(c=>!cv||c.id===cv).map(c=>{const ts=c.tools.map((t,i)=>[t,i]).filter(([t])=>(!q||(t.name+t.verdict+t.tags.join(' ')).toLowerCase().includes(q))&&(!free||t.tags.includes('free-tier')||/free/i.test(t.price)));
    return ts.length?`<section class="cat"><h2><a href="/category/${c.id}.html">${c.name} →</a></h2><p class="sub">${H(c.q)}</p><div class="grid">${ts.map(([t,i])=>card(t,i)).join('')}</div></section>`:''}).join('')||'<p>No matches.</p>'};
  ['q','cat','free'].forEach(i=>document.getElementById(i).addEventListener('input',draw));draw();
  document.getElementById('cats').innerHTML=d.categories.map(c=>`<a class="card" style="text-decoration:none;color:inherit" href="/category/${c.id}.html"><b>${c.name}</b><div class="sub">${c.tools.length} ranked picks</div></a>`).join('');
 }else if(p==='category'){
  const c=d.categories.find(c=>c.id===new URLSearchParams(location.search).get('c'))||d.categories[0];document.title=c.name+' · VibeStack Rankings';
  el.innerHTML=`<h1>${c.name}</h1><p class="sub">${H(c.q)} Updated ${d.updated}.</p><div class="grid">${c.tools.map((t,i)=>card(t,i)).join('')}</div><h3>Other categories</h3><p>${d.categories.map(x=>`<a href="/category/${x.id}.html">${x.name}</a>`).join(' · ')}</p>`;
 }else if(p==='new'){
  el.innerHTML=d.news.map(n=>`<div class="card" style="margin-bottom:10px"><span class="tag">${n.date}</span><h3 style="margin:.4em 0">${H(n.title)}</h3><a href="${n.url}" target="_blank" rel="noopener">Source: ${H(n.source)} ↗</a></div>`).join('');
 }});
