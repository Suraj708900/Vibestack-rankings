<?php
// /api/auth/{signup,login,logout,me,providers}  (rewritten to auth.php?action=...)
require __DIR__ . '/_boot.php';
require_once __DIR__ . '/_google-config.php';
const GENERIC = 'Invalid email or password.';
$action = (string) ($_GET['action'] ?? '');
if ($action === 'me') { $u = vs_current_user(); vs_send_json(200, ['user' => $u ? ['name' => $u['name'], 'email' => $u['email'], 'saved' => $u['saved'] ?? []] : null]); }
if ($action === 'providers') { header('Cache-Control: public, max-age=300'); vs_raw_json(200, ['google' => vs_google_client_id() ?: null, 'github' => vs_cfg('GITHUB_CLIENT_ID') !== '' && vs_cfg('GITHUB_CLIENT_SECRET') !== '', 'facebook' => vs_cfg('FB_APP_ID') !== '' && vs_cfg('FB_APP_SECRET') !== '']); }
if (vs_method() !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
if (!vs_same_origin()) vs_send_json(403, ['error' => 'Forbidden.']);
$b = vs_body();
if ($action === 'logout') { vs_set_cookie('', 0); vs_send_json(200, ['ok' => true]); }
if ($action === 'signup') {
  if (vs_rate_limited('signup', 5, 3600)) vs_send_json(429, ['error' => 'Too many attempts. Try again later.']);
  $name = mb_substr(trim((string) ($b['name'] ?? '')), 0, 80); $email = vs_norm_email($b['email'] ?? ''); $pw = (string) ($b['password'] ?? ''); $confirm = (string) ($b['confirm'] ?? '');
  if ($name === '' || !vs_valid_email($email)) vs_send_json(400, ['error' => 'Please enter your name and a valid email.']);
  $len = mb_strlen($pw); if ($len < 8 || $len > 200) vs_send_json(400, ['error' => 'Password must be 8 to 200 characters.']);
  if ($pw !== $confirm) vs_send_json(400, ['error' => 'Passwords do not match.']);
  $k = vs_key_for($email);
  $u = ['k' => $k, 'name' => $name, 'email' => $email, 'pw' => vs_hash_password(vs_pw_input($pw)), 'created' => vs_iso_now(), 'saved' => [], 'sv' => 1, 'fails' => 0, 'lockUntil' => 0];
  if (vs_load_user($k) || !vs_save_user($u, false)) vs_send_json(400, ['error' => 'Could not create account. If you already have one, log in instead.']);
  vs_set_cookie(vs_sign_session($u), VS_MAX_AGE);
  vs_send_json(200, ['ok' => true, 'user' => ['name' => $name, 'email' => $email]]);
}
if ($action === 'login') {
  if (vs_rate_limited('login', 10, 900)) vs_send_json(429, ['error' => 'Too many attempts. Try again later.']);
  $email = vs_norm_email($b['email'] ?? ''); $pw = (string) ($b['password'] ?? '');
  $u = vs_valid_email($email) ? vs_load_user(vs_key_for($email)) : null;
  if (!$u) { vs_verify_password($pw, vs_dummy_hash()); vs_send_json(401, ['error' => GENERIC]); }
  $nowMs = (int) (microtime(true) * 1000);
  if (!empty($u['lockUntil']) && $u['lockUntil'] > $nowMs) vs_send_json(429, ['error' => 'Too many attempts. Try again later.']);
  if (!vs_verify_password($pw, (string) $u['pw'])) {
    $u['fails'] = ($u['fails'] ?? 0) + 1; if ($u['fails'] >= 8) { $u['lockUntil'] = $nowMs + 900000; $u['fails'] = 0; }
    vs_save_user($u); vs_send_json(401, ['error' => GENERIC]);
  }
  if (!empty($u['fails']) || !empty($u['lockUntil'])) { $u['fails'] = 0; $u['lockUntil'] = 0; vs_save_user($u); }
  vs_set_cookie(vs_sign_session($u), VS_MAX_AGE); vs_send_json(200, ['ok' => true, 'user' => ['name' => $u['name'], 'email' => $u['email']]]);
}
vs_send_json(404, ['error' => 'Not found.']);
