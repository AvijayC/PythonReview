# PythonReview

This repo is a structured learning workspace rather than a single software project. It is used to track lessons, examples, quiz attempts, and progress across Python and adjacent topics.

## Start Here

Any new Codex chat working in this repo should:

1. Read this file first.
2. Read [AGENTS.md](/Users/avijaychakravorti/Desktop/Learning/PythonReview/AGENTS.md).
3. Confirm the current lesson directory with the user if it is not already explicit.
4. Read the relevant lesson files and any `autolessons` logs in that lesson directory before continuing.

## Current Status

Date: 2026-04-12

Active lesson:
- `snippets/sql_parsing`
- current focus: Snowflake SELECT lineage tracing with `sqlglot==29.0.0`, normalized pydantic I/O models, and robust structured error reporting
- implementation status: single-file snippet added in [sql_lineage.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/snippets/sql_parsing/sql_lineage.py) with embedded Northwind-inspired tests

Recent progress:
- added [sql_lineage.py](/Users/avijaychakravorti/Desktop/Learning/PythonReview/snippets/sql_parsing/sql_lineage.py) under `snippets/sql_parsing`
- implemented `TableSchema`, `QueryLineageRequest`, `QueryLineageResult`, and related pydantic models for standardized input and output
- added validation for lowercased fully qualified table names, quoted identifier handling, duplicate schema definitions, missing table schemas, and non-FQTN physical table references
- added lineage tracing across joins, stars, computed expressions, CTEs, nested CTEs, nested subqueries, union branches, self-joins, and duplicate output names by position
- added 26 Northwind-inspired tests in the same file and verified them with `pytest -q snippets/sql_parsing/sql_lineage.py`
- cleaned up the local warning noise by updating type annotations for `beartype` compatibility and removing an unsupported pytest config entry

Current understanding:
- the snippet now resolves top-level output columns back to base table columns by combining `sqlglot` qualification with lineage traversal
- failure cases return structured error objects rather than raising uncaught exceptions
- quoted and unquoted fully qualified table names normalize to the same lowercase internal format

Known next topics:
- integrate the snippet into the downstream program and feed real `DESCRIBE TABLE` output into `TableSchema`
- add any production-specific Snowflake query edge cases that show up later
- optionally split tests from runtime code or clean up `beartype` generic-type deprecation warnings if those become noisy

## Lesson Tracking Convention

- Each lesson directory can get an `autolessons/` subdirectory for quiz logs and lesson handoff notes.
- Quiz logs should use one row per question-attempt.
- On pausing or concluding a lesson, update this README with a short status snapshot so future chats can recover context quickly.
