# OpenAI API

This lesson directory is intentionally code-light.

The goal here is to learn the modern OpenAI API from the official docs, starting with the Python quickstart and the Responses API before branching into more advanced patterns.

## Lesson Goals

- understand the difference between account setup, API-key setup, SDK install, and the first successful request
- make a basic text request from Python with the official SDK
- understand the shape of a response object and the convenience of `response.output_text`
- learn when to use plain text output, streaming, structured outputs, and function calling
- build toward small practical exercises instead of jumping straight into a larger app

## Current Environment Status

- as of 2026-04-20, the repo does not yet include the `openai` Python package in `/Users/avijaychakravorti/Desktop/Learning/PythonReview/requirements.txt`
- no project-specific OpenAI example code is checked in yet
- this directory includes a docs map and a first-practice plan, but no starter solution code

## First Docs To Read

1. [Developer quickstart](https://platform.openai.com/docs/quickstart?lang=python)
2. [Responses API reference](https://platform.openai.com/docs/api-reference/responses/compact?api-mode=responses)
3. [Text generation guide](https://platform.openai.com/docs/guides/chat-completions)
4. [Streaming API responses](https://platform.openai.com/docs/guides/streaming-responses)
5. [Function calling guide](https://platform.openai.com/docs/guides/function-calling)
6. [Structured model outputs](https://platform.openai.com/docs/guides/structured-outputs)

## Core Ideas To Lock In

### 1. Start With The Responses API

For new work, start from the Responses API examples in the official docs and learn that request and response shape first.

### 2. Separate Setup From Usage

There are four distinct steps to keep straight:

- having an OpenAI account
- creating an API key
- exporting `OPENAI_API_KEY` in your shell
- installing and using the Python SDK

### 3. Keep The First Request Small

The first success case should be one short text request and one printed result. Do not mix in streaming, tools, or JSON formatting until the plain request works.

### 4. Learn The Response Shape Early

Do not treat the SDK call as magic. Understand what request you send, what object comes back, and why `response.output_text` is a convenience rather than the entire response structure.

### 5. Add Complexity One Layer At A Time

Recommended order:

1. basic text generation
2. conversation state
3. streaming
4. structured outputs
5. function calling

## Working Rule For This Lesson

- do not store API keys in tracked files
- do not keep prewritten solution code here before the lesson step needs it
- add examples only when you are actively learning that specific step
- use the `autolessons` log to track quiz attempts, confusions, and corrections

## Suggested Next Step

Read the quickstart and the docs map in this directory, then write the smallest possible Python request only after the SDK and API key are set up locally.
