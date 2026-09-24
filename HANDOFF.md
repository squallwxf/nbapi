# NBAPI Current Handoff

Updated: 2026-09-25

## 2026-09-25 explicit model supplier management

- Added `gpt-6-sol` as a hidden OpenAI Responses model with the same approved dynamic two-tier prices and `272K` threshold as `gpt-5.6-sol`. It has no supplier assignment by default and cannot be shown until a super administrator assigns at least one supplier.
- Existing models keep the legacy `channels.allowed_models` routing behavior unchanged. Only newly created models use explicit many-to-many supplier assignments, preserving every historical model/channel relationship.
- The super-admin “供应商对接” area is now “供应商管理” with create, edit, test, enable/disable and delete actions. Deleting the final assigned supplier automatically hides affected explicit models.
- Fixed supplier creation consuming the POST body twice. The create form now validates required fields, shows a submitting state and reports API errors inline.
- Added the OpenAI-compatible `GET /v1/models` catalog for Codex and other clients. It lists active models allowed by the requesting API token, and the playground refreshes its model list when opened or after visibility changes.
- The pricing page can create and configure models with protocol, pricing, visibility and multiple supplier selections. Supported protocol metadata covers OpenAI Chat/Responses, Anthropic Messages, Gemini Generate Content, images and videos.
- `/api/admin/models` provides super-admin model creation/listing; the existing model update endpoint now supports metadata and explicit supplier assignments. Public `/api/models` includes protocol and endpoint metadata without exposing API keys.
- The playground recognizes OpenAI Responses models and extracts Responses API output text. Frontend JavaScript uses release query `v=20260925.3` so the model list refresh fix is not hidden by browser or CDN caches.
- Regression coverage is now 37 tests, including seed idempotency, legacy routing preservation, explicit supplier routing, API validation, model discovery and automatic hiding after supplier deletion.

### New-server deployment status

- Deployed on 2026-09-25 only to the current server `195.72.185.130` in `/opt/nbapi`; the legacy server was not changed.
- Pre-deployment rollback archive: `/opt/nbapi-backups/nbapi-pre-model-discovery-20260925-0224.tar.gz`, SHA-256 `eff1e565efd81504d385453e29b27b417421c2a131e07610072808b4669ad3e0`.
- `nbapi.service` is active, `https://nbapi.win/health` returns `ok`, and the public page references `assets/nbapi.js?v=20260925.3`.
- A real active NBAPI token verified that `GET /v1/models` returns an OpenAI-compatible list containing active `gpt-6-sol`. Requests without a token return `401`.
- The `qiaomo` supplier base URL was normalized in production from `https://qiaomoapi.cn/v1` to `https://qiaomoapi.cn`; the proxy appends `/v1/responses` itself.
- Remaining external blocker: TLS negotiation from the new server to `qiaomoapi.cn:443` times out. The supplier must allow the new server IP `195.72.185.130` or remove the applicable region/CDN/firewall restriction. Until then the model is discoverable but real calls through this supplier will fail.
- After supplier access is restored, run the supplier connection test and confirm a healthy status before selecting `gpt-6-sol` in Codex. Codex uses `base_url = "https://nbapi.win/v1"`, `wire_api = "responses"`, and `model = "gpt-6-sol"`.

## 2026-09-23 dynamic tier billing

- The three models shown with upstream context-length pricing now use NBAPI dynamic billing: `gpt-5.6-sol` switches at `272K`, `gpt-5.6-terra` at `200K`, and `gpt-6-astra` at `272K` input tokens. `gpt-5.6-sol` keeps its separately approved customer rates; `gpt-5.6-terra` and `gpt-6-astra` use 1.8x the screenshot upstream rates. Each second tier follows the upstream multipliers: input/cache x2 and output x1.5.
- `gpt-5.6-sol` first tier is input `1.7000`, output `14.5000`, cache read `0.1170`, cache create `1.4625`; second tier is `3.4000`, `21.7500`, `0.2340`, `2.9250` USD per 1M tokens.
- `gpt-5.6-terra` first/second tiers are `0.7020 / 6.0120 / 0.0702 / 0.8775` and `1.4040 / 9.0180 / 0.1404 / 1.7550`; `gpt-6-astra` first/second tiers are `3.5100 / 17.5500 / 0.3510 / 4.3875` and `7.0200 / 26.3250 / 0.7020 / 8.7750` USD per 1M tokens.
- The migration adds only dynamic pricing columns and fills them once. Correction version 2 applies the approved prices to these three dynamic models; it does not rewrite users, balances, tokens, channels, or historical ledger rows.
- Final settlement selects the tier from authoritative upstream input usage, including the threshold boundary; reservation estimates use the same selector. Input, output, cache-read and cache-create charges all use the selected tier.
- `/api/models` and the super-admin pricing screen expose both tiers, thresholds and all four prices. The model plaza displays the same dynamic pricing information.
- The model plaza keeps dynamic cards compact by showing only the first-tier input, output, cache-read and cache-create prices. The clickable `动态计费 · 2档` label opens a responsive detail dialog with the threshold and both complete pricing tiers; this is presentation-only and does not change settlement behavior.
- The page references the plaza CSS and JavaScript with release query `v=20260923.2` so browsers and Cloudflare do not keep serving the pre-dialog assets from the four-hour static cache.

## 2026-09-23 pricing correction

