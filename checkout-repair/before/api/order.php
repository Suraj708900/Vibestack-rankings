<?php
// POST /api/order {id, product, method:'upi'|'paypal', name, email, utr}: records a payment claim as a pending order for manual verification.
// MAIL_VIA_RESEND on (preview build): emails the buyer an order-received note and the owner (OWNER_NOTIFY_TO) a verify-this-payment notice.
// The download link is emailed later, when the owner marks the order paid in /admin-orders.html (api/admin.php).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
if (vs_method() !== 'POST') vs_send_json(405, ['error' => 'Method not allowed.']);
if (!vs_same_origin()) vs_send_json(403, ['error' => 'Forbidden.']);
if (vs_rate_limited('order', 6, 3600)) vs_send_json(429, ['error' => 'Too many attempts. Please try again later.']);
$b = vs_body();
if (!empty($b['company'])) vs_send_json(200, ['ok' => true]); // honeypot
$CFG = vs_products_cfg();
$id = strtoupper((string) ($b['id'] ?? '')); $slug = (string) ($b['product'] ?? ''); $p = $CFG['products'][$slug] ?? null;
$method = strtolower((string) ($b['method'] ?? '')); $name = mb_substr(trim((string) ($b['name'] ?? '')), 0, 80); $email = vs_norm_email($b['email'] ?? ''); $utr = strtoupper(trim((string) ($b['utr'] ?? '')));
if (!preg_match(VS_ORDER_RE, $id) || !$p) vs_send_json(400, ['error' => 'Invalid order. Please reload the checkout page.']);
if (!in_array($method, ['upi', 'paypal'], true)) vs_send_json(400, ['error' => 'Please choose UPI or PayPal.']);
if (mb_strlen($name) < 2 || !vs_valid_email($email)) vs_send_json(400, ['error' => 'Please enter your name and a valid email.']);
if (!preg_match('/^[A-Z0-9]{10,22}$/', $utr)) vs_send_json(400, ['error' => $method === 'upi' ? 'Please enter the UPI transaction reference (UTR), usually 12 digits.' : 'Please enter the PayPal transaction ID (17 characters).']);
if (vs_load_order($id)) vs_send_json(409, ['error' => 'This order was already submitted.']);
$o = ['id' => $id, 'product' => $slug, 'product_name' => $p['name'], 'method' => $method, 'amount' => $method === 'upi' ? $p['price'] : $p['price_usd'], 'currency' => $method === 'upi' ? 'INR' : 'USD',
  'file' => $p['file'] ?? '', 'name' => $name, 'email' => $email, 'utr' => $utr, 'status' => 'pending', 'created' => vs_iso_now()];
if (!vs_save_order($o, false)) { if (vs_load_order($id)) vs_send_json(409, ['error' => 'This order was already submitted.']); vs_send_json(500, ['error' => 'Could not save your order. Please try again or email us.']); }
if (vs_mail_enabled()) {
  $amt = ($o['currency'] === 'INR' ? '₹' : '$') . $o['amount'] . ' ' . $o['currency'];
  $how = $method === 'upi' ? 'UPI (UTR ' . $utr . ')' : 'PayPal (transaction ' . $utr . ')';
  $first = preg_split('/\s+/', $name)[0] ?: $name;
  $paras = ["Hi $first,", "Thanks for your order. We have received your payment details and will verify them manually, usually within 24 hours.",
    "Order ID: $id\nProduct: {$p['name']}\nAmount: $amt\nPaid via: $how", "Once the payment is confirmed you will get a second email with your download link.",
    "Questions? Use the contact form at " . vs_site_url() . "/contact.html and include your order ID. (This is a no-reply address.)"];
  $buyer = vs_send_mail(['kind' => 'order-received', 'to' => $email, 'idem' => 'order-received:' . $id, 'subject' => "Order received: {$p['name']} ($id)",
    'text' => vs_mail_text($paras), 'html' => vs_mail_html('Order received, pending verification', $paras)]);
  $owner = vs_mail_owner();
  $own = $owner === '' ? ['ok' => false] : vs_send_mail(['kind' => 'order-owner', 'to' => $owner, 'reply_to' => $email, 'idem' => 'order-owner:' . $id,
    'subject' => "[AIUseFlow] New order to verify: {$p['name']} $amt ($id)",
    'text' => "New order waiting for payment verification\n\nOrder ID: $id\nProduct: {$p['name']} ($slug)\nAmount: $amt\nMethod: $method\nUTR / transaction ID: $utr\nBuyer: $name <$email>\nTime (UTC): " . gmdate('Y-m-d H:i') . "\n\nCheck the payment in your " . ($method === 'upi' ? 'bank / UPI app' : 'PayPal account') . ", then mark it paid at " . vs_site_url() . "/admin-orders.html to email the download link.\n"]);
  $o['mail_received'] = $buyer['ok']; $o['mail_owner'] = $own['ok']; vs_save_order($o, true);
}
vs_send_json(200, ['ok' => true, 'id' => $id, 'status' => 'pending']);
