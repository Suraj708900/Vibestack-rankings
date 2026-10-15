title: MCP Explained: What the Model Context Protocol Is and Why Builders Care
keyword: MCP explained
description: The Model Context Protocol (MCP) explained in plain English: what servers and clients are, how AI tools use MCP, how to build or use an MCP server, and security tips.
date: 2026-10-16
category: agent-frameworks
---
If you use AI coding tools or build agents, you have probably seen "MCP" everywhere. The Model Context Protocol is an open standard, introduced by Anthropic and now supported by many AI applications, for connecting AI models to external tools and data. This guide explains what it is, why it matters, and how to use it safely, without assuming you already know the jargon.

## The problem MCP solves

AI assistants become far more useful when they can do things: read your files, query a database, search your docs, create a ticket. Before MCP, every AI app had to build its own integration for every service, and every service had to build plugins for every AI app. That is a lot of duplicated, incompatible work.

MCP standardises the connection. A service exposes its capabilities once, as an MCP server, and any MCP-compatible AI application can use it. People often compare it to USB-C: one standard plug instead of a drawer full of adapters.

## The pieces

- **MCP host / client:** the AI application you use, such as a desktop chat app, an AI code editor or an agent you build. It connects to servers and makes their capabilities available to the model.
- **MCP server:** a small program that exposes capabilities from some system, such as a database, a SaaS API or your filesystem.
- **Capabilities:** servers can offer **tools** (actions the model can call, like "create_issue"), **resources** (data the model can read, like files or records) and **prompts** (reusable templates).

Servers can run locally on your machine, communicating over standard input/output, or remotely over HTTP, which is how hosted services offer MCP endpoints.

## How it shows up in tools you use

Many AI coding tools, including editors such as [Cursor](/tools/cursor.html) and agents such as [Claude Code](/tools/claude-code.html), can connect to MCP servers. That lets your coding agent, for example, read issues from your tracker, inspect your database schema or check deployment logs without you copying and pasting. Agent frameworks, including the [OpenAI Agents SDK](/tools/openai-agents-sdk.html), have added MCP support so agents you build can use the same servers. Check each tool's documentation for its current MCP setup.

## Using an MCP server

The typical steps:

1. Find a server for the system you want (many services publish official ones; there are also community servers).
2. Add it to your AI tool's MCP configuration, usually a JSON entry with the command to run or the URL to connect to, plus any credentials it needs.
3. Restart or refresh the tool; it lists the new tools and resources.
4. Ask the AI to use them naturally ("look up the open bugs labelled checkout").

## Building your own MCP server

If you have an internal API or database you want your AI tools to use, you can write a server. Official SDKs exist for several languages, including TypeScript and Python. A minimal server defines a few tools, each with a name, a clear description and an input schema, and implements what happens when they are called. Good tool descriptions matter a lot: they are the model's only documentation.

Start with read-only tools. Add write actions later, with care.

## Security: treat MCP servers like software you install

MCP gives AI models real capabilities, so security matters:

- **Only install servers you trust.** A local server runs code on your machine with your permissions. Prefer official or well-maintained servers and review what they do.
- **Use least privilege.** Give servers scoped, read-only credentials where possible, never your admin keys.
- **Require approval for actions** with side effects. Many clients let you confirm tool calls before they run; keep that on for anything destructive.
- **Watch for prompt injection.** Content returned by a tool, such as a web page, an email or a ticket, can contain instructions aimed at the model. Do not let tool output automatically trigger sensitive actions.
- **Keep secrets out of shared configs** committed to git.

## MCP vs plain function calling

Function calling is the model-level ability to request a tool call. MCP sits a layer above it: a standard way to package and discover tools so they work across applications. If you are building one agent with three custom tools, plain function calling is fine. If you want your tools usable in many AI apps, or want to use the growing ecosystem of existing servers, MCP is the better fit. See [how to build an AI agent](/blog/how-to-build-an-ai-agent.html) for the broader picture.

## FAQ

### Who created MCP?
Anthropic introduced the Model Context Protocol as an open standard, and it has since been adopted by many AI tools and companies.

### Do I need to code to use MCP?
Not to use existing servers in tools that support them; you usually just add a configuration entry. Building a server requires some programming.

### Is MCP safe?
It is as safe as the servers you install and the permissions you give them. Use trusted servers, scoped credentials and approval for risky actions.
