/* Product engagement (preview build): real views, likes and comments via /api/product. Counts come only from the server; nothing is seeded.
   All user text is inserted with textContent (no HTML). Avatars: initials on a gradient derived from a server-side one-way hash (no external service). */
(function(){
  var API='/api/product';
  function el(t,c,txt){var e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e}
  function n(x,one,many){return x+' '+(x===1?one:many)}
  function post(o){return fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(o)}).then(function(r){return r.json().catch(function(){return{}}).then(function(j){j._s=r.status;return j})})}
  function setK(root,k,v){root.querySelectorAll('[data-k="'+k+'"]').forEach(function(e){e.textContent=v})}
  // listing: counts per product card
  var cards=document.querySelectorAll('.pe-stats[data-pe-slug]');
  if(cards.length){fetch(API+'?all=1',{credentials:'same-origin'}).then(function(r){return r.ok?r.json():null}).then(function(j){if(!j||!j.counts)return;
    cards.forEach(function(c){var x=j.counts[c.dataset.peSlug];if(!x)return;setK(c,'views','👁 '+n(x.views,'view','views'));setK(c,'likes','♥ '+n(x.likes,'like','likes'));setK(c,'comments','💬 '+n(x.comments,'comment','comments'))})}).catch(function(){})}
  var box=document.getElementById('pe'); if(!box)return;
  var slug=box.dataset.peSlug, list=box.querySelector('.pe-list'), like=box.querySelector('.pe-like'), f=box.querySelector('.pe-f'), msg=box.querySelector('.pe-msg'), t0=Date.now(), stars=0;
  function initials(name){var p=String(name).trim().split(/\s+/);return ((p[0]||'?').charAt(0)+(p.length>1?p[p.length-1].charAt(0):'')).toUpperCase()}
  function avatar(c){var h=parseInt(c.av.slice(0,4),16)%360,h2=(h+35+parseInt(c.av.slice(4,6),16)%90)%360,a=el('span','pe-av',initials(c.name));
    a.style.background='linear-gradient(135deg,hsl('+h+' 72% 52%),hsl('+h2+' 70% 38%))';a.setAttribute('aria-hidden','true');return a}
  function fmt(ts){try{return new Date(ts).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'})}catch(e){return ts.slice(0,10)}}
  function render(d){
    setK(box,'views',n(d.views,'view','views'));setK(box,'likes',String(d.likes));setK(box,'count',n(d.count,'comment','comments'));
    setK(box,'rating',d.rating?('★ '+d.rating.avg+' / 5 from '+n(d.rating.count,'verified buyer','verified buyers')):'');
    like.disabled=false;like.setAttribute('aria-pressed',d.liked?'true':'false');like.querySelector('span').textContent=d.liked?'Liked':'Like';
    list.textContent='';
    if(!d.comments.length){list.appendChild(el('li','sub','No comments yet. Be the first to comment.'));return}
    d.comments.forEach(function(c){var li=el('li','pe-c'),b=el('div'),m=el('div','pe-meta');li.appendChild(avatar(c));
      m.appendChild(el('b',null,c.name));if(c.verified)m.appendChild(el('span','pe-vb','Verified buyer'));
      if(c.stars){var s=el('span','pe-st','★★★★★'.slice(0,c.stars)+'☆☆☆☆☆'.slice(0,5-c.stars));s.setAttribute('aria-label',c.stars+' out of 5 stars');m.appendChild(s)}
      m.appendChild(el('span',null,fmt(c.ts)));
      if(c.mine){var x=el('button','pe-del','Delete');x.type='button';x.onclick=function(){if(!confirm('Delete your comment?'))return;post({action:'delete_comment',slug:slug,id:c.id}).then(load)};m.appendChild(x)}
      b.appendChild(m);b.appendChild(el('p',null,c.body));li.appendChild(b);list.appendChild(li)})}
  function load(){return fetch(API+'?slug='+encodeURIComponent(slug),{credentials:'same-origin'}).then(function(r){return r.json()}).then(render).catch(function(){list.textContent='';list.appendChild(el('li','sub','Comments are unavailable right now.'))})}
  var vk='pe_v_'+slug+'_'+new Date().toISOString().slice(0,10);
  (function(){var seen=false;try{seen=sessionStorage.getItem(vk)}catch(e){}
    (seen?Promise.resolve():post({action:'view',slug:slug}).then(function(){try{sessionStorage.setItem(vk,'1')}catch(e){}})).catch(function(){}).then(load)})();
  like.onclick=function(){var on=like.getAttribute('aria-pressed')==='true';like.disabled=true;post({action:on?'unlike':'like',slug:slug}).then(function(j){if(j.ok){like.setAttribute('aria-pressed',j.liked?'true':'false');like.querySelector('span').textContent=j.liked?'Liked':'Like';setK(box,'likes',String(j.likes))}like.disabled=false})};
  var sb=f.querySelectorAll('.pe-stars [data-v]'),clr=f.querySelector('.pe-clr'),buyer=f.querySelectorAll('.pe-buyer');
  function setStars(v){stars=v;sb.forEach(function(b){var on=+b.dataset.v<=v;b.classList.toggle('on',on);b.setAttribute('aria-checked',+b.dataset.v===v?'true':'false')});clr.hidden=!v;buyer.forEach(function(x){x.hidden=!v})}
  sb.forEach(function(b){b.onclick=function(){setStars(+b.dataset.v)}});clr.onclick=function(){setStars(0)};
  f.querySelector('.pe-forget').onclick=function(){if(!confirm('Remove your like, views and comments on this product?'))return;post({action:'forget',slug:slug}).then(function(j){try{sessionStorage.removeItem(vk)}catch(e){}msg.textContent=j.ok?'Removed '+(j.removed||0)+' item(s).':(j.error||'Could not remove.');load()})};
  f.onsubmit=function(e){e.preventDefault();var fd=new FormData(f),btn=f.querySelector('[type=submit]');
    var o={action:'comment',slug:slug,name:fd.get('name'),body:fd.get('body'),website:fd.get('website'),t:Date.now()-t0};
    if(stars){o.stars=stars;o.order_id=fd.get('order_id');o.email=fd.get('email')}
    btn.disabled=true;msg.textContent='Posting…';
    post(o).then(function(j){btn.disabled=false;if(j.ok){msg.textContent=j.verified?'Thanks! Your verified review is live.':'Thanks! Your comment is live.';f.reset();setStars(0);load()}else msg.textContent=j.error||'Could not post. Please try again.'}).catch(function(){btn.disabled=false;msg.textContent='Network error. Please try again.'})};
})();
