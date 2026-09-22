# NBAPI Working Guide

## Context discipline

- Start with `HANDOFF.md`, then use `rg` to locate the relevant function or DOM ID.
- Read only the matching line ranges. Do not load all of `server.py` or `assets/nbapi.js` unless the task genuinely spans the whole file.
- Keep command output focused. Prefer filtered logs and short tails over full files.
- Do not load local databases, certificates, private keys, backups, generated previews, or spreadsheet inspection dumps into model context.
- After a major feature is complete, update the concise current-state section in `HANDOFF.md` and continue unrelated work in a fresh task.

## Ownership map

- `api-website.html`: page structure and stable DOM IDs only.
- `assets/nbapi.css`: all visual styles and responsive layout.
- `assets/nbapi.js`: browser state, API calls, rendering, and event handlers.
- `server.py`: HTTP API, authentication, proxying, billing, payment, database migrations, and static file serving.
- `tools/test_usage_parsing.py`: billing, usage parsing, streaming, and protocol regression tests.
- `nbapi.nginx`, `nbapi.service`: production service definitions.

## Safety rules

- Preserve existing API paths, JSON fields, DOM IDs, role checks, database columns, and billing semantics unless the task explicitly changes them.
- Changes to proxying, usage parsing, reservations, settlement, refunds, ZPAY, or authentication require focused regression tests.
- Never commit `nbapi.sqlite3`, `.env`, certificates, private keys, logs, backups, or generated inspection files.
- Run Python syntax checks, JavaScript syntax checks, regression tests, and `git diff --check` before deployment.
