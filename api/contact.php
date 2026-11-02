<?php
// POST /api/contact {name, email, subject, message, website (honeypot), elapsed (ms since page load), lang}
// 1) spam checks (honeypot, timing, per-IP rate limits)  2) store in SQLite contact_messages FIRST  3) notify the owner.
// Notify: when MAIL_VIA_RESEND is on (preview build), Resend sends the owner notification to OWNER_NOTIFY_TO (reply-to = visitor)
// plus an auto-acknowledgement to the visitor (max 1 per address per 24h); otherwise the old PHP mail() path to CONTACT_TO (skipped on STAGING).
// A message is never lost if mail fails: it stays in storage/vs.sqlite (status 'new', mailed 0).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_notifications.php';
require __DIR__ . '/_commerce.php';
if (vs_method() !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
if (!auf_origin_ok()) vs_send_json(403, ['error' => 'Forbidden.']);
$b = vs_body();
$fake = fn() => vs_send_json(200, ['ok' => true]); // bots get a success-looking reply and learn nothing
if (trim((string) ($b['website'] ?? '')) !== '') $fake();                      // honeypot filled
$elapsed = (int) ($b['elapsed'] ?? 0);
if ($elapsed < 3000 || $elapsed > 6 * 3600 * 1000) $fake();                     // too fast (script) or a stale tab
if (vs_is_bot()) $fake();
if (vs_rate_limited('contact', 3, 3600) || vs_rate_limited('contact-day', 8, 86400)) vs_send_json(429, ['error' => 'Too many messages. Please try again later.']);

$one = fn($k, $n) => mb_substr(trim(str_replace(["\r", "\n", "\0"], ' ', (string) ($b[$k] ?? ''))), 0, $n); // single-line fields: no header injection
$name = $one('name', 80);
$email = vs_norm_email($one('email', 254));
$subjects = ['general' => 'General question', 'listing' => 'Correct a listing', 'ads' => 'Advertising / sponsorship', 'partner' => 'Partnership', 'privacy' => 'Privacy / data request'];
$sk = (string) ($b['subject'] ?? 'general'); $subject = $subjects[$sk] ?? $subjects['general'];
$msg = trim(str_replace("\0", '', (string) ($b['message'] ?? '')));
$msg = mb_substr(preg_replace("/\r\n?/", "\n", $msg), 0, 5000);
$lang = (($b['lang'] ?? '') === 'hi') ? 'hi' : 'en';
if ($name === '' || !vs_valid_email($email) || mb_strlen($msg) < 10) vs_send_json(400, ['error' => $lang === 'hi' ? 'कृपया नाम, सही ईमेल और संदेश (कम से कम 10 अक्षर) भरें।' : 'Please add your name, a valid email and a message (at least 10 characters).']);
if (preg_match_all('#https?://#i', $msg) > 3) $fake();                          // link spam
// global safety valve so a flood can never fill the disk or the mailbox
try {
  $st = vs_db()->prepare('SELECT COUNT(*) FROM contact_messages WHERE ts >= ?'); $st->execute([time() - 86400]);
  if ((int) $st->fetchColumn() >= (int) vs_cfg('CONTACT_DAILY_CAP', 100)) vs_send_json(429, ['error' => 'We are receiving too many messages right now. Please try again tomorrow.']);
} catch (Throwable $e) { vs_fail500('contact cap: ' . $e->getMessage()); }

$id = 'C' . gmdate('ymdHis') . strtoupper(bin2hex(random_bytes(3)));
$iph = hash_hmac('sha256', vs_ip(), (string) vs_cfg('AUTH_SECRET', 'aiuseflow'));   // salted hash, never the raw IP
$ua = mb_substr((string) ($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 200);
try {
  if(defined('AUF_CHECKOUT_SANDBOX')) { $dir=vs_storage().'/checkout-qa/contacts';if(!is_dir($dir))mkdir($dir,0700,true);$path=$dir.'/'.$id.'.json';if(file_put_contents($path,json_encode(['id'=>$id,'name'=>$name,'email'=>$email,'subject'=>$subject,'body'=>$msg]),LOCK_EX)===false)throw new RuntimeException('Could not save');chmod($path,0600); } else {
  vs_db()->prepare('INSERT INTO contact_messages(id,ts,name,email,subject,body,lang,ip_hash,ua) VALUES(?,?,?,?,?,?,?,?,?)')
    ->execute([$id, time(), $name, $email, $subject, $msg, $lang, $iph, $ua]);
  }
} catch (Throwable $e) { vs_fail500('contact store: ' . $e->getMessage()); }

// Save-first delivery with a durable retry queue, scoped to requested transactional messages.
$owner=auf_owner_notice('contact:'.$id.':owner',['kind'=>'contact-owner','to'=>'contact@aiuseflow.com','reply_to'=>$email,'subject'=>'[AIUseFlow] '.$subject.' ('.$id.')','text'=>"New customer message\nReference: $id\nName: $name\nEmail: $email\nTopic: $subject\n\n$msg"]);
$customer=['state'=>'rate_limited'];
$st=vs_db()->prepare('SELECT COUNT(*) FROM contact_messages WHERE email=? AND ts>=?');$st->execute([$email,time()-86400]);
if((int)$st->fetchColumn()<=1){$paras=['Hi '.$name.',','We saved your message. Reference ID: '.$id,'Topic: '.$subject,'We usually reply within 2–3 working days. Reply to this email if you need to add information.'];$customer=auf_notice('contact:'.$id.':customer',['kind'=>'contact-ack','to'=>$email,'subject'=>'We received your message ('.$id.')','text'=>vs_mail_text($paras),'html'=>vs_mail_html('Message received',$paras)]);}
if(!defined('AUF_CHECKOUT_SANDBOX')){try{vs_db()->prepare('UPDATE contact_messages SET mailed=? WHERE id=?')->execute([$owner['state']==='sent'?1:0,$id]);}catch(Throwable $e){}}
vs_send_json(200,['ok'=>true,'id'=>$id,'notifications'=>['owner'=>$owner['state'],'customer'=>$customer['state']]]);
