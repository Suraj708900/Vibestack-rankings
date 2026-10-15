title: Vibe Coding Security Checklist: 12 Things to Check Before You Launch
keyword: vibe coding security
description: A practical security checklist for AI-built and vibe-coded apps: secrets, database access rules, auth, input validation, dependencies and more.
date: 2026-10-16
category: vibe-coding
---
AI makes it possible to ship an app in a weekend. It also makes it possible to ship security holes in a weekend. The good news: most problems in vibe-coded apps are the same handful of mistakes, and you can catch them with a checklist. Run through this before you invite real users. It applies whether you built with [Lovable](/tools/lovable.html), [Replit](/tools/replit.html), [Bolt](/tools/bolt.html) or an editor like [Cursor](/tools/cursor.html).

## 1. No secret keys in frontend code
Anything shipped to the browser is public. Search your code for API keys (AI providers, payment providers, database service keys). Move them to server-side environment variables and call those services from a server function.

## 2. Database access rules are on
If you use [Supabase](/tools/supabase.html), enable row-level security on every table and write policies. If you use [Firebase](/tools/firebase.html), write Security Rules; never leave test-mode rules open. Then test: log in as user A and try to read user B's data.

## 3. Service-role keys stay on the server
Admin or service keys bypass access rules entirely. They must never appear in client code or public repositories.

## 4. Authentication is enforced on the server
Hiding a button is not security. Every server endpoint that changes or reveals data must check who the user is and whether they are allowed.

## 5. Validate input
Validate and limit everything users send: lengths, types, allowed values. Use parameterised queries or an ORM, never string-built SQL.

## 6. Rate-limit expensive endpoints
Any endpoint that calls a paid AI API can be abused to run up your bill. Add per-user and per-IP limits and set spending caps in provider dashboards. See our [AI API pricing guide](/blog/ai-api-pricing-guide.html).

## 7. Check your git history
If a key was ever committed, assume it is leaked even if you deleted it later. Rotate it.

## 8. Update dependencies
AI tools sometimes add outdated packages. Run your package manager's audit command and update anything flagged.

## 9. Lock down file uploads
Limit file types and sizes, store uploads in a storage bucket with proper access rules, and never execute uploaded files.

## 10. Watch for prompt injection
If your app feeds user content or web pages into an AI model that can take actions, that content can contain instructions. Do not let model output trigger sensitive actions without checks. More in [how to build an AI agent](/blog/how-to-build-an-ai-agent.html).

## 11. Set up error monitoring and logs
You cannot fix what you cannot see. Make sure errors are logged somewhere you will notice, without logging passwords or tokens.

## 12. Ask the AI for a security review, then verify
Prompt your coding agent: "Review this project for security issues: exposed secrets, missing access control, injection risks, missing rate limits. List each issue with the file and a fix." Treat the result as a starting point and verify each finding yourself.

## Make it a habit

Re-run this checklist whenever you add a feature that touches data, payments or AI calls. For the full build process, see [how to vibe code an app](/blog/how-to-vibe-code-an-app.html), and browse the [vibe coding tools](/category/vibe-coding.html).

## A 15-minute pre-launch test

Before launch, spend 15 minutes trying to break your own app:

1. Open the browser dev tools Network tab, use the app, and look at every request. Do any responses include data that the current user should not see?
2. Copy an API request and replay it with another user's ID. Does it succeed?
3. Log out and call the same endpoints. Do they still return data?
4. Search the built JavaScript for strings like "key", "secret" and "token".
5. Submit forms with very long text, empty values and HTML tags.

Anything that surprises you is a fix to make before real users arrive. Repeat after big changes. This is the same thinking a basic security review uses, just applied by you.

## Keep a security notes file

Create a short `SECURITY.md` (or notes page) listing where secrets live, which tables have access rules, which endpoints are rate-limited and who can deploy. Give it to your coding agent at the start of tasks that touch data or auth, and update it as the app grows. It keeps both you and the AI from accidentally undoing protections you added earlier.

## Further reading

For deployment-specific settings, read [how to deploy a vibe-coded app](/blog/how-to-deploy-a-vibe-coded-app.html).

## Re-check after every major change

Security is not a one-time task. New features add new endpoints and data.

## FAQ

### Are vibe-coded apps insecure?
Not inherently, but they often ship with common mistakes like exposed keys and missing database rules. A checklist catches most of them.

### Can AI find security bugs in my code?
AI coding agents are useful reviewers and catch many issues, but they also miss things. Verify their findings and test access rules manually.

### What is the single most important check?
Make sure no secret keys are in your frontend and that database access rules are enabled and tested.
