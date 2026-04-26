# OpenAI API Official Docs Map

Reference date: 2026-04-20

This map is a small set of official OpenAI docs pages to anchor the lesson. It is intentionally narrow so the first pass stays focused.

## Current Starting Point

- The official quickstart and text-generation docs point new projects toward the Responses API.
- The Python quickstart examples use the official `openai` SDK and show a first request through `client.responses.create(...)`.

## Core Pages

### 1. Quickstart

Link:

- https://platform.openai.com/docs/quickstart?lang=python

Use this for:

- creating and exporting `OPENAI_API_KEY`
- installing the Python SDK
- seeing the first minimal Python example

### 2. Responses API Reference

Link:

- https://platform.openai.com/docs/api-reference/responses/compact?api-mode=responses

Use this for:

- the request fields you can send
- the top-level response shape
- checking what changes when you move beyond the first example

### 3. Text Generation Guide

Link:

- https://platform.openai.com/docs/guides/chat-completions

Use this for:

- prompt structure
- basic text-generation patterns
- understanding why the lesson starts with Responses API for new work

### 4. Streaming Guide

Link:

- https://platform.openai.com/docs/guides/streaming-responses

Use this for:

- when to stream instead of waiting for a full response
- how Python iteration over streamed events works

### 5. Function Calling Guide

Link:

- https://platform.openai.com/docs/guides/function-calling

Use this for:

- defining tools with schemas
- understanding the application-side tool loop
- delaying tool use until after plain prompting is comfortable

### 6. Structured Outputs Guide

Link:

- https://platform.openai.com/docs/guides/structured-outputs

Use this for:

- deciding when to ask for structured JSON output
- understanding the difference between structured responses and tool calls

## Practical Reading Order

1. Quickstart
2. Responses API reference
3. Text generation guide
4. Streaming guide
5. Structured outputs guide
6. Function calling guide

## What To Ignore For The First Pass

- agents
- realtime
- multimodal workflows
- built-in tools such as web search or file search
- large app architecture questions

Those are useful later, but they are noise until the first plain Python request is working.
