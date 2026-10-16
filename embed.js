/* VibeStack Rankings embeddable "Top picks" widget. Usage: <div data-vibestack-embed="coding-agents" data-count="3" data-theme="dark"></div><script src="https://vibestack-rankings.vercel.app/embed.js" async></script> */
(function(){var B='https://vibestack-rankings.vercel.app';
var H=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})};
var sl=function(s){return s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')};
function render(el,d){var c=d.categories.filter(function(x){return x.id===el.getAttribute('data-vibestack-embed')})[0]||d.categories[0];
 var n=Math.max(1,Math.min(5,parseInt(el.getAttribute('data-count')||'3',10)||3)),L=el.getAttribute('data-theme')==='light';
 var bg=L?'#ffffff':'#131722',fg=L?'#14161c':'#e6e8ee',mu=L?'#5b6170':'#9aa3b8',bd=L?'#dfe3ea':'#222838',ln=L?'#2457d6':'#8ab4ff',u='?utm_source=embed&utm_medium=widget&utm_campaign='+c.id;
 el.innerHTML='<div style="font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:'+bg+';color:'+fg+';border:1px solid '+bd+';border-radius:14px;padding:14px 16px;max-width:420px">'
 +'<div style="font-weight:700;font-size:16px;margin-bottom:8px">Top picks for '+H(c.name)+'</div><ol style="margin:0;padding-left:20px">'
 +c.tools.slice(0,n).map(function(t){return '<li style="margin:6px 0"><a href="'+B+'/tools/'+sl(t.name)+'.html'+u+'" target="_blank" rel="noopener" style="color:'+ln+';font-weight:600;text-decoration:none">'+H(t.name)+'</a><div style="color:'+mu+';font-size:13px">'+H(t.verdict)+'</div></li>'}).join('')
 +'</ol><div style="margin-top:10px;font-size:12px;color:'+mu+'">Rankings by <a href="'+B+'/category/'+c.id+'.html'+u+'" target="_blank" rel="noopener" style="color:'+ln+'">VibeStack Rankings</a></div></div>'}
function run(){var els=document.querySelectorAll('[data-vibestack-embed]');if(!els.length)return;
 (window.__vsEmbed=window.__vsEmbed||fetch(B+'/tools.json').then(function(r){return r.json()})).then(function(d){for(var i=0;i<els.length;i++)render(els[i],d)})}
window.VibeStackEmbed=run;document.readyState==='loading'?document.addEventListener('DOMContentLoaded',run):run();
if(location.pathname==='/embed.html'){document.addEventListener('DOMContentLoaded',function(){var g=function(i){return document.getElementById(i)};if(!g('emb-cat'))return;
 var up=function(){var a=g('emb-cat').value,n=g('emb-n').value,t=g('emb-th').value,code='<div data-vibestack-embed="'+a+'" data-count="'+n+'"'+(t==='light'?' data-theme="light"':'')+'></div>\n<script src="'+B+'/embed.js" async></'+'script>';
  g('emb-code').textContent=code;g('emb-prev').innerHTML=code.split('\n')[0];run()};
 ['emb-cat','emb-n','emb-th'].forEach(function(i){g(i).addEventListener('change',up)});
 g('emb-copy').addEventListener('click',function(){navigator.clipboard&&navigator.clipboard.writeText(g('emb-code').textContent).then(function(){g('emb-copy').textContent='Copied ✓'})});up()})}
})();
