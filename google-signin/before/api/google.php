<?php
// POST /api/google.php {credential}: Google Identity Services ID token -> verified -> find/link/create user -> vs_session cookie.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_social.php';
header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');
if (vs_method() !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
if (!vs_same_origin_strict()) vs_send_json(403, ['error' => 'Forbidden.']);
$cid = (string) vs_cfg('GOOGLE_CLIENT_ID');
if ($cid === '') vs_send_json(404, ['error' => 'Google sign-in is not enabled.']);
if (vs_rate_limited('google', 20, 900)) vs_send_json(429, ['error' => 'Too many attempts. Try again later.']);
$b = vs_body(); $jwt = (string) ($b['credential'] ?? '');
if ($jwt === '' || strlen($jwt) > 4096) vs_send_json(400, ['error' => 'Missing Google credential.']);
$c = vs_google_verify($jwt, $cid, vs_google_jwks(), time());
if (!$c) vs_send_json(401, ['error' => 'Google sign-in could not be verified. Please try again.']);
try { $u = vs_social_login('google', (string) $c['sub'], (string) $c['email'], (string) ($c['name'] ?? '')); }
catch (Throwable $e) { error_log('google login: ' . $e->getMessage()); vs_send_json(500, ['error' => 'Could not sign you in. Please try again.']); }
vs_send_json(200, ['ok' => true, 'user' => ['name' => $u['name'], 'email' => $u['email']]]);