- `gpt-5.6-sol` customer pricing is set to input `1.7000` and output `14.5000` USD per 1M tokens, with cache read `0.1170` and cache write `1.4625` USD per 1M tokens. The input/output values are the approved fixed rates; cache values are the upstream reference rates plus 50%.
- The one-time `dynamic_pricing_correction_version=2` migration aligns all three production rows and the code defaults with these values; the production database is backed up before deployment.
- Existing ledger rows are not rewritten. New calls use the corrected prices after the service reload.

## Read this first

This file is the concise current state. Older investigations and deployment history are preserved in `docs/HANDOFF_HISTORY.md`; search that file only when a task needs historical detail.

Repository: `https://github.com/squallwxf/nbapi`

Production:

- Site: `https://nbapi.win`
- App directory: `/opt/nbapi`
- Service: `nbapi.service`
- Backend: Python `ThreadingHTTPServer` on `127.0.0.1:8765`
- Reverse proxy: Nginx
- Production database and `/etc/nbapi.env` must never be overwritten by deployment.

## Current architecture

- `api-website.html`: page structure and stable DOM IDs.
- `assets/nbapi.css`: extracted visual styles and responsive layout.
- `assets/nbapi.js`: extracted browser logic, rendering, API calls, and event handlers.
- `server.py`: API, authentication, SQLite migrations, upstream proxy, protocol bridge, billing, refunds, ZPAY, and static asset serving.
- `tools/test_usage_parsing.py`: 37 regression tests covering usage parsing, dynamic tier selection, supplier routing, model management and discovery, approved customer rates, reservations, settlement, refunds, streaming, disconnect behavior, Gemini bridging, ZPAY idempotency, and static assets.
- `AGENTS.md`: context and safety instructions for future Codex work.

The frontend extraction is behavior-preserving: CSS and JavaScript were copied byte-for-byte after line-ending normalization, and all 190 DOM IDs remain unchanged. `server.py` now serves only the fixed asset paths `/assets/nbapi.css` and `/assets/nbapi.js`; arbitrary filesystem paths are not exposed.

## Production-critical behavior

- Real model calls use authenticated `/v1`, `/v1beta`, and compatible proxy routes.
- Per-token billing settles only from authoritative upstream input/output usage. Unverifiable usage is refunded instead of estimated and charged.
- Reservations are atomic, capped, idempotent, and finalized exactly once.
- Failed upstream calls refund the reservation. Client disconnects do not cancel upstream reading or final settlement.
- Native SSE is forwarded immediately with Nginx buffering disabled for that response.
- Gemini native models can be bridged from OpenAI chat requests and converted back to OpenAI-compatible responses.
- Channel routing keeps one matching enabled channel as a recovery probe when every matching channel is in health cooldown; this prevents transient `no_eligible_upstream_channel` errors without bypassing model allowlists.
- ZPAY credits paid orders transactionally and idempotently. Current user-facing payment method is Alipay only.
- Wallet orders, transactions, usage logs, tokens, and balances are scoped to the authenticated user. Super administrators have explicit elevated views.
- API token secrets remain copyable from the token page and must not be invalidated by normal code deployments.

## Roles

- User: own tokens, wallet, playground, usage logs, and API access.
- Admin: managed customer list and customer recharge statistics.
- Super admin: admin capabilities plus balances, model pricing/visibility/deletion, customer assignment, channels, and scoped/all-user logs.

## Required verification

Use an available Python 3 executable; on the Codex desktop host the bundled runtime can be obtained with `load_workspace_dependencies`.

```powershell
python -m py_compile server.py
python -m unittest tools.test_usage_parsing -v
node --check assets/nbapi.js
git diff --check
```

Expected regression result: 37 tests pass.

For frontend changes, verify desktop and mobile widths, browser console errors, authentication visibility, and no horizontal overflow. For proxy or billing changes, also run a real low-cost streaming request against a controlled account and reconcile reservation, ledger amount, wallet balance, usage source, and upstream charge.

## Deployment safety

Before deploying:

1. Commit and push only source and documentation.
2. Confirm that `nbapi.sqlite3`, `.env`, certificates, private keys, logs, backups, and generated inspection files are absent from the commit.
3. Back up the production SQLite database.
4. Pull the selected commit in `/opt/nbapi`.
5. Restart `nbapi.service` and check `/health`, service logs, the homepage, CSS, and JavaScript asset responses.
6. Do not copy a local database or local environment file to production.

Production secrets belong only in `/etc/nbapi.env`. Important variable families include super-admin bootstrap password, ZPAY merchant settings, SMTP password reset settings, upstream timeouts, reservation cap, and allowed origins. Never record their values in Git.

## Known operational finding

Long Codex desktop tasks can send roughly 40 MB of accumulated context per model request. NBAPI receives that body and forwards it upstream, so server aggregate receive/send traffic is roughly twice the request body before responses. The repository source itself is only about 0.5 MB; the primary cause is long conversation history, screenshots, and tool output, not application code size.

For future work:

- Start from this file and `AGENTS.md`.
- Use `rg` and narrow line reads instead of loading whole large files.
- Open a fresh task after each major feature and carry only this concise handoff.
- Keep command output and screenshots focused on the fault being investigated.

## Next safe improvements

- Add response-byte and per-user traffic metrics before making hosting decisions.
- Add HTTP-level tests for authentication scope, wallet queries, token persistence, static assets, and administrative permissions.
- Only after those tests exist, consider splitting backend domains out of `server.py`. Do not refactor billing, proxy, payment, and auth simultaneously.
