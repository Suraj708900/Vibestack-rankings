<?php
// Admin orders API (Authorization: Bearer ADMIN_TOKEN). GET list; POST {action:'paid'|'delete', id} | {action:'upload', product, data(base64 zip)}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_notifications.php';
header('X-Robots-Tag: noindex');
if (!vs_is_admin()) vs_send_json(401, ['error' => 'Unauthorized.']);
$CFG = vs_products_cfg(); $hours = (int) ($CFG['download_hours'] ?? 72);
function vs_mail_order(array $o, string $link, int $hours): array {
 $paras=['Hi '.$o['name'].',','Your payment for '.$o['product_name'].' is confirmed.','Order / tracking ID: '.$o['id'],'The download link is valid for '.$hours.' hours. For support, reply to this email or contact contact@aiuseflow.com.'];
 $r=auf_notice('download:'.$o['id'].':'.substr(hash('sha256',$link),0,16),['kind'=>'order-download','to'=>$o['email'],'subject'=>'Your download: '.$o['product_name'].' ('.$o['id'].')','text'=>vs_mail_text($paras,['Download your product',$link]),'html'=>vs_mail_html('Your download is ready',$paras,['Download your product',$link])]);
 return ['sent'=>$r['state']==='sent','queued'=>$r['state']==='pending','reason'=>$r['state']==='pending'?'Email queued for retry; the order and download link remain saved.':null,'id'=>$r['provider_id']??null];
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
