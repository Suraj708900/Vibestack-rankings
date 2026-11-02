import {tools,byId,categories,searchTools} from './catalog.mjs';
import {esc} from './core.mjs';

const root=document.querySelector('#auf-home-tools');
if(root){
 const q=document.querySelector('#auf-home-search'),grid=root.querySelector('[data-home-grid]'),count=root.querySelector('[data-home-count]'),more=root.querySelector('[data-home-more]'),panel=document.querySelector('#auf-home-workspace'),frame=panel.querySelector('iframe'),status=panel.querySelector('[data-workspace-status]'),dialog=document.querySelector('#auf-switch-dialog');
 let category='all',mode='all',expanded=false,selected=null,pending=null,observer=null,resize=null,scheduled=false;
 const read=(k,d)=>{try{return JSON.parse(localStorage.getItem('auf-v4-'+k))??d}catch{return d}};
 const save=(k,v)=>{try{localStorage.setItem('auf-v4-'+k,JSON.stringify(v))}catch{}};
 const favorites=()=>{const f=read('favorites',[]);return Array.isArray(f)?f.filter(id=>byId[id]):[]};
 const recent=()=>{const r=read('recent',[]);return Array.isArray(r)?r.filter(id=>byId[id]):[]};
 const card=t=>`<article class="auf-tool-card"><div class="auf-tool-top"><span class="auf-tool-symbol" data-kind="${t.category}" aria-hidden="true">${categories.find(c=>c[0]===t.category)[3]}</span><button class="auf-favorite" type="button" data-home-favorite="${t.id}" aria-label="${favorites().includes(t.id)?'Remove from':'Add to'} favorites: ${esc(t.name)}" aria-pressed="${favorites().includes(t.id)}">${favorites().includes(t.id)?'★':'☆'}</button></div><h3><a href="/tools/${t.id}/" data-home-open="${t.id}">${esc(t.name)}</a></h3><p>${esc(t.description)}</p><div class="auf-tool-bottom"><span>${t.category==='ai'?'AI / local resume':'On your device'}</span><a href="/tools/${t.id}/" data-home-open="${t.id}" aria-label="Use ${esc(t.name)} on this page">Use tool <span aria-hidden="true">↗</span></a></div></article>`;
 function render(){
  let found=searchTools(q.value,category);
  if(!q.value.trim()&&category==='all'){const picks=['photo-to-pdf','image-compressor','invoice-generator','merge-pdf','ai-resume','qr-code','photo-size-kb','json-formatter'];found.sort((a,b)=>{const rank=id=>picks.includes(id)?picks.indexOf(id):100;return rank(a.id)-rank(b.id)})}
  if(mode==='favorites')found=found.filter(t=>favorites().includes(t.id));
  if(mode==='recent')found=recent().map(id=>byId[id]).filter(t=>found.some(x=>x.id===t.id));
  const limit=expanded||q.value.trim()||category!=='all'||mode!=='all'?50:8;
  grid.innerHTML=found.length?found.slice(0,limit).map(card).join(''):`<div class="auf-empty"><h3>${mode==='favorites'?'Your favorites belong here':mode==='recent'?'Your next task starts here':'No matching tools yet'}</h3><p>${mode==='favorites'?'Use the star on any tool to keep it close.':mode==='recent'?'Open a tool and it will appear here on this device.':'Try “photo 50KB”, “invoice”, “merge PDF” or another task.'}</p></div>`;
  count.textContent=`${found.length} ${found.length===1?'tool':'tools'}${mode==='favorites'?' in your favorites':mode==='recent'?' recently used':' available'}`;
  more.hidden=found.length<=limit;more.textContent=`Show all ${found.length} tools`;
  root.querySelectorAll('[data-home-category]').forEach(b=>b.setAttribute('aria-pressed',String(category===b.dataset.homeCategory)));
  root.querySelectorAll('[data-home-mode]').forEach(b=>b.setAttribute('aria-pressed',String(mode===b.dataset.homeMode)));
 }
 function hasWork(){try{return !!frame.contentDocument?.querySelector('.result a[download]')||[...frame.contentDocument.querySelectorAll('input[type=file]')].some(e=>e.files.length)||[...frame.contentDocument.querySelectorAll('textarea,input[type=text],input[type=email]')].some(e=>e.value!==e.defaultValue)}catch{return false}}
 function withSwitch(action){if(selected&&hasWork()){pending=action;dialog.showModal();dialog.querySelector('[data-stay]').focus()}else action()}
 dialog.querySelector('[data-stay]').onclick=()=>{pending=null;dialog.close()};
 dialog.querySelector('[data-switch]').onclick=()=>{const action=pending;pending=null;dialog.close();action?.()};
 function fit(){if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;try{const h=Math.max(300,Math.min(2600,Math.ceil(frame.contentDocument.body.getBoundingClientRect().height)+12));if(Math.abs(frame.clientHeight-h)>3)frame.style.height=h+'px'}catch{}})}
 function prepareFrame(){
  observer?.disconnect();resize?.disconnect();
  try{
   const doc=frame.contentDocument;if(!doc||!doc.querySelector('#workspace'))throw Error('Workspace unavailable');
   const style=doc.createElement('style');style.textContent='html,body{min-height:0!important;background:#090a12!important;overflow-x:hidden}body{height:auto!important;display:flow-root;margin:0!important}body:before,.site-header,.site-footer,.stage-banner,.skip,.breadcrumb,.tool-heading,.tool-sidebar,.guide,.tool-page-bottom{display:none!important}main.shell{width:100%!important;margin:0!important;padding:10px!important}.tool-layout{display:block!important;margin:0!important}.workspace{border:0!important;padding:8px!important;box-shadow:none!important;background:transparent!important}.workspace:focus{outline:none}';doc.head.append(style);
   const check=()=>{if(doc.querySelector('#workspace form')&&!panel.classList.contains('is-ready')){status.textContent=byId[selected].category==='ai'?'Resume export can run locally. AI text is sent only after consent.':'Your files are processed in this browser. Download your result before switching tools.';frame.hidden=false;frame.removeAttribute('aria-busy');panel.classList.add('is-ready');render()}fit()};
   observer=new MutationObserver(check);observer.observe(doc.body,{subtree:true,childList:true});resize=new ResizeObserver(fit);resize.observe(doc.body);check();
   const guide=panel.querySelector('[data-workspace-guide]');guide.replaceChildren();doc.querySelectorAll('.tool-sidebar h2,.tool-sidebar p').forEach(el=>{const copy=document.createElement(el.tagName==='H2'?'h4':'p');copy.textContent=el.textContent;guide.append(copy)});
  }catch{status.textContent='This workspace could not load. Reload the page or use the tool’s direct link below.';panel.querySelector('[data-direct-tool]').hidden=false;}
 }
 frame.addEventListener('load',()=>{if(selected)prepareFrame()});
 function openTool(id,push=true){
  const t=byId[id];if(!t)return;selected=id;panel.hidden=false;panel.classList.remove('is-ready');panel.querySelector('[data-workspace-title]').textContent=t.name;panel.querySelector('[data-workspace-description]').textContent=t.description;panel.querySelector('[data-direct-tool]').href='/tools/'+id+'/';panel.querySelector('[data-direct-tool]').hidden=true;status.textContent='Loading '+t.name+'…';frame.setAttribute('aria-busy','true');frame.title=t.name+' — inline workspace';frame.hidden=true;frame.style.height='420px';
  panel.querySelector('[data-workspace-related]').innerHTML=tools.filter(x=>x.category===t.category&&x.id!==id).slice(0,3).map(x=>`<button type="button" data-home-open="${x.id}">${esc(x.name)} <span aria-hidden="true">↗</span></button>`).join('');
  frame.src=new URL((window.AUF_HOME_TOOL_BASE||'/tools/')+id+'/',location.origin).href;
  if(push)history.pushState(null,'','#use-tool/'+id);panel.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});panel.querySelector('[data-workspace-title]').focus({preventScroll:true});
 }
 document.addEventListener('click',e=>{
  const open=e.target.closest('[data-home-open]');if(open){e.preventDefault();const id=open.dataset.homeOpen;if(id!==selected)withSwitch(()=>openTool(id));return}
  const favorite=e.target.closest('[data-home-favorite]');if(favorite){const f=favorites(),id=favorite.dataset.homeFavorite;save('favorites',f.includes(id)?f.filter(x=>x!==id):[...f,id]);render();return}
  const task=e.target.closest('[data-home-query]');if(task){q.value=task.dataset.homeQuery;category='all';mode='all';render();root.scrollIntoView({behavior:'smooth'});return}
  const workflow=e.target.closest('[data-home-workflow]');if(workflow)withSwitch(()=>openTool(workflow.dataset.homeWorkflow));
 });
 root.querySelectorAll('[data-home-category]').forEach(b=>b.onclick=()=>{category=b.dataset.homeCategory;expanded=false;render()});root.querySelectorAll('[data-home-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.homeMode;expanded=false;render()});
 const showResults=()=>{root.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});const heading=document.querySelector('#auf-tools-title');heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true})};
 q.addEventListener('input',render);q.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();showResults()}});document.querySelector('[data-home-search-submit]').onclick=showResults;more.onclick=()=>{expanded=true;render()};
 panel.querySelector('[data-close-workspace]').onclick=()=>withSwitch(()=>{observer?.disconnect();resize?.disconnect();selected=null;frame.src='about:blank';panel.hidden=true;history.replaceState(null,'','#free-tools');q.focus()});
 const motion=document.querySelector('[data-home-motion]');function motionState(){const paused=read('motionPaused',false)===true;document.documentElement.classList.toggle('auf-motion-paused',paused);motion.setAttribute('aria-pressed',String(paused));motion.textContent=paused?'Resume motion':'Pause motion'}motion.onclick=()=>{save('motionPaused',read('motionPaused',false)!==true);motionState()};motionState();
 addEventListener('storage',e=>{if(['auf-v4-favorites','auf-v4-recent'].includes(e.key))render();if(e.key==='auf-v4-motionPaused')motionState()});addEventListener('pageshow',render);
 addEventListener('popstate',()=>{const id=location.hash.match(/^#use-tool\/([a-z0-9-]+)$/)?.[1];if(byId[id]&&id!==selected)withSwitch(()=>openTool(id,false))});
 render();const initial=location.hash.match(/^#use-tool\/([a-z0-9-]+)$/)?.[1];if(byId[initial])openTool(initial,false);
}
