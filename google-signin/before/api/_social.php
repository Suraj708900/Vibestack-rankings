<?php
// Shared helpers for social login (Google ID token, GitHub + Facebook OAuth code flow).
// Secrets come only from the private config.php (vs_cfg); nothing here is sent to the browser.
if (!defined('VS_API')) { http_response_code(404); exit; }

function vs_http(string $method, string $url, array $headers = [], ?string $body = null): array {
  $ch = curl_init($url);
  curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10, CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_FOLLOWLOCATION => false,
    CURLOPT_PROTOCOLS => CURLPROTO_HTTPS, CURLOPT_HTTPHEADER => array_merge(['User-Agent: AIUseFlow-Login'], $headers), CURLOPT_CUSTOMREQUEST => $method]);
  if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
  $res = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE); $hdr = '';
  curl_close($ch);
  return ['code' => $code, 'body' => is_string($res) ? $res : '', 'json' => is_string($res) ? json_decode($res, true) : null];
}

// Strict same-origin for state-changing POSTs: Origin must be present and match this host.
function vs_same_origin_strict(): bool { return ($_SERVER['HTTP_ORIGIN'] ?? '') !== '' && vs_same_origin(); }

// Find the user by verified email (link) or create a password-less account; then set the normal signed session cookie.
function vs_social_login(string $provider, string $sub, string $email, string $name): array {
  $email = vs_norm_email($email);
  if (!vs_valid_email($email)) throw new RuntimeException('bad email');
  $k = vs_key_for($email); $u = vs_load_user($k);
  if (!$u) {
    $u = ['k' => $k, 'name' => mb_substr(trim($name) !== '' ? trim($name) : explode('@', $email)[0], 0, 80), 'email' => $email, 'pw' => '', 'created' => vs_iso_now(),
      'saved' => [], 'sv' => 1, 'fails' => 0, 'lockUntil' => 0, 'providers' => [$provider => $sub]];
    if (!vs_save_user($u, false)) { $u = vs_load_user($k); if (!$u) throw new RuntimeException('save failed'); }
  }
  $p = $u['providers'] ?? [];
  if (($p[$provider] ?? null) !== $sub) { $p[$provider] = $sub; $u['providers'] = $p; vs_save_user($u); }
  vs_set_cookie(vs_sign_session($u), VS_MAX_AGE);
  return $u;
}

// ---- Google ID token (RS256 JWT) verification ----
function vs_der_len(int $n): string { if ($n < 128) return chr($n); $b = ''; while ($n > 0) { $b = chr($n & 255) . $b; $n >>= 8; } return chr(0x80 | strlen($b)) . $b; }
function vs_der_int(string $x): string { $x = ltrim($x, "\0"); if ($x === '' || ord($x[0]) > 127) $x = "\0" . $x; return "\x02" . vs_der_len(strlen($x)) . $x; }
function vs_jwk_to_pem(array $jwk): ?string {
  if (($jwk['kty'] ?? '') !== 'RSA' || empty($jwk['n']) || empty($jwk['e'])) return null;
  $n = vs_b64u_dec($jwk['n']); $e = vs_b64u_dec($jwk['e']); if ($n === false || $e === false) return null;
  $rsa = "\x30" . vs_der_len(strlen($i = vs_der_int($n) . vs_der_int($e))) . $i;
  $bit = "\x03" . vs_der_len(strlen($rsa) + 1) . "\0" . $rsa;
  $alg = "\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00";
  $spki = "\x30" . vs_der_len(strlen($alg . $bit)) . $alg . $bit;
  return "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($spki), 64, "\n") . "-----END PUBLIC KEY-----\n";
}
// Returns the verified claims or null. Pure function: JWKS and clock passed in (unit-testable).
function vs_google_verify(string $jwt, string $clientId, array $jwks, int $now): ?array {
  if ($clientId === '') return null;
  $parts = explode('.', $jwt); if (count($parts) !== 3) return null;
  [$h64, $p64, $s64] = $parts;
  $h = json_decode((string) vs_b64u_dec($h64), true); $c = json_decode((string) vs_b64u_dec($p64), true); $sig = vs_b64u_dec($s64);
  if (!is_array($h) || !is_array($c) || $sig === false || ($h['alg'] ?? '') !== 'RS256' || empty($h['kid'])) return null;
  $pem = null; foreach (($jwks['keys'] ?? []) as $k) if (($k['kid'] ?? '') === $h['kid']) { $pem = vs_jwk_to_pem($k); break; }
  if (!$pem || openssl_verify($h64 . '.' . $p64, $sig, $pem, OPENSSL_ALGO_SHA256) !== 1) return null;
  if (!in_array($c['iss'] ?? '', ['accounts.google.com', 'https://accounts.google.com'], true)) return null;
  $aud = $c['aud'] ?? ''; if (!(is_string($aud) ? hash_equals($clientId, $aud) : in_array($clientId, (array) $aud, true))) return null;
  if ((int) ($c['exp'] ?? 0) < $now - 60 || (int) ($c['iat'] ?? 0) > $now + 300) return null;
  if (($c['email_verified'] ?? false) !== true && ($c['email_verified'] ?? '') !== 'true') return null;
  if (empty($c['sub']) || empty($c['email'])) return null;
  return $c;
}
function vs_google_jwks(): array {
  $test = (string) vs_cfg('GOOGLE_JWKS_FILE'); // local testing only; leave unset in production
  if ($test !== '') return vs_read_json_file($test) ?? [];
  $cache = vs_storage() . '/google-jwks.json'; $c = vs_read_json_file($cache);
  if ($c && ($c['_exp'] ?? 0) > time()) return $c;
  $r = vs_http('GET', 'https://www.googleapis.com/oauth2/v3/certs');
  if ($r['code'] !== 200 || !is_array($r['json']) || empty($r['json']['keys'])) return $c ?? [];
  $j = $r['json']; $j['_exp'] = time() + 3600; vs_write_json_file($cache, $j); return $j;
}

// ---- OAuth state (CSRF): random value in a short-lived signed HttpOnly cookie, echoed back by the provider ----
function vs_oauth_start(string $provider): string {
  $state = vs_b64u(random_bytes(24));
  $v = vs_sign_payload(['s' => $state, 'p' => $provider, 'exp' => time() + 600], 'oauth:');
  header('Set-Cookie: vs_oauth=' . $v . '; Path=/api/; HttpOnly; Secure; SameSite=Lax; Max-Age=600', false);
  return $state;
}
function vs_oauth_check(string $provider, string $state): bool {
  $c = (string) ($_COOKIE['vs_oauth'] ?? '');
  header('Set-Cookie: vs_oauth=; Path=/api/; HttpOnly; Secure; SameSite=Lax; Max-Age=0', false);
  $d = $c !== '' ? vs_verify_payload($c, 'oauth:') : null;
  return $d && ($d['p'] ?? '') === $provider && ($d['exp'] ?? 0) >= time() && $state !== '' && hash_equals((string) $d['s'], $state);
}
function vs_oauth_done(string $err = ''): void {
  header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');
  header('Location: ' . ($err === '' ? '/account' : '/login?oauth_error=' . rawurlencode($err)), true, 302); exit;
}
function vs_cb_url(string $file): string { return vs_site_url() . '/api/' . $file; }
