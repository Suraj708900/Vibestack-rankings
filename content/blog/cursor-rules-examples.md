title: Cursor Rules Examples: Practical Templates for Better AI Code
keyword: Cursor rules examples
description: Practical Cursor rules examples you can adapt: project overview, coding style, testing, framework-specific and security rules, plus how Cursor rules files work.
date: 2026-10-16
category: coding-agents
cover: p-270348
cover_credit: Photo via Pexels
---
Rules are the most effective way to make [Cursor](/tools/cursor.html)'s AI write code the way your project needs. Instead of repeating "we use TypeScript strict mode and Tailwind" in every prompt, you write it once and the agent follows it. This guide explains how Cursor rules work and gives practical examples to adapt. Formats evolve, so check Cursor's documentation for current details.

## How Cursor rules work

Cursor supports project rules stored in your repository in a `.cursor/rules` directory, as separate rule files (Cursor uses an `.mdc` format with a small header). Each rule can apply always, automatically when matching files are involved (using file patterns), or only when referenced. Older projects may use a single `.cursorrules` file in the project root, which Cursor treats as legacy. There are also user-level rules in settings for personal preferences.

Because project rules live in git, your whole team, and every AI session, shares them.

## Principles for good rules

- **Be specific and short.** "Use named exports" beats "write clean code".
- **State the why when it is not obvious.** It helps the model generalise.
- **Scope rules by file pattern** so front-end rules do not clutter back-end work.
- **Prefer positive instructions** ("use X") with a few clear "never" rules for real hazards.
- **Update rules when the AI repeats a mistake.** Rules are living documentation.

## Example 1: Project overview (always on)

```
# Project overview
- Next.js app (App Router) with TypeScript in strict mode.
- Styling: Tailwind CSS. No CSS modules or styled-components.
- Data: Supabase (Postgres). Schema lives in supabase/migrations.
- Run `npm run dev` to start, `npm test` for tests, `npm run lint` before finishing.
- Components in src/components, server code in src/server.
```

This gives every session a map of your project. If you use Supabase, see [Supabase vs Firebase](/blog/supabase-vs-firebase.html).

## Example 2: Code style

```
# Code style
- Use named exports, not default exports.
- Prefer small pure functions; keep components under ~150 lines.
- Use async/await, never .then chains.
- Handle errors explicitly; never swallow errors silently.
- Match existing patterns in nearby files before inventing new ones.
```

## Example 3: Testing (auto-attached to source files)

```
# Testing
- New functions with logic get unit tests next to them (*.test.ts).
- Cover empty, single and many-item cases, plus one failure case.
- Run `npm test` after changes and fix failures before declaring done.
- Do not delete or weaken existing tests to make them pass.
```

The last line prevents a common failure: an agent "fixing" a failing test by changing the assertion.

## Example 4: Framework-specific (Next.js)

```
# Next.js
- Default to Server Components; add "use client" only when needed.
- Fetch data on the server; never expose secret keys to client components.
- Use the framework's Image component for images.
```

Adapt this for your framework: Django, Rails, Laravel, SvelteKit and so on.

## Example 5: Security

```
# Security
- Never hard-code secrets; read them from environment variables.
- Server-only keys (service role, payment secrets) must never be imported into client code.
- Every database table needs row-level security policies; explain any policy you add.
- Validate all user input on the server.
```

See the full [vibe coding security checklist](/blog/vibe-coding-security-checklist.html).

## Example 6: Workflow and boundaries

```
# Workflow
- For tasks touching more than 2 files, propose a plan and wait for approval.
- Do not change the database schema or public API without asking.
- Do not add new dependencies without asking; prefer what is installed.
- Summarise what you changed and why at the end.
```

## Example 7: Tool usage (MCP)

```
# Tools
- Use the database MCP server to inspect the schema before writing queries.
- Use the browser tool to verify UI changes on http://localhost:3000.
```

If you use MCP, see [best MCP servers for Cursor](/blog/best-mcp-servers-for-cursor.html).

## Rules in other tools

The same idea exists elsewhere: [Claude Code](/tools/claude-code.html) reads `CLAUDE.md` (see the [Claude Code tutorial](/blog/claude-code-tutorial-for-beginners.html)), [OpenAI Codex](/tools/openai-codex.html) reads `AGENTS.md`, and [GitHub Copilot](/tools/github-copilot.html) supports repository custom instructions. Keep one source of truth and adapt it into each format.

## Maintaining rules

Review rules monthly. Delete ones the AI follows naturally and add ones for recurring mistakes. Several small, scoped rule files work better than one giant file.

## FAQ

### Where do Cursor rules go?
Project rules go in the `.cursor/rules` directory of your repository. Older projects may use a root `.cursorrules` file. Check Cursor's docs for the current format.

### How long should Cursor rules be?
Short. A focused page of specific instructions works better than a long essay, which dilutes the important points.

### Do rules work with every model in Cursor?
Rules are included as instructions to whichever model you choose, though models vary in how strictly they follow them.
