# Agent Instructions (Coding Agents Only)

_Last updated: 2026-01-09 10:45 IST_

These instructions apply to all coding agents (e.g., Codex, GPT-5.2) working in this repo.

## Purpose
- Provide clear, predictable collaboration by requiring clarification before assumptions or structure decisions.
- Reduce token waste and avoid unnecessary output or temporary artifacts.

## Must-Do Rules
- Ask clarifying questions before writing or editing anything when instructions are ambiguous or would require assumptions.
- Confirm expectations at the start of each task: structure, location, length, tone, and style.
- Wait for explicit confirmation before proceeding if any of the above are unclear.
- Follow the user's instructions exactly; do not assume missing details.
- Review the full chat context before starting work to ensure all instructions are captured.
- Apply instructions across the entire repo (all directories), unless the user explicitly scopes otherwise.

## Clarifying Questions (Required When Ambiguous)
Ask questions if any of the following are unclear:
- Where to write (file path or new vs. existing file).
- What structure to use (sections, headings, formatting, templates).
- Desired length, tone, and style.
- Any assumptions about scope, constraints, or audience.

If instructions are clear and fully specified, proceed without additional questions.

## Token and Output Discipline
- Do not create intermediary markdown files or temporary docs unless explicitly requested.
- Do not print or paste long content into the console unless explicitly asked.
- Avoid unnecessary command output; summarize results instead.
- If a potential action would waste tokens (e.g., drafting large text without confirmed expectations), ask for confirmation first.

## Writing and Editing
- Use the minimal number of file edits to satisfy the request.
- Prefer edits to the requested file/location; do not create new files unless explicitly asked.
- Keep edits focused on the user’s stated goals; avoid unrelated refactors.

## Confirmation Flow
At the start of each task, confirm:
- Target file(s)/path(s)
- Structure and format
- Length, tone, style
Once confirmed, proceed without repeated questioning unless new ambiguity arises.
