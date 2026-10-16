"""Account pages: /signup, /login, /account (noindex). Called from build.py."""
def run(g):
    page=g['page']; SITE=g['SITE']
    NI='<meta name="robots" content="noindex, nofollow">'
    CSS=('<style>.af{display:grid;gap:12px;max-width:420px}.af label{display:grid;gap:6px;font-weight:600}.af input{padding:11px 12px;border-radius:10px;border:1px solid #2a3142;background:#0f131c;color:inherit;font:inherit}'
         '.af button{padding:12px;border-radius:10px;border:0;background:#7c5cff;color:#fff;font-weight:700;cursor:pointer}.af button:disabled{opacity:.6}.af-msg{color:#f87171;min-height:1.2em;margin:0}.auth-wrap{max-width:480px;margin:24px auto}'
         'html[data-theme=light] .af input{background:#fff;border-color:#dfe3ea}.acc-saved{padding-left:1.1em}.acc-saved li{margin:.4em 0}</style>')
    page('/signup.html',f'Create your account · {SITE}','Create a free VibeStack Rankings account to save AI tools.',CSS+
      '<div class="auth-wrap card"><h1>Create your account</h1><p class="sub">Save tools to your account and find them on any device. Free.</p>'
      '<form id="signup-form" class="af" novalidate><label>Name<input name="name" required maxlength="80" autocomplete="name"></label><label>Email<input type="email" name="email" required autocomplete="email"></label>'
      '<label>Password<input type="password" name="password" required minlength="8" autocomplete="new-password"></label><label>Confirm password<input type="password" name="confirm" required minlength="8" autocomplete="new-password"></label>'
      '<button type="submit">Create account</button><p class="af-msg" role="alert"></p></form><p class="sub">Already have an account? <a href="/login">Log in</a> · <a href="/privacy">Privacy</a></p></div>',extra=NI)
    page('/login.html',f'Log in · {SITE}','Log in to your VibeStack Rankings account.',CSS+
      '<div class="auth-wrap card"><h1>Log in</h1><form id="login-form" class="af" novalidate><label>Email<input type="email" name="email" required autocomplete="email"></label>'
      '<label>Password<input type="password" name="password" required autocomplete="current-password"></label><button type="submit">Log in</button><p class="af-msg" role="alert"></p></form>'
      '<p class="sub">New here? <a href="/signup">Create an account</a></p></div>',extra=NI)
    page('/account.html',f'Your account · {SITE}','Your VibeStack Rankings account.',CSS+'<h1>Your account</h1><div id="account-app"><p class="sub">Loading…</p></div>',extra=NI)
