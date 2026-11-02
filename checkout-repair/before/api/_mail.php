<?php
// Transactional email via the Resend HTTPS API (plain curl, no SDK). Not web-accessible (.htaccess denies api/_*).
// OFF unless the PRIVATE config sets MAIL_VIA_RESEND=true (currently only the preview build), so production keeps its old behaviour.
// Config keys: MAIL_VIA_RESEND, RESEND_API_KEY, MAIL_FROM ('AIUseFlow <noreply@aiuseflow.com>'), OWNER_NOTIFY_TO, MAIL_REPLY_TO (optional),
// MAIL_SIGNOFF, MAIL_ALLOW_ONLY (comma list; when set, mail to any other address is skipped: staging safety), MAIL_DRY_RUN (log only),
// RESEND_SEGMENT_ID (newsletter segment). Every attempt is appended to storage/mail.log (JSON lines, no API key).
if (!defined('VS_API')) { http_response_code(404); exit; }

function vs_mail_enabled(): bool {
  return (bool) vs_cfg('MAIL_VIA_RESEND', false) && (string) vs_cfg('RESEND_API_KEY') !== '' && vs_mail_addr((string) vs_cfg('MAIL_FROM')) !== '';
}
// bare address from 'Name <a@b>' or 'a@b'; '' if invalid
function vs_mail_addr(string $s): string { $s = trim($s); if (preg_match('/<([^<>]+)>\s*$/', $s, $m)) $s = trim($m[1]); return vs_valid_email($s) ? strtolower($s) : ''; }
function vs_mail_owner(): string { return vs_mail_addr((string) vs_cfg('OWNER_NOTIFY_TO')); }
function vs_mail_signoff(): string { $s = trim((string) vs_cfg('MAIL_SIGNOFF', 'Suraj Kumar')); return $s !== '' ? $s : 'Suraj Kumar'; }
function vs_mail_allowed(string $to): bool {
  $list = array_filter(array_map(fn($x) => strtolower(trim($x)), explode(',', (string) vs_cfg('MAIL_ALLOW_ONLY', ''))));
  return !$list || in_array(strtolower($to), $list, true);
}
function vs_mail_log(array $row): void {
  $row = ['ts' => gmdate('c')] + $row;
  @file_put_contents(vs_storage() . '/mail.log', json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX);
  @chmod(vs_storage() . '/mail.log', 0600);
}
// Minimal HTML email: $paras = list of plain-text paragraphs (escaped here); optional button [label, url].
function vs_mail_html(string $title, array $paras, ?array $btn = null): string {
  $e = fn($s) => nl2br(htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'));
  $h = '<div style="font:15px/1.55 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#111;max-width:560px;margin:0 auto;padding:16px">'
     . '<p style="font-weight:700;font-size:18px;margin:0 0 12px">' . $e($title) . '</p>';
  foreach ($paras as $p) $h .= '<p style="margin:0 0 12px">' . $e($p) . '</p>';
  if ($btn) $h .= '<p style="margin:18px 0"><a href="' . htmlspecialchars($btn[1], ENT_QUOTES, 'UTF-8') . '" style="background:#4f46e5;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none;display:inline-block">' . $e($btn[0]) . '</a></p>'
     . '<p style="margin:0 0 12px;font-size:12px;color:#555">Or paste this link into your browser: ' . $e($btn[1]) . '</p>';
  return $h . '<p style="margin:16px 0 0">' . $e("— " . vs_mail_signoff() . "\nAIUseFlow") . '</p></div>';
}
function vs_mail_text(array $paras, ?array $btn = null): string {
  return implode("\n\n", $paras) . ($btn ? "\n\n" . $btn[0] . ": " . $btn[1] : '') . "\n\n— " . vs_mail_signoff() . "\nAIUseFlow\n";
}
/** Send one email. $m: to (string), subject, text, html, reply_to (optional), kind (log label), idem (optional idempotency key).
 *  Returns ['ok'=>bool, 'id'=>?string, 'code'=>int, 'skipped'=>?string]. Never throws. */
function vs_send_mail(array $m): array {
  $to = vs_mail_addr((string) ($m['to'] ?? '')); $kind = (string) ($m['kind'] ?? 'mail');
  $res = function (array $r) use ($kind, $to) { vs_mail_log(['kind' => $kind, 'to' => $to] + $r); return $r + ['ok' => false, 'id' => null, 'code' => 0]; };
  if (!vs_mail_enabled()) return $res(['skipped' => 'mail disabled']);
  if ($to === '') return $res(['skipped' => 'invalid recipient']);
  if (!vs_mail_allowed($to)) return $res(['skipped' => 'not in MAIL_ALLOW_ONLY']);
  $subject = mb_substr(trim(str_replace(["\r", "\n"], ' ', (string) ($m['subject'] ?? ''))), 0, 200);
  $p = ['from' => trim((string) vs_cfg('MAIL_FROM')), 'to' => [$to], 'subject' => $subject, 'text' => (string) ($m['text'] ?? '')];
  if (!empty($m['html'])) $p['html'] = (string) $m['html'];
  $rt = vs_mail_addr((string) ($m['reply_to'] ?? vs_cfg('MAIL_REPLY_TO', '')));
  if ($rt !== '') $p['reply_to'] = [$rt];
  $p['tags'] = [['name' => 'kind', 'value' => preg_replace('/[^A-Za-z0-9_-]/', '_', $kind)]];
  if (vs_cfg('MAIL_DRY_RUN', false)) return $res(['ok' => true, 'skipped' => 'dry run', 'subject' => $subject, 'reply_to' => $rt]);
  $hdr = ['Authorization: Bearer ' . (string) vs_cfg('RESEND_API_KEY'), 'Content-Type: application/json', 'User-Agent: aiuseflow-php/1'];
  if (!empty($m['idem'])) $hdr[] = 'Idempotency-Key: ' . substr(preg_replace('/[^A-Za-z0-9:_-]/', '', (string) $m['idem']), 0, 200);
  $ch = curl_init('https://api.resend.com/emails');
  curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_CONNECTTIMEOUT => 8,
    CURLOPT_HTTPHEADER => $hdr, CURLOPT_POSTFIELDS => json_encode($p, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)]);
  $r = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  $j = is_string($r) ? json_decode($r, true) : null;
  $ok = $code >= 200 && $code < 300 && !empty($j['id']);
  return $res(['ok' => $ok, 'id' => $ok ? (string) $j['id'] : null, 'code' => $code] + ($ok ? [] : ['error' => mb_substr((string) ($j['message'] ?? $r), 0, 300)]));
}
// Generic JSON call to the Resend API (contacts / segments). Returns [code, decoded body|null].
function vs_resend_call(string $method, string $path, ?array $payload = null): array {
  $ch = curl_init('https://api.resend.com' . $path);
  $o = [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_CONNECTTIMEOUT => 8,
    CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . (string) vs_cfg('RESEND_API_KEY'), 'Content-Type: application/json', 'User-Agent: aiuseflow-php/1']];
  if ($payload !== null) $o[CURLOPT_POSTFIELDS] = json_encode($payload);
  curl_setopt_array($ch, $o); $r = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  return [$code, is_string($r) ? json_decode($r, true) : null];
}
// Newsletter: add/attach a confirmed subscriber to the Resend segment (free tier: contacts + segments). Returns true when Resend has it.
function vs_resend_add_contact(string $email): bool {
  if ((string) vs_cfg('RESEND_API_KEY') === '' || vs_cfg('MAIL_DRY_RUN', false)) return false;
  $seg = (string) vs_cfg('RESEND_SEGMENT_ID', vs_cfg('RESEND_AUDIENCE_ID', ''));
  $body = ['email' => $email, 'unsubscribed' => false] + ($seg !== '' ? ['segments' => [['id' => $seg]]] : []);
  [$code, $j] = vs_resend_call('POST', '/contacts', $body);
  if ($code >= 200 && $code < 300) { vs_mail_log(['kind' => 'contact-add', 'to' => $email, 'ok' => true, 'code' => $code]); return true; }
  // already a contact: make sure it is in the segment
  if ($seg !== '') { [$c2] = vs_resend_call('POST', '/contacts/' . rawurlencode($email) . '/segments/' . rawurlencode($seg)); $ok = $c2 >= 200 && $c2 < 300; }
  else $ok = false;
  vs_mail_log(['kind' => 'contact-add', 'to' => $email, 'ok' => $ok, 'code' => $code, 'error' => mb_substr((string) ($j['message'] ?? ''), 0, 200)]);
  return $ok;
}
// subscribers table: add double-opt-in columns once (idempotent)
function vs_sub_migrate(): void {
  static $done = false; if ($done) return; $done = true;
  $cols = array_column(vs_db()->query('PRAGMA table_info(subscribers)')->fetchAll(PDO::FETCH_ASSOC), 'name');
  if (!in_array('confirmed_at', $cols, true)) vs_db()->exec('ALTER TABLE subscribers ADD COLUMN confirmed_at INTEGER');
  if (!in_array('confirm_sent', $cols, true)) vs_db()->exec('ALTER TABLE subscribers ADD COLUMN confirm_sent INTEGER NOT NULL DEFAULT 0');
}
