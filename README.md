# PythonReview

This repo is a structured learning workspace rather than a single software project. It is used to track lessons, examples, quiz attempts, and progress across Python and adjacent topics.

## Start Here

Any new Codex chat working in this repo should:

1. Read this file first.
2. Read [AGENTS.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/AGENTS.md).
3. Confirm the current lesson directory with the user if it is not already explicit.
4. Read the relevant lesson files and any `autolessons` logs in that lesson directory before continuing.

## Current Status

Date: 2026-04-20

Active lesson:
- `openai-api`
- current focus: initial onboarding for learning the OpenAI API from official docs, starting with the Python quickstart and the Responses API
- implementation status: lesson scaffold added with a lesson README, docs map, first-practice plan, and an empty quiz log

Recent progress:
- created [openai-api/README.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/openai-api/README.md)
- added [openai-api/docs/official_docs_map.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/openai-api/docs/official_docs_map.md) with current official-doc entry points
- added [openai-api/docs/first_practice_plan.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/openai-api/docs/first_practice_plan.md) to stage the first hands-on steps
- added [openai-api/autolessons/openai_api_quiz_log.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/openai-api/autolessons/openai_api_quiz_log.md)
- previous lesson context in `snippets/sql_parsing` remains available if that thread resumes later

Current understanding:
- this lesson should start with the official quickstart and the Responses API rather than older OpenAI API patterns
- the repo does not yet include the `openai` Python package in [requirements.txt](/Users/avijaychakravorti/Desktop/Learning/PythonReview/requirements.txt)
- no lesson code has been checked in yet by design; the directory is set up for guided practice

Known next topics:
- install the `openai` SDK into the repo environment when ready
- export `OPENAI_API_KEY` locally without checking secrets into the repo
- write a first Python request with `client.responses.create(...)`
- practice streaming, structured outputs, and function calling after the first plain-text request works

## Lesson Tracking Convention

- Each lesson directory can get an `autolessons/` subdirectory for quiz logs and lesson handoff notes.
- Quiz logs should use one row per question-attempt.
- On pausing or concluding a lesson, update this README with a short status snapshot so future chats can recover context quickly.
