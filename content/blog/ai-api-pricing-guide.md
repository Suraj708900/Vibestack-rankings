title: AI API Pricing Explained: How to Estimate Your Model Costs
keyword: AI API pricing
description: How AI API pricing works (tokens, input vs output, caching, batch) and how to estimate and control costs across OpenAI, Anthropic, Gemini, OpenRouter and Groq.
date: 2026-10-16
category: ai-apis
cover: p-5466250
cover_credit: Photo via Pexels
---
Almost every AI API, from [OpenAI](/tools/openai-api.html) to [Anthropic](/tools/anthropic-api.html) and [Google Gemini](/tools/google-gemini-api.html), charges per token. Understanding what that means is the difference between a side project that costs pocket change and one that sends you a surprise bill. This guide explains the pricing model, how to estimate your costs, and how to keep them down. We intentionally do not quote per-token prices: they change frequently and differ by model, so always use each provider's official pricing page for the numbers.

## What is a token?

A token is a chunk of text the model processes, often a word or part of a word. Providers publish tokenizer tools, and most API responses report exactly how many tokens a request used. As a rough rule of thumb for English, a token is a few characters, so a page of text is hundreds of tokens.

## Input vs output tokens

Nearly every provider prices **input tokens** (what you send: system prompt, conversation history, documents) separately from **output tokens** (what the model writes back). Output tokens are typically priced higher than input tokens. Two consequences:

1. Long prompts that you resend on every request (big system prompts, full chat histories, pasted documents) can dominate cost.
2. Asking for concise answers directly reduces the more expensive side of the bill.

## Model tiers

Providers offer families of models, from large flagship models to smaller, faster, cheaper ones. Prices between tiers can differ by a large factor. A very common optimisation is to route easy tasks (classification, extraction, short replies) to a small model and reserve the flagship model for hard reasoning or coding.

## Discounts worth knowing

- **Prompt caching:** several providers discount input tokens that repeat across requests, such as a long, unchanging system prompt. Put stable content at the start of the prompt so it can be cached.
- **Batch APIs:** if results can wait, some providers offer discounted asynchronous batch processing.
- **Free tiers:** the Gemini API offers a free tier through Google AI Studio, and [Groq](/tools/groq.html) has a free tier for fast open-model inference. Free tiers usually have rate limits and may have different data-use terms, so read them.

## How to estimate your monthly cost

1. Pick a representative request and measure its input and output tokens (the API response tells you).
2. Multiply by the model's official per-token prices to get cost per request.
3. Multiply by requests per user per day, times expected daily users, times 30.
4. Add a safety margin for retries, longer conversations and growth.

Do this for two model tiers and you will quickly see whether the cheaper model is "good enough" economics-wise.

## Comparing providers with one key

[OpenRouter](/tools/openrouter.html) gives you one API and key for hundreds of models from many providers, which makes it easy to compare quality and cost side by side or add fallbacks when one provider is down. See our [OpenRouter guide](/blog/openrouter-guide.html).

## Cost-control checklist

- Set a hard monthly spending limit or budget alert in every provider dashboard.
- Cap `max_tokens` on responses.
- Trim conversation history: summarise older turns instead of resending everything.
- Cache results for identical requests in your own app.
- Never expose your API key in frontend code; call the API from a server function so users cannot abuse it.
- Rate-limit per user.

Browse all model providers in our [AI APIs & models rankings](/category/ai-apis.html), and if you are building an agent, read [how to build an AI agent](/blog/how-to-build-an-ai-agent.html), because agents make many calls per task and costs add up quickly.

## A worked estimation template

You do not need real prices to set up the maths; you plug them in from the provider's pricing page. Here is a template you can copy into a spreadsheet:

| Input | Where it comes from |
|---|---|
| Input tokens per request | `usage` field in a real API response |
| Output tokens per request | `usage` field in a real API response |
| Price per input token | provider's official pricing page |
| Price per output token | provider's official pricing page |
| Requests per active user per day | your product analytics or a guess you revisit |
| Daily active users | analytics |

Cost per request = (input tokens × input price) + (output tokens × output price). Multiply up by requests and users, then add 20–50% headroom for retries and growth. Re-run the sheet whenever you change models or prompts, because a longer system prompt changes every request.

## Where hidden costs come from

- **Agent loops.** One user action can trigger many model calls when an agent plans, calls tools and re-reads results. Measure tokens per *task*, not per call.
- **Retrieval context.** RAG apps often stuff many document chunks into each prompt. Retrieving fewer, better chunks is usually cheaper and more accurate.
- **Images, audio and video.** Multimodal inputs are priced differently from text; check the provider's page for how they are counted.
- **Embeddings.** Usually cheap per call, but re-embedding a whole corpus after every change adds up. Only embed what changed.

## FAQ

### Which AI API is cheapest?
It depends on the model and task. Small models from every major provider are far cheaper than flagship models, and Gemini and Groq offer free tiers. Compare current official pricing for the specific models you need.

### Why is my AI API bill higher than expected?
The usual causes are resending long histories or documents on every request, using a flagship model for simple tasks, and unbounded output length.

### Do I pay for failed requests?
Policies vary by provider. Generally you are billed for tokens actually processed. Check your provider's documentation.
