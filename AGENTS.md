# AGENTS.md

This repo is used as a guided learning workspace. New Codex chats should recover context quickly and preserve lesson continuity.

## First-Chat Workflow

1. Read [README.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/README.md) first.
2. If the user has not already made the lesson focus explicit, ask which learning directory or lesson directory is currently in focus.
3. Read the relevant lesson files and the relevant `autolessons` quiz log before teaching or editing.
4. If recent progress is unclear, ask the user for any missing context rather than assuming.

## Lesson Logging Rules

- Each lesson directory should get an `autolessons/` subdirectory once the lesson needs quizzes, progress tracking, or handoff continuity.
- Create the quiz log inside the in-focus learning directory, not at repo root.
- Use one row per question-attempt for all quiz logs.
- Keep quiz logs append-only in spirit: preserve older attempts and add later attempts as new rows.

## Required Quiz Log Shape

Use a markdown table with these columns:

| Date | Quiz | Lesson Dir | Source File | Q# | Attempt # | Prompt Summary | User Answer | Status | Feedback | Progress Notes |
|---|---|---|---|---:|---:|---|---|---|---|---|

Notes:
- One row represents exactly one user attempt at one question.
- If a user later improves the same answer, add another row for the new attempt instead of overwriting the prior row.
- Keep prompt summaries short but specific enough to recover the concept later.
- Status should be values such as `correct`, `partially correct`, `not yet correct`, or `clarified`.

## Progress Recovery

To understand recent progress in a new chat:

1. Read [README.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/README.md).
2. Read the relevant lesson directory's `autolessons` files.
3. Check recently modified files if needed.
4. Ask the user to confirm the active lesson if there is any ambiguity.

## README Maintenance

- At the conclusion or pause of a lesson, update [README.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/README.md) with the current lesson state, recent progress, open questions, and next steps.
- New Codex chats should treat the README as the high-level handoff document and the lesson quiz logs as the detailed attempt history.
