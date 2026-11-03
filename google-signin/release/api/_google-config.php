<?php
// OAuth Client IDs are public identifiers. Client secrets are never used here.
if (!defined('VS_API')) { http_response_code(404); exit; }
function vs_google_client_id(): string {
  $configured = trim((string) vs_cfg('GOOGLE_CLIENT_ID'));
  return $configured !== '' ? $configured : '977299634733-nlbllg9j6ovlnkq8040kqgbpun4ivnrt.apps.googleusercontent.com';
}
