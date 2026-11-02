<?php
// Admin orders API (Authorization: Bearer ADMIN_TOKEN). GET list; POST {action:'paid'|'delete', id} | {action:'upload', product, data(base64 zip)}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
header('X-Robots-Tag: noindex');
if (!vs_is_admin()) vs_send_json(401, ['error' => 'Unauthorized.']);
$CFG = vs_products_cfg(); $hours = (int) ($CFG['download_hours'] ?? 72);
function vs_mail_order(array $o, string $link, int $hours): array {
  if (vs_mail_enabled()) { // Resend transactional path (preview build): MAIL_FROM, sign-off MAIL_SIGNOFF
    $amt = ($o['currency'] === 'INR' ? '₹' : '$') . $o['amount'] . ' ' . $o['currency'];
    $first = preg_split('/\s+/', (string) $o['name'])[0] ?: (string) $o['name'];
    $paras = ["Hi $first,", "Your payment of $amt for {$o['product_name']} is confirmed. Thank you!", "Your download link is valid for $hours hours. If it expires, use the contact form at " . vs_site_url() . "/contact.html with your order ID and we will send a new one.", "Order ID: {$o['id']}"];
    $r = vs_send_mail(['kind' => 'order-download', 'to' => $o['email'], 'idem' => 'order-download:' . $o['id'] . ':' . substr(hash('sha256', $link), 0, 12),
      'subject' => "Your download: {$o['product_name']} (order {$o['id']})", 'text' => vs_mail_text($paras, ['Download ' . $o['product_name'], $link]),
      'html' => vs_mail_html('Your download is ready', $paras, ['Download ' . $o['product_name'], $link])]);
    return $r['ok'] ? ['sent' => true, 'id' => $r['id']] : ['sent' => false, 'reason' => $r['skipped'] ?? ('Resend error ' . $r['code'])];
  }
  $from = (string) vs_cfg('RESEND_FROM'); // only set once a sending domain is verified
  if (vs_cfg('RESEND_API_KEY') === '' || $from === '') return ['sent' => false, 'reason' => 'No verified Resend sending domain configured (RESEND_FROM).'];
  [$code] = vs_resend('/emails', ['from' => $from, 'to' => [$o['email']], 'subject' => "Your download: {$o['product_name']} (order {$o['id']})",
    'text' => "Hi {$o['name']},\n\nThanks for your payment of {$o['currency']} {$o['amount']} for {$o['product_name']}. Your download link (valid {$hours} hours):\n{$link}\n\nOrder: {$o['id']}\nQuestions? Reply to this email.\n\nAIUseFlow / Suraj Kamdev"]);
  return ($code >= 200 && $code < 300) ? ['sent' => true] : ['sent' => false, 'reason' => 'Resend error ' . $code];
}
$m = vs_method();
if ($m === 'GET') vs_send_json(200, ['orders' => vs_list_orders()]);
if ($m !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
$b = vs_body();
$act = $b['action'] ?? '';
if ($act === 'upload') { // store a product zip at its configured private path
  $p = $CFG['products'][(string) ($b['product'] ?? '')] ?? null; if (!$p || empty($p['file'])) vs_send_json(400, ['error' => 'Unknown product.']);
  $buf = base64_decode((string) ($b['data'] ?? ''), true);
  if ($buf === false || $buf === '' || strlen($buf) > 3200000) vs_send_json(400, ['error' => 'Bad file.']);
  $dst = vs_product_file($p['file']); if (!$dst) vs_send_json(400, ['error' => 'Unknown product.']);
  if (!is_dir(dirname($dst))) @mkdir(dirname($dst), 0700, true);
  if (file_put_contents($dst, $buf, LOCK_EX) === false) vs_send_json(500, ['error' => 'Server error.']);
  vs_send_json(200, ['ok' => true, 'pathname' => $p['file'], 'size' => strlen($buf)]);
}
$o = vs_load_order((string) ($b['id'] ?? '')); if (!$o) vs_send_json(404, ['error' => 'Order not found.']);
if ($act === 'delete') { vs_delete_order($o['id']); vs_send_json(200, ['ok' => true, 'deleted' => $o['id']]); }
if ($act === 'paid') {
  $link = vs_site_url() . '/api/download?token=' . vs_make_token($o, $hours);
  try { $mail = vs_mail_order($o, $link, $hours); } catch (Throwable $e) { $mail = ['sent' => false, 'reason' => $e->getMessage()]; }
  $o['status'] = 'paid'; $o['paid_at'] = vs_iso_now(); $o['emailed'] = $mail['sent']; vs_save_order($o, true);
  vs_send_json(200, ['ok' => true, 'order' => $o, 'link' => $link, 'email' => $mail]);
}
vs_send_json(400, ['error' => 'Invalid action.']);
