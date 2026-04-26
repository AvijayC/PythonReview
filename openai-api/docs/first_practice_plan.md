# OpenAI API First Practice Plan

This plan keeps the first practice run small and observable.

## Phase 1: Setup

1. Create an API key in the OpenAI dashboard.
2. Export `OPENAI_API_KEY` in your shell.
3. Install the Python SDK into the repo environment with `pip install openai`.

Stop and explain:

- where the key lives
- why it should not be committed
- how the SDK finds the key

## Phase 2: First Request

1. Create one tiny Python file in this directory.
2. Initialize the client with `OpenAI()`.
3. Make one short `client.responses.create(...)` call.
4. Print the returned text.

Stop and explain:

- what the `model` field does
- what the `input` field does
- what came back from the API

## Phase 3: Inspect The Response

After the first success case:

1. Print the full response object or inspect its fields.
2. Compare the full object with `response.output_text`.
3. Write down which fields feel obvious and which still feel opaque.

## Phase 4: First Controlled Variations

Only after the first plain request works:

1. change the prompt but keep the rest identical
2. try a slightly longer response
3. stream the same task
4. compare normal output versus structured output for a simple schema

## Working Rule

Change only one dimension at a time. If the request fails, reduce the script back to the smallest known-working version before adding anything else.
