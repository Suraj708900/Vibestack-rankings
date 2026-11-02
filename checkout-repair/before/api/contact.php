<?php
// POST /api/contact {name, email, subject, message, website (honeypot), elapsed (ms since page load), lang}
// 1) spam checks (honeypot, timing, per-IP rate limits)  2) store in SQLite contact_messages FIRST  3) notify the owner.
// Notify: when MAIL_VIA_RESEND is on (preview build), Resend sends the owner notification to OWNER_NOTIFY_TO (reply-to = visitor)
// plus an auto-acknowledgement to the visitor (max 1 per address per 24h); otherwise the old PHP mail() path to CONTACT_TO (skipped on STAGING).
// A message is never lost if mail fails: it stays in storage/vs.sqlite (status 'new', mailed 0).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
if (vs_method() !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
if (!vs_same_origin()) vs_send_json(403, ['error' => 'Forbidden.']);
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
  vs_db()->prepare('INSERT INTO contact_messages(id,ts,name,email,subject,body,lang,ip_hash,ua) VALUES(?,?,?,?,?,?,?,?,?)')
    ->execute([$id, time(), $name, $email, $subject, $msg, $lang, $iph, $ua]);
} catch (Throwable $e) { vs_fail500('contact store: ' . $e->getMessage()); }

// notify the owner (best effort; stored copy above is the source of truth)
if (vs_mail_enabled()) {
  $owner = vs_mail_owner(); $mailed = 0; $ack = null;
  if ($owner !== '') {
    $r = vs_send_mail(['kind' => 'contact-owner', 'to' => $owner, 'reply_to' => $email, 'idem' => 'contact-owner:' . $id,
      'subject' => '[AIUseFlow] ' . $subject . ' — ' . $name,
      'text' => "New message from the AIUseFlow contact form\n\nID: $id\nName: $name\nEmail: $email\nSubject: $subject\nLanguage: $lang\nTime (UTC): " . gmdate('Y-m-d H:i') . "\n\n" . $msg . "\n\nReply to this email to answer $name directly.\n"]);
    $mailed = $r['ok'] ? 1 : 0;
  } else error_log('contact: OWNER_NOTIFY_TO not set');
  // auto-acknowledgement; at most one per address per 24h so the form cannot be used to mail-bomb someone
  try { $st = vs_db()->prepare('SELECT COUNT(*) FROM contact_messages WHERE email=? AND ts>=?'); $st->execute([$email, time() - 86400]); $recent = (int) $st->fetchColumn(); } catch (Throwable $e) { $recent = 99; }
  if ($recent <= 1) {
    $hi = $lang === 'hi'; $first = preg_split('/\s+/', $name)[0] ?: $name;
    $paras = $hi
      ? ["नमस्ते $first,", "AIUseFlow से संपर्क करने के लिए धन्यवाद। हमें आपका संदेश (\"$subject\") मिल गया है और हम आमतौर पर 2-3 कार्यदिवसों में जवाब देते हैं।", "संदर्भ ID: $id", "यह एक स्वचालित ईमेल है; कृपया इसका जवाब न दें। कुछ और जोड़ना हो तो " . vs_site_url() . "/contact.html पर फ़ॉर्म दोबारा भरें।"]
      : ["Hi $first,", "Thanks for contacting AIUseFlow. We received your message (\"$subject\") and usually reply within 2-3 working days.", "Reference ID: $id", "This is an automatic email from a no-reply address. To add anything, please use the form again at " . vs_site_url() . "/contact.html."];
    $title = $hi ? 'हमें आपका संदेश मिल गया' : 'We received your message';
    $ack = vs_send_mail(['kind' => 'contact-ack', 'to' => $email, 'idem' => 'contact-ack:' . $id,
      'subject' => $hi ? "हमें आपका संदेश मिल गया ($id)" : "We received your message ($id)", 'text' => vs_mail_text($paras), 'html' => vs_mail_html($title, $paras)])['ok'];
  }
  try { vs_db()->prepare('UPDATE contact_messages SET mailed=? WHERE id=?')->execute([$mailed, $id]); } catch (Throwable $e) {}
  vs_send_json(200, ['ok' => true, 'id' => $id]);
}
$to = (string) vs_cfg('CONTACT_TO', 'contact@aiuseflow.com');
$from = (string) vs_cfg('CONTACT_FROM', 'no-reply@aiuseflow.com');
$mailed = 0;
if (!vs_cfg('STAGING') && function_exists('mail') && vs_valid_email($to) && vs_valid_email($from)) {
  $subj = '=?UTF-8?B?' . base64_encode('[AIUseFlow] ' . $subject . ' — ' . $name) . '?=';
  $text = "New message from the AIUseFlow contact form\n\nID: $id\nName: $name\nEmail: $email\nSubject: $subject\nLanguage: $lang\nTime (UTC): " . gmdate('Y-m-d H:i') . "\n\n" . $msg . "\n";
  $hdr = implode("\r\n", ['From: AIUseFlow <' . $from . '>', 'Reply-To: ' . $email, 'MIME-Version: 1.0', 'Content-Type: text/plain; charset=UTF-8', 'Content-Transfer-Encoding: 8bit', 'X-AIUseFlow-ID: ' . $id]);
  try { $mailed = @mail($to, $subj, $text, $hdr, '-f' . $from) ? 1 : 0; } catch (Throwable $e) { $mailed = 0; }
  try { vs_db()->prepare('UPDATE contact_messages SET mailed=? WHERE id=?')->execute([$mailed, $id]); } catch (Throwable $e) {}
  if (!$mailed) error_log('contact: mail() failed for ' . $id);
}
vs_send_json(200, ['ok' => true, 'id' => $id]);
