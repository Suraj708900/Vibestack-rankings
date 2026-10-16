title: How to Deploy a Vibe-Coded App (From Builder or Editor to Live URL)
keyword: how to deploy a vibe-coded app
description: A practical guide to deploying an AI-built app: publishing from builders, deploying from GitHub to Vercel, Netlify, Cloudflare Pages or Render, environment variables, domains and launch checks.
date: 2026-10-16
category: hosting
cover: p-586087
cover_credit: Photo via Pexels
---
You have built something with AI and it works in the preview. Now you want a real URL that you can share, ideally on your own domain, without it breaking the moment real people use it. This guide covers both routes: publishing straight from an app builder, and deploying your own code from GitHub. It links to our [Hosting & deploy rankings](/category/hosting.html) for the platforms themselves.

## Route 1: Publish from your builder

If you built with [Lovable](/tools/lovable.html), [Replit](/tools/replit.html) or [Bolt](/tools/bolt.html), the simplest option is the builder's own publish or deploy feature. It handles hosting, HTTPS and updates for you. Most also let you connect a custom domain, sometimes only on paid plans, so check the current plan details.

This is the right choice when you want to keep iterating inside the builder and do not need special infrastructure. You can always move later.

## Route 2: Deploy your code from GitHub

When you have exported your project to GitHub, or you build in an editor like [Cursor](/tools/cursor.html), deploy from the repository:

1. **Pick a host.** [Vercel](/tools/vercel.html) for Next.js and frontend frameworks, [Netlify](/tools/netlify.html) or [Cloudflare Pages](/tools/cloudflare-pages.html) for static sites and Jamstack apps, [Render](/tools/render.html) for long-running servers, workers and Python backends. See [free hosting for side projects](/blog/free-hosting-for-side-projects.html).
2. **Import the repository.** All four hosts let you connect GitHub and choose a repo. They usually auto-detect the framework and build command.
3. **Set environment variables.** Copy every variable your app needs (database URL, API keys) into the host's settings. Never commit them to the repo.
4. **Deploy.** The host builds and gives you a URL. From now on, every push to your main branch redeploys automatically, and many hosts create preview URLs for branches and pull requests.

## Environment variables: the most common failure

Most "it works locally but not in production" problems are missing or wrong environment variables. Make a checklist of every variable your app uses. Ask your coding agent: "List every environment variable this project reads and where." Remember the distinction between public variables, which some frameworks expose to the browser, and server-only secrets. Secret keys must only be used in server code.

## Connect your database correctly

If you use [Supabase](/tools/supabase.html) or [Neon](/tools/neon.html), use the connection details for production, and with serverless hosting prefer the pooled connection string the provider documents. Make sure access rules (like Supabase row-level security) are enabled before launch. For choosing a database, see [best database for side projects](/blog/best-database-for-side-projects.html).

## Add a custom domain

Buy a domain from any registrar, add it in your host's dashboard, and create the DNS records the host shows you. HTTPS certificates are issued automatically. DNS changes can take a while to propagate, so do this a day before you announce anything.

## Pre-launch checklist

- **Sign up, log in, log out** on the live site, in a private browser window.
- **Test on a phone.** Many visitors will be on mobile.
- **Check error pages.** Visit a URL that does not exist and see what happens.
- **Look for exposed secrets** in the browser's dev tools and in the page source.
- **Set up basic monitoring.** Most hosts show logs and errors; learn where they are.
- **Add analytics** if you want to know whether anyone uses it, and a privacy note if you collect data.
- **Run our [security checklist](/blog/vibe-coding-security-checklist.html).**

## After launch: a safe update workflow

Once real users rely on your app, change how you ship. Work on a branch, let the host build a preview deployment, test it, then merge to main. If something breaks in production, every major host lets you roll back to a previous deployment quickly. Learn where that button is before you need it.

## Costs to watch

Free tiers are usually enough for launch. As traffic grows, watch bandwidth, function invocations and database usage, and set spending alerts where available. If your app calls AI APIs, those are often the biggest cost; read the [AI API pricing guide](/blog/ai-api-pricing-guide.html).

## Moving from a builder to your own hosting

If you outgrow your builder's hosting, export or sync the code to GitHub, open it in an editor and run it locally first. Then follow Route 2 above. Expect to recreate environment variables and reconnect the database.

## FAQ

### Where should I host an app built with AI?
If your builder offers publishing, start there. If you have the code in GitHub, Vercel suits Next.js, Netlify or Cloudflare Pages suit static sites, and Render suits backend servers.

### Why does my app work in preview but not when deployed?
Usually missing environment variables, a database connection string pointing at the wrong place, or access rules blocking production requests. Check the host's build and runtime logs.

### Can I use my own domain for free?
Hosting with a custom domain is free on all four major hosts' free tiers; you only pay for the domain itself.
