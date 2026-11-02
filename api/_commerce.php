<?php
if (!defined('VS_API')) { http_response_code(404); exit; }
require_once __DIR__.'/_notifications.php';
function auf_order_load(string $id): ?array {
 if(!preg_match(VS_ORDER_RE,$id))return null;
 if(!defined('AUF_CHECKOUT_SANDBOX'))return vs_load_order($id);
 $p=vs_storage().'/checkout-qa/orders/'.$id.'.json';return is_file($p)?json_decode(file_get_contents($p),true):null;
}
function auf_order_save(array $o,bool $overwrite): bool {
 if(!defined('AUF_CHECKOUT_SANDBOX'))return vs_save_order($o,$overwrite);
 $d=vs_storage().'/checkout-qa/orders';if(!is_dir($d))mkdir($d,0700,true);$p=$d.'/'.$o['id'].'.json';
 if(!$overwrite&&is_file($p))return false;$ok=file_put_contents($p,json_encode($o),LOCK_EX)!==false;if($ok)chmod($p,0600);return $ok;
}
function auf_origin_ok(): bool {
 $origin=rtrim((string)($_SERVER['HTTP_ORIGIN']??''),'/');$host=(string)($_SERVER['HTTP_HOST']??'');
 return $origin!==''&&hash_equals('https://'.$host,$origin);
}
function auf_base(): string { return defined('AUF_CHECKOUT_SANDBOX')?'https://preview.aiuseflow.com/checkout-repair-v1':'https://aiuseflow.com'; }
function auf_tracking_link(string $id,string $key): string {return auf_base().'/order-status.html#id='.rawurlencode($id).'&key='.rawurlencode($key);}
function auf_access(array $o,string $key): bool {return preg_match('/^[a-f0-9]{64}$/',$key)&&!empty($o['track_hash'])&&hash_equals($o['track_hash'],hash('sha256',$key));}
function auf_order_notice(array $o,string $key,string $event): array {
 $paid=$event==='submitted';$status=$paid?'Payment details submitted — pending verification':'Order created — awaiting payment';
 $amt=($o['currency']==='INR'?'₹':'$').number_format((float)$o['amount'],2).' '.$o['currency'];$url=auf_tracking_link($o['id'],$key);
 $summary="Order / tracking ID: {$o['id']}\nProduct: {$o['product_name']}\nAmount: $amt\nMethod: {$o['method']}\nStatus: $status";
 if($paid)$summary.="\nTransaction reference: {$o['utr']}\nThis is a customer-supplied payment reference, not bank confirmation.";
 $owner=auf_owner_notice('order:'.$o['id'].':'.$event.':owner',['kind'=>'checkout-owner','to'=>'contact@aiuseflow.com','reply_to'=>$o['email'],'subject'=>'[AIUseFlow] '.$status.' ('.$o['id'].')','text'=>$summary."\nCustomer: {$o['name']}\nEmail: {$o['email']}\nCreated: {$o['created']}\n\nVerify payments in your bank or PayPal before marking the order paid in https://aiuseflow.com/admin-orders.html."]);
 $paras=['Hi '.$o['name'].',',$status.'.',$summary,$paid?'We saved your payment reference. We will verify the payment and email your download link after confirmation.':'Your order is saved. Return to checkout to make the payment, then submit the UPI UTR or PayPal transaction ID. No payment has been confirmed and no automatic subscription has been activated.','For help, reply to this email or contact contact@aiuseflow.com.'];
 $buyer=auf_notice('order:'.$o['id'].':'.$event.':buyer',['kind'=>'checkout-buyer','to'=>$o['email'],'subject'=>$status.' ('.$o['id'].')','text'=>vs_mail_text($paras,['Track your order',$url]),'html'=>vs_mail_html($status,$paras,['Track your order',$url])]);
 return ['owner'=>$owner['state'],'customer'=>$buyer['state']];
}
function auf_public_order(array $o,string $key,bool $payment=false): array {
 $state=$o['status']==='paid'?'paid':($o['payment_stage']??'awaiting_payment');$r=['ok'=>true,'id'=>$o['id'],'product'=>$o['product_name'],'amount'=>$o['amount'],'currency'=>$o['currency'],'unit'=>$o['unit']??'','status'=>$state,'tracking_url'=>auf_tracking_link($o['id'],$key),'notifications'=>$o['notifications']??[],'sandbox'=>defined('AUF_CHECKOUT_SANDBOX')];
 if($payment){$c=vs_products_cfg();$r['upi_url']='upi://pay?'.http_build_query(['pa'=>$c['upi']['pa'],'pn'=>$c['upi']['pn'],'am'=>number_format($o['amount_inr'],2,'.',''),'cu'=>'INR','tn'=>$o['id']]);
 $r['paypal_url']=strtr($c['paypal_link'],['{email}'=>rawurlencode($c['paypal_email']),'{item}'=>rawurlencode($o['product_name'].' ('.$o['id'].')'),'{usd}'=>rawurlencode((string)$o['amount_usd']),'{order}'=>rawurlencode($o['id'])]);$r['amount_inr']=$o['amount_inr'];$r['amount_usd']=$o['amount_usd'];}
 return $r;
}
