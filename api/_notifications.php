<?php
// Scoped transactional notifications. Existing newsletter/global mail settings are untouched.
if (!defined('VS_API')) { http_response_code(404); exit; }
require_once __DIR__ . '/_mail.php';
function auf_notice_dir(): string {
  $p=vs_storage().(defined('AUF_CHECKOUT_SANDBOX')?'/checkout-qa/notices':'/transaction-notices');
  if(!is_dir($p)&&!mkdir($p,0700,true)&&!is_dir($p))throw new RuntimeException('Notification storage unavailable');
  return $p;
}
function auf_notice_queue(string $key,array $message): string {
  $id=hash('sha256',$key);$p=auf_notice_dir().'/'.$id.'.json';
  $f=@fopen($p,'x');if($f){fwrite($f,json_encode(['message'=>$message,'state'=>'pending','attempts'=>0,'next'=>0,'created'=>gmdate('c')],JSON_UNESCAPED_SLASHES));fclose($f);chmod($p,0600);}
  elseif(!is_file($p))throw new RuntimeException('Notification could not be queued');
  return $id;
}
function auf_notice_send(array $m): array {
  if(defined('AUF_CHECKOUT_SANDBOX')&&!defined('AUF_REAL_MAIL_TEST'))return ['ok'=>false,'code'=>0,'skipped'=>'sandbox'];
  $to=vs_mail_addr((string)($m['to']??''));$from=trim((string)vs_cfg('MAIL_FROM'));
  if($to===''||vs_mail_addr($from)==='')return ['ok'=>false,'code'=>0,'skipped'=>'invalid sender or recipient'];
  if(!vs_mail_allowed($to)||vs_cfg('MAIL_DRY_RUN',false))return ['ok'=>false,'code'=>0,'skipped'=>'recipient restricted or dry run'];
  if((string)vs_cfg('RESEND_API_KEY')==='')return ['ok'=>false,'code'=>0,'skipped'=>'mail provider not configured'];
  $payload=['from'=>$from,'to'=>[$to],'subject'=>mb_substr(str_replace(["\r","\n"],' ',(string)$m['subject']),0,200),'text'=>(string)$m['text']];
  if(!empty($m['html']))$payload['html']=$m['html'];
  $rt=vs_mail_addr((string)($m['reply_to']??'contact@aiuseflow.com'));if($rt!=='')$payload['reply_to']=[$rt];
  // Provider-side idempotency prevents duplicate delivery if a request times out after acceptance.
  $headers=['Authorization: Bearer '.(string)vs_cfg('RESEND_API_KEY'),'Content-Type: application/json','Idempotency-Key: auf-'.hash('sha256',(string)($m['key']??json_encode($payload)))];
  $ch=curl_init('https://api.resend.com/emails');curl_setopt_array($ch,[CURLOPT_POST=>true,CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>12,CURLOPT_CONNECTTIMEOUT=>5,CURLOPT_HTTPHEADER=>$headers,CURLOPT_POSTFIELDS=>json_encode($payload,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)]);
  $r=curl_exec($ch);$code=(int)curl_getinfo($ch,CURLINFO_HTTP_CODE);curl_close($ch);$j=is_string($r)?json_decode($r,true):null;
  $ok=$code>=200&&$code<300&&!empty($j['id']);vs_mail_log(['kind'=>$m['kind']??'transactional','to'=>$to,'ok'=>$ok,'code'=>$code]);
  return ['ok'=>$ok,'code'=>$code,'id'=>$ok?$j['id']:null];
}
function auf_notice_flush(string $id): array {
  if(!preg_match('/^[a-f0-9]{64}$/',$id))return ['state'=>'unavailable'];
  $p=auf_notice_dir().'/'.$id.'.json';$f=@fopen($p,'r+');if(!$f)return ['state'=>'unavailable'];
  if(!flock($f,LOCK_EX)){fclose($f);return ['state'=>'pending'];}$j=json_decode(stream_get_contents($f),true);
  if(!is_array($j)){flock($f,LOCK_UN);fclose($f);return ['state'=>'unavailable'];}
  if($j['state']!=='sent'&&($j['next']??0)<=time()&&($j['attempts']??0)<8){
    $r=auf_notice_send($j['message']);$j['attempts']++;$j['last_code']=$r['code']??0;$j['state']=!empty($r['ok'])?'sent':'pending';$j['provider_id']=$r['id']??null;$j['next']=time()+min(3600,60*(2**min($j['attempts'],6)));
    if(defined('AUF_CHECKOUT_SANDBOX')&&!defined('AUF_REAL_MAIL_TEST'))$j['state']='sandbox';
    rewind($f);ftruncate($f,0);fwrite($f,json_encode($j,JSON_UNESCAPED_SLASHES));fflush($f);
  }
  flock($f,LOCK_UN);fclose($f);return ['state'=>$j['state'],'provider_id'=>$j['provider_id']??null];
}
function auf_notice(string $key,array $m): array { $m['key']=$key;return auf_notice_flush(auf_notice_queue($key,$m)); }

function auf_owner_notice(string $key,array $message): array {
 $out=[];foreach(['contact@aiuseflow.com','kamdevsuraj03@gmail.com'] as $to){$m=$message;$m['to']=$to;$out[$to]=auf_notice($key.':'.hash('sha256',$to),$m);}
 $states=array_column($out,'state');return ['state'=>count(array_filter($states,fn($s)=>$s==='sent'))===count($states)?'sent':(count(array_filter($states,fn($s)=>$s==='sandbox'))===count($states)?'sandbox':'pending')];
}
