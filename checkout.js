(function(){var C=window.VS_PAY,app=document.getElementById('co-app');if(!C||!app)return;
var q=new URLSearchParams(location.search),slug=q.get('p'),p=C.products[slug];
function H(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
if(!p){app.innerHTML='<h1>Product not found</h1><p><a href="/products.html">See all products</a></p>';return}
var key='vs-order-'+slug,id=sessionStorage.getItem(key);
if(!/^VS[0-9A-Z]{6,14}$/.test(id||'')){var r='',a='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';var b=new Uint8Array(4);crypto.getRandomValues(b);for(var i=0;i<4;i++)r+=a[b[i]%a.length];id='VS'+Date.now().toString(36).toUpperCase()+r;sessionStorage.setItem(key,id)}
var inr=p.price.toFixed(2),usd=String(p.price_usd);
var upi='upi://pay?pa='+encodeURIComponent(C.upi.pa)+'&pn='+encodeURIComponent(C.upi.pn)+'&am='+inr+'&cu=INR&tn='+encodeURIComponent(id);
var pp=C.paypal_link.replace('{email}',encodeURIComponent(C.paypal_email)).replace('{item}',encodeURIComponent(p.name+' ('+id+')')).replace('{usd}',encodeURIComponent(usd)).replace('{order}',encodeURIComponent(id));
var qr='';try{var Q=qrcode(0,'M');Q.addData(upi);Q.make();qr=Q.createSvgTag({cellSize:6,margin:2,scalable:true})}catch(e){}
var m=q.get('m')==='paypal'?'paypal':'upi';
app.innerHTML='<h1>'+H(p.name)+'</h1><p class="sub">'+H(p.includes||'')+' · Order ID <b class="co-id">'+H(id)+'</b></p>'
+'<p><span class="co-amt">₹'+H(p.price.toLocaleString('en-IN'))+'</span>'+(p.unit?' <span class="sub">'+H(p.unit)+'</span>':'')+' <span class="sub">by UPI · or $'+H(usd)+' USD by PayPal</span></p>'
+'<h2>1. Choose how to pay</h2><div class="co-tabs" role="tablist"><button type="button" data-m="upi">UPI (India)</button><button type="button" data-m="paypal">PayPal (international)</button></div>'
+'<div class="co-pane" data-p="upi"><p>Scan with any UPI app (GPay, PhonePe, Paytm, BHIM) or tap the button on your phone. Pay exactly <b>₹'+H(inr)+'</b> to <b>'+H(C.upi.pn)+'</b> (<span class="co-id">'+H(C.upi.pa)+'</span>).</p>'
+'<div class="co-qr" aria-label="UPI QR code">'+qr+'</div><p style="text-align:center"><a class="cta-aff" href="'+H(upi)+'">Pay with UPI — ₹'+H(inr)+'</a></p><p class="sub">The payment note carries your order ID '+H(id)+'. After paying, copy the 12-digit UTR / transaction ID from your UPI app.</p></div>'
+'<div class="co-pane" data-p="paypal"><p>Pay <b>$'+H(usd)+' USD</b> to <b>'+H(C.paypal_email)+'</b> on PayPal. USD price is set separately from the INR price.</p><p style="text-align:center"><a class="cta-aff" href="'+H(pp)+'" target="_blank" rel="noopener">Pay with PayPal — $'+H(usd)+' USD</a></p><p class="sub">Include order ID '+H(id)+' if PayPal asks for a note. After paying, copy the 17-character transaction ID from your PayPal receipt.</p></div>';
var fc=document.getElementById('co-form-card'),f=document.getElementById('co-form'),msg=f.querySelector('.af-msg'),lab=document.getElementById('co-utr-l');fc.hidden=false;
function setM(x){m=x;app.querySelectorAll('.co-tabs button').forEach(function(b){b.classList.toggle('on',b.dataset.m===x);b.setAttribute('aria-selected',b.dataset.m===x)});app.querySelectorAll('.co-pane').forEach(function(d){d.classList.toggle('on',d.dataset.p===x)});f.method.value=x;lab.textContent=x==='upi'?'UPI transaction reference (UTR)':'PayPal transaction ID';f.utr.placeholder=x==='upi'?'e.g. 412345678901':'e.g. 1AB23456CD789012E'}
app.querySelectorAll('.co-tabs button').forEach(function(b){b.onclick=function(){setM(b.dataset.m)}});f.method.onchange=function(){setM(f.method.value)};setM(m);
f.addEventListener('submit',function(e){e.preventDefault();var d={id:id,product:slug,method:f.method.value,name:f.name.value,email:f.email.value,utr:f.utr.value.replace(/\s+/g,''),company:f.company.value};
var btn=f.querySelector('button');btn.disabled=true;msg.textContent='Submitting…';
fetch('/api/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json().then(function(j){return[r.ok,j]})}).then(function(x){
if(x[0]){sessionStorage.removeItem(key);fc.classList.add('co-ok');fc.innerHTML='<h2>Payment received for verification</h2><p>You\u2019ll get your download link by email after confirmation. Order ID <b class="co-id">'+H(id)+'</b>. Keep it for your records.</p>'}
else{msg.textContent=x[1].error||'Could not submit. Please try again.';btn.disabled=false}}).catch(function(){msg.textContent='Network error, please try again.';btn.disabled=false})})})();
