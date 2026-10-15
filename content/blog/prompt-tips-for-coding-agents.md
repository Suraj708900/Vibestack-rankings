title: Prompt Tips for Coding Agents: How to Get Better Code from AI
keyword: prompt tips for coding agents
description: Practical prompting techniques for AI coding agents like Cursor, Claude Code, Copilot and Codex: context, planning, scoping, testing and review habits that improve results.
date: 2026-10-16
category: coding-agents
---
Two developers can use the same AI coding agent and get very different results. The difference is rarely luck; it is how they brief the agent. These techniques work across [Cursor](/tools/cursor.html), [Claude Code](/tools/claude-code.html), [GitHub Copilot](/tools/github-copilot.html), [OpenAI Codex](/tools/openai-codex.html) and [Windsurf](/tools/windsurf.html), because they address how all language-model agents work: they only know what you give them and what they can find.

## 1. State the goal, not just the action

"Add a loading spinner" is an action. "Users think the app froze when saving a large project; show progress while saving and disable the save button until done" is a goal. Goals let the agent make sensible decisions you did not anticipate.

## 2. Give the right context

Point the agent at the relevant files, paste exact error messages, and mention constraints ("we use Tailwind, not CSS modules"; "this must work on Node 20"). Agents that can search your codebase still benefit from a hint about where to look. Too much irrelevant context can hurt, so be selective.

## 3. Keep a project rules file

Most agents support a project-level instructions file. Put your stack, folder structure, conventions, commands to run tests and lint, and things to avoid. Keep it short and current. This saves you repeating the same instructions in every prompt and reduces style drift.

## 4. Ask for a plan first on bigger tasks

For anything touching several files, ask: "Propose a plan before writing code. List the files you will change and why." Review the plan, correct misunderstandings, then approve. Fixing a plan is far cheaper than fixing a large diff.

## 5. Scope tasks small

One feature or fix per request. Large, vague tasks produce large, vague diffs that are hard to review. If a task is big, break it into steps and run them one at a time, committing between steps.

## 6. Make verification possible

Agents do better when they can check their own work. Have a single command that runs tests, type checks and linting, and tell the agent to run it. Ask for tests alongside new features: "Add tests covering the empty, single-item and many-items cases."

## 7. Commit before you start

Commit a clean state before each agent task. If the result is bad, you can discard it instantly. This also makes it easy to review exactly what the agent changed with a diff.

## 8. Describe bugs precisely

Give the exact error, steps to reproduce, expected and actual behaviour, and what you already tried. "It doesn't work" leads to guesswork; a precise report leads to a fix.

## 9. Ask it to explain

When the agent produces code you do not fully understand, ask it to explain the approach and any trade-offs. This catches mistakes and helps you learn. Ask "What could go wrong with this?" for anything touching security, money or data.

## 10. Tell it what not to touch

"Do not modify the public API of this module" or "Do not change the database schema" prevents well-meaning but unwanted changes.

## 11. Reset when stuck

If the agent goes in circles after two or three attempts, stop. Roll back, start a fresh conversation with a clearer prompt and better context. Long, confused conversations rarely recover.

## 12. Review like a teammate

Read every diff before merging. Check edge cases, error handling, security and whether the change actually solves the goal. The agent is a fast collaborator, not an infallible one.

## A reusable prompt template

> **Goal:** what and why.
> **Context:** relevant files, errors, constraints.
> **Plan first:** list files and approach before coding.
> **Done when:** tests pass / behaviour X works.
> **Don't:** things to leave alone.

## Model choice matters less than you think

Good briefing narrows the gap between models considerably. If you are still deciding, see [Claude vs GPT for coding](/blog/claude-vs-gpt-for-coding.html) and [best AI coding agents](/blog/best-ai-coding-agents.html).

## Example: a weak prompt vs a strong prompt

**Weak:** "Fix the login."

**Strong:** "Goal: users with uppercase letters in their email can't log in. Context: auth logic is in `lib/auth.ts`, signup lowercases emails but login doesn't. Plan first, then fix. Done when: a new test logging in with `Test@Example.com` passes and existing auth tests still pass. Don't change the database schema."

The second prompt is longer to write but saves several rounds of back-and-forth.

## FAQ

### What is the best way to prompt an AI coding agent?
Give a clear goal, relevant context and constraints, ask for a plan on larger tasks, keep tasks small, and make tests easy to run.

### Should I use a rules file?
Yes. A short project instructions file with your stack, conventions and commands improves consistency across every request.

### Why does my coding agent keep making the same mistake?
It may lack context or a rule. Add the constraint to your rules file, and start a fresh conversation if the current one is confused.
