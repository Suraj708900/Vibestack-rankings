<?php
require __DIR__.'/_boot.php';require __DIR__.'/_commerce.php';
header('Cache-Control: no-store');header('X-Robots-Tag: noindex');
if(vs_method()!=='POST')vs_send_json(405,['error'=>'Method not allowed.']);
if(!auf_origin_ok())vs_send_json(403,['error'=>'Forbidden.']);
$b=vs_body();$action=(string)($b['action']??'');
if(!in_array($action,['create','proof','status'],true))vs_send_json(400,['error'=>'Unknown request.']);
if(vs_rate_limited('checkout-v2-'.$action,$action==='status'?120:10,3600))vs_send_json(429,['error'=>'Too many attempts. Please try again later.']);
if($action==='create'){
 $name=mb_substr(trim(str_replace(["\r","\n"],' ',(string)($b['name']??''))),0,80);$email=vs_norm_email($b['email']??'');$slug=(string)($b['product']??'');$c=vs_products_cfg();$p=$c['products'][$slug]??null;$method=(string)($b['method']??'upi');$nonce=(string)($b['request_id']??'');
 if(!empty($b['company']))vs_send_json(400,['error'=>'Could not create this order. Please contact support.']);
 if(!$p||!in_array($method,['upi','paypal'],true)||!preg_match('/^[a-f0-9]{32}$/',$nonce))vs_send_json(400,['error'=>'Choose a valid product and payment method.']);
 if(mb_strlen($name)<2||!vs_valid_email($email))vs_send_json(400,['error'=>'Enter your name and a valid email.']);
 $secret=(string)vs_cfg('AUTH_SECRET');if(strlen($secret)<24)vs_send_json(503,['error'=>'Checkout is temporarily unavailable. Please contact support.']);
 $id='VS'.strtoupper(substr(hash_hmac('sha256','order:'.$nonce,$secret),0,12));$key=hash_hmac('sha256','tracking:'.$nonce,$secret);$o=auf_order_load($id);
 if(!$o){$o=['id'=>$id,'product'=>$slug,'product_name'=>$p['name'],'name'=>$name,'email'=>$email,'method'=>$method,'amount'=>$method==='upi'?$p['price']:$p['price_usd'],'currency'=>$method==='upi'?'INR':'USD','amount_inr'=>$p['price'],'amount_usd'=>$p['price_usd'],'unit'=>$p['unit']??'','file'=>$p['file']??'','status'=>'pending','payment_stage'=>'awaiting_payment','utr'=>'','track_hash'=>hash('sha256',$key),'created'=>vs_iso_now()];if(!auf_order_save($o,false))vs_send_json(503,['error'=>'Could not save your order. Please retry; no payment is required yet.']);}
 if(!auf_access($o,$key)||$o['product']!==$slug)vs_send_json(409,['error'=>'This checkout session is no longer valid. Please start again.']);
 if(empty($o['notifications'])){$o['notifications']=auf_order_notice($o,$key,'created');auf_order_save($o,true);}
 vs_send_json(200,auf_public_order($o,$key,true)+['access_key'=>$key]);
}
$id=strtoupper((string)($b['id']??''));$key=(string)($b['access_key']??'');$o=auf_order_load($id);
if(!$o||!auf_access($o,$key))vs_send_json(404,['error'=>'Order not found or access link invalid.']);
if($action==='status')vs_send_json(200,auf_public_order($o,$key));
if($o['status']==='paid')vs_send_json(200,auf_public_order($o,$key));
$utr=strtoupper(preg_replace('/\s+/','',(string)($b['utr']??'')));$method=(string)($b['method']??$o['method']);
if(!in_array($method,['upi','paypal'],true))vs_send_json(400,['error'=>'Choose a payment method.']);
if(($method==='upi'&&!preg_match('/^\d{12}$/',$utr))||($method==='paypal'&&!preg_match('/^[A-Z0-9]{17}$/',$utr)))vs_send_json(400,['error'=>$method==='upi'?'Enter the 12-digit UPI transaction reference (UTR).':'Enter the 17-character PayPal transaction ID.']);
$lock=auf_notice_dir().'/order-'.hash('sha256',$id).'.lock';$fp=fopen($lock,'c');if(!$fp||!flock($fp,LOCK_EX))vs_send_json(503,['error'=>'Please retry shortly.']);
$o=auf_order_load($id);
if(($o['payment_stage']??'')==='submitted'){
 if($o['utr']!==$utr||$o['method']!==$method)vs_send_json(409,['error'=>'Payment details were already submitted. Contact support with your tracking ID to correct them.']);
 vs_send_json(200,auf_public_order($o,$key));
}
$o['method']=$method;$o['amount']=$method==='upi'?$o['amount_inr']:$o['amount_usd'];$o['currency']=$method==='upi'?'INR':'USD';$o['utr']=$utr;$o['payment_stage']='submitted';$o['submitted_at']=vs_iso_now();
if(!auf_order_save($o,true))vs_send_json(503,['error'=>'Could not save payment details. Retry with the same tracking ID; do not pay again.']);
$o['notifications']=auf_order_notice($o,$key,'submitted');auf_order_save($o,true);flock($fp,LOCK_UN);fclose($fp);vs_send_json(200,auf_public_order($o,$key));
