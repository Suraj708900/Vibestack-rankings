/* Accounts: nav state, Save hearts, login/signup/account pages. Talks to /api/auth/* and /api/account. */
(function(){
var me=fetch('/api/auth/me',{credentials:'same-origin',cache:'no-store'}).then(function(r){return r.json()}).then(function(d){return d.user}).catch(function(){return null});
window.VSAuth=me;var saved=new Set();
function H(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function post(u,b,m){return fetch(u,{method:m||'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(b||{})}).then(function(r){return r.json().then(function(j){j._s=r.status;return j})})}
function next(){var n=new URLSearchParams(location.search).get('next')||'/account';return /^\/(?!\/)/.test(n)?n:'/account'}
// nav
me.then(function(u){var nav=document.querySelector('header nav');if(!nav)return;var a=nav.querySelector('.nav-auth');if(!a){a=document.createElement('a');a.className='nav-auth';nav.insertBefore(a,nav.querySelector('.sx-btn'))}
 if(u){a.href='/account';a.textContent='Account';var o=document.createElement('a');o.href='#';o.className='nav-auth';o.textContent='Log out';o.onclick=function(e){e.preventDefault();post('/api/auth/logout').then(function(){location.href='/'})};a.after(o)}
 else{a.href='/login?next='+encodeURIComponent(location.pathname);a.textContent='Log in'}});
// save hearts
function slugOf(a){var m=(a.getAttribute('href')||'').match(/^\/(?:t|tools)\/([a-z0-9-]+)\.html/);return m&&m[1]}
function heart(slug){var b=document.createElement('button');b.type='button';b.className='vs-heart';b.dataset.slug=slug;paint(b);b.onclick=function(e){e.preventDefault();e.stopPropagation();toggle(b)};return b}
function paint(b){var on=saved.has(b.dataset.slug);b.classList.toggle('on',on);b.setAttribute('aria-pressed',on);b.setAttribute('aria-label',(on?'Remove ':'Save ')+b.dataset.slug);b.title=on?'Saved to your account':'Save to your account';b.innerHTML=on?'&#9829;':'&#9825;'}
function toggle(b){me.then(function(u){if(!u){location.href='/login?next='+encodeURIComponent(location.pathname);return}
 var on=saved.has(b.dataset.slug);post('/api/account',{action:on?'unsave':'save',slug:b.dataset.slug}).then(function(d){if(d.saved){saved=new Set(d.saved);document.querySelectorAll('.vs-heart').forEach(paint)}})})}
function scan(root){(root||document).querySelectorAll('.card h3 a[href], .sc-card h3 a[href]').forEach(function(a){var s=slugOf(a),c=a.closest('.card');if(!s||!c||c.querySelector('.vs-heart'))return;c.classList.add('vs-hc');c.appendChild(heart(s))});
 var m=location.pathname.match(/^\/(?:t|tools)\/([a-z0-9-]+)\.html$/),h1=document.querySelector('main h1');if(m&&h1&&!h1.querySelector('.vs-heart')){var b=heart(m[1]);b.classList.add('inline');h1.appendChild(b)}}
me.then(function(u){if(u)saved=new Set(u.saved||[]);scan();var g=document.getElementById('dg');if(g&&window.MutationObserver)new MutationObserver(function(){scan(g)}).observe(g,{childList:true})});
// forms
function form(id,fn){var f=document.getElementById(id);if(!f)return;var msg=f.querySelector('.af-msg');f.addEventListener('submit',function(e){e.preventDefault();var d={};new FormData(f).forEach(function(v,k){d[k]=v});var btn=f.querySelector('button');btn.disabled=true;msg.textContent='';fn(d).then(function(r){btn.disabled=false;if(r&&r.error)msg.textContent=r.error})})}
form('signup-form',function(d){if(d.password!==d.confirm)return Promise.resolve({error:'Passwords do not match.'});return post('/api/auth/signup',d).then(function(r){if(r.ok)location.href=next();return r})});
form('login-form',function(d){return post('/api/auth/login',d).then(function(r){if(r.ok)location.href=next();return r})});
var acc=document.getElementById('account-app');
if(acc){fetch('/api/account',{credentials:'same-origin',cache:'no-store'}).then(function(r){if(r.status===401){location.href='/login?next=/account';return}return r.json()}).then(function(u){if(!u)return;
 acc.innerHTML='<section class="card"><h2>Profile</h2><p><b>Name:</b> '+H(u.name)+'</p><p><b>Email:</b> '+H(u.email)+'</p><p class="sub">Member since '+H(u.created.slice(0,10))+'</p><p><button type="button" id="acc-logout">Log out</button></p></section>'
 +'<section class="card" style="margin-top:14px"><h2>Saved tools ('+u.saved.length+')</h2>'+(u.saved.length?'<ul class="acc-saved">'+u.saved.map(function(s){return'<li><a href="/t/'+H(s)+'.html">'+H(s)+'</a> <button type="button" class="s" data-un="'+H(s)+'">Remove</button></li>'}).join('')+'</ul>':'<p class="sub">Tap the &#9825; on any tool card to save it here.</p>')+'</section>'
 +'<details class="card" style="margin-top:14px"><summary>Delete account</summary><form id="acc-del" class="af"><label>Confirm password<input type="password" name="password" required autocomplete="current-password"></label><button type="submit">Delete my account</button><p class="af-msg sub" role="alert"></p></form></details>';
 document.getElementById('acc-logout').onclick=function(){post('/api/auth/logout').then(function(){location.href='/'})};
 acc.querySelectorAll('[data-un]').forEach(function(b){b.onclick=function(){post('/api/account',{action:'unsave',slug:b.dataset.un}).then(function(){b.parentNode.remove()})}});
 document.getElementById('acc-del').onsubmit=function(e){e.preventDefault();if(!confirm('Delete your account permanently?'))return;post('/api/account',{password:this.password.value},'DELETE').then(function(r){if(r.deleted)location.href='/';else e.target.querySelector('.af-msg').textContent=r.error||'Could not delete.'})}})}
})();
