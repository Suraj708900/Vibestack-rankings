"""/checkout.html (UPI QR + deep link, PayPal link, order form) and /admin-orders.html. Called from build.py."""
import json,os
def run(g):
    page,E,SITE=g['page'],g['E'],g['SITE']; NI='<meta name="robots" content="noindex, nofollow">'
    C=json.load(open('data/products-config.json'))
    pub={'upi':C['upi'],'paypal_email':C['paypal_email'],'paypal_link':C['paypal_link'],'products':{k:{x:v.get(x) for x in ('name','price','price_usd','unit','includes')} for k,v in C['products'].items()}}
    CSS=('<style>.co{max-width:760px;margin:0 auto}.co-tabs{display:flex;gap:8px;margin:14px 0}.co-tabs button{flex:1;padding:12px;border-radius:12px;border:1px solid #2a3142;background:transparent;color:inherit;font:inherit;font-weight:700;cursor:pointer}'
         '.co-tabs button.on{border-color:#7c5cff;background:#7c5cff22}.co-pane{display:none}.co-pane.on{display:block}.co-qr{background:#fff;padding:12px;border-radius:14px;width:min(260px,80vw);margin:10px auto}.co-qr svg{width:100%;height:auto;display:block}'
         '.co-amt{font-size:1.6em;font-weight:800}.co-id{font-family:ui-monospace,monospace}.af{display:grid;gap:12px}.af label{display:grid;gap:6px;font-weight:600}.af input,.af select{padding:11px 12px;border-radius:10px;border:1px solid #2a3142;background:#0f131c;color:inherit;font:inherit}'
         '.af button{padding:12px;border-radius:10px;border:0;background:#7c5cff;color:#fff;font-weight:700;cursor:pointer}.af-msg{min-height:1.2em}.co-ok{border-color:#16a34a88}html[data-theme=light] .af input,html[data-theme=light] .af select{background:#fff;border-color:#dfe3ea}'
         '.adm table{width:100%;border-collapse:collapse;font-size:.9em}.adm td,.adm th{border-bottom:1px solid #2a3142;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere}.adm .lnk{font-size:.8em}</style>')
    body=(CSS+'<div class="co"><p class="sub"><a href="/products.html">Products</a> › Checkout</p><div id="co-app" class="card"><p>Loading…</p></div>'
      '<section class="card" id="co-form-card" style="margin-top:14px" hidden><h2>2. Confirm your payment</h2><p class="sub">After paying, enter the transaction ID so we can match your payment. We verify it manually and email your download link.</p>'
      '<form id="co-form" class="af" novalidate><label>Payment method<select name="method"><option value="upi">UPI</option><option value="paypal">PayPal</option></select></label>'
      '<label>Name<input name="name" required maxlength="80" autocomplete="name"></label><label>Email (download link is sent here)<input type="email" name="email" required maxlength="254" autocomplete="email"></label>'
      '<label><span id="co-utr-l">UPI transaction reference (UTR)</span><input name="utr" required maxlength="22" autocomplete="off" inputmode="text" placeholder="e.g. 412345678901"></label>'
      '<input name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">'
      '<button type="submit">Submit payment details</button><p class="af-msg sub" role="status"></p></form></section>'
      '<p class="sub">Questions? Email <a href="mailto:kamdevsuraj03@gmail.com">kamdevsuraj03@gmail.com</a> with your order ID. See our <a href="/refund">refund & delivery policy</a>.</p></div>'
      '<script src="/vendor/qrcode.js"></script><script>window.VS_PAY='+json.dumps(pub).replace('</','<\\/')+';</script><script src="/checkout.js" defer></script>')
    page('/checkout.html',f'Checkout · {SITE}','Pay for a VibeStack Rankings product by UPI or PayPal.',body,extra=NI)
    adm=(CSS+'<div class="adm"><h1>Orders</h1><p class="sub">Enter the admin token (kept in this browser tab only).</p><form id="adm-login" class="af" style="max-width:420px"><input type="password" id="adm-tok" placeholder="Admin token" autocomplete="off"><button>Load orders</button></form>'
      '<p id="adm-msg" class="sub"></p><div id="adm-list"></div></div><script src="/admin-orders.js" defer></script>')
    page('/admin-orders.html',f'Orders admin · {SITE}','Orders admin.',adm,extra=NI)
