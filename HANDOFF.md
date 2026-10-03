# NBAPI Current Handoff

Updated: 2026-10-03

## 2026-10-03 download layout — deployed

- Fixed inherited grid stretching on the download route with start alignment; removed empty status spacing. Catalog uses full-width horizontal screenshot/content rows on desktop and single-column cards on smaller screens. Summaries clamp to three lines in the catalog; detail retains full text. Download buttons wrap safely and show concise platform/size labels instead of long filenames; original filenames remain available in tooltips/details. Cross-platform package labels infer Windows/macOS/Linux from clear filenames for presentation/filtering only; stored metadata and download URLs are unchanged.
- CSS/software JS release `v=20261003.1`. Replaced only HTML, CSS and software JS, without backend restart or DB changes. Backup `/opt/nbapi-backups/download-layout-20261002-164316` (server UTC directory timestamp). Local and server staging passed all 52 regressions; syntax/diff checks passed. Live NB智能画布 verified at desktop and 390px viewport with no horizontal overflow; Windows/macOS download links retain original IDs. Service health active/ok. Screenshot `C:/Users/Administrator/AppData/Local/Temp/nbapi-downloads-layout-fixed.png`.

## 2026-10-02 1 GiB and multiple installers — deployed

- Installer limit is now 1 GiB (1024 MB) per file. Browser sends sequential 8 MiB chunks to the existing super-admin upload route; every chunk carries original-byte SHA-256, upload ID, offset and total. Server binds uploads to owner/name/total, rejects offsets/concurrent writes and checks all stored chunks again before registering a file. Final SHA-256 covers the assembled installer. Screenshots remain 8 MiB each. Whole installers are never buffered/unpacked/executed. Incomplete `.partial`/`.upload.json` files stay private and are retained; an interrupted browser upload starts a new upload ID on retry. A process crash can leave a `.lock` directory requiring operator cleanup for that old upload ID.
- Same software release supports multiple platform-labelled packages sharing version/screenshots/description. Additive `software_release_installers` table; existing `installer_id` and original download route are preserved. Catalog includes `installers`; platform-specific download routes validate release membership and publication. Old releases without association rows fall back to their original installer. Editor supports multi-select/append/remove/platform labels; public page has separate Windows/macOS/etc. buttons and hashes. Frontend release queries for CSS/software JS are `v=20261002.5`.
- All 52 tests pass, including existing 44 billing/protocol regressions. Added chunk checks, >112 MiB transfer and exact hash, size boundary, wrong owner/offset/name/total/checksum, disk corruption rejection, legacy releases, multi-platform download/Range/edit/remove/unpublish. Browser local super-admin uploaded a harmless 131,257,298-byte ZIP plus a tiny macOS fixture under one release; public download size/hash equals original exactly. No production sample or paid call made. Syntax/diff checks pass.
- Deployed after connectivity recovered on 2026-10-02; CSS/software JS `v=20261002.5`. Server staging passed all 52 tests. An initial static-resource failure was caused by missing existing `assets/nbapi.js` in staging; copying the unchanged production file fixed the fixture. Backup of replaced sources and consistent SQLite snapshot: `/opt/nbapi-backups/multi-installer-20261002-155120`. Replaced only software module, software JS, HTML, CSS and software tests; preserved production DB/environment/billing sources. Existing Nginx 500m permits 8 MiB requests; no proxy-size change needed. Restart/local and public health passed, public catalog returns 200, unauthenticated admin catalog returns 401. Live browser verified new asset versions, multiple file input and 1 GB copy. No production test release or paid call made; large upload and exact download/hash were verified locally and in server-isolated tests, not with a full 1 GiB production transfer.

## 2026-10-02 software downloads — deployed

- New top navigation and mobile link `NB ai工具下载` opens the public `#downloads` page in the existing app shell. Catalog includes search/platform filters, screenshots, version, description, install instructions, system requirements, changelog, file size and SHA-256. Existing light/dark theme and responsive styles are reused.
- Only super-admins can upload installation packages/screenshots, create releases or edit/publish/unpublish them. Forms include upload progress, screenshot previews, required metadata and errors. New versions are separate release entries; editing can retain existing files. Unpublished files cannot be downloaded through public routes. Downloading is free and has no billing side effects.
- Isolated backend module `software_downloads.py`, frontend `assets/software.js`, and additive tables `software_files`/`software_releases`. Files live beside the database in `software-storage/`, or `NBAPI_SOFTWARE_DIR`; exclude them from Git and back them up separately. Random storage IDs prevent user filenames becoming paths. Packages are streamed in 1 MB chunks and never executed/unpacked. Downloads support HTTP Range. Screenshots are restricted to signature-checked PNG/JPEG/WebP.
- Installer limit 90 MB (below usual CDN single-request limits); screenshot limit 8 MB, 1–6 per release. ZIP/7z/EXE/MSI/DMG/PKG/DEB/RPM/AppImage/tar.gz supported. Uploaded but unused files remain private and retained; no automatic cleanup/deletion. Larger installers require a future chunked/object-storage upload design. No existing payment, wallet, model proxy or billing code changed.
- 47 tests passed: all 44 existing tests and 3 new real-HTTP software tests covering publish/edit/unpublish, exact file download/hash, Range, role denial, invalid file types/paths/sizes, screenshot validation, drafts and missing metadata. Browser localhost verified super-admin login, upload with preview, publish, details, download and logout; preview fixtures are only in a temporary database. Screenshot: `C:/Users/Administrator/AppData/Local/Temp/nbapi-software-preview.png`.
- Deployed on 2026-10-02 after VPN was disabled and SSH access recovered. Release `v=20261002.4`; backup source and consistent SQLite snapshot at `/opt/nbapi-backups/downloads-20261002`. Server staging passed all 47 tests before replacing sources. Fixed a publication race exposed by Linux tests: commit release metadata before returning success, so an immediate public refresh sees the release. Restart and localhost/public health passed; public catalog and assets return 200, unauthenticated management returns 401, authenticated super-admin catalog returns 200. Live browser shows the download link/page with an empty catalog. No sample software was published in production and no production balance was changed. Local browser and isolated real HTTP tests cover uploads/downloads.

## 2026-10-02 own super-admin balance — deployed with downloads

- Added a dedicated 我的余额（超级管理员） card at the top of user management, independent of user search/pagination. It sets the total balance using the existing super-admin-only `PUT /api/admin/users/{currentUser.id}` endpoint. Saves update the header balance immediately; user list refresh reads `/api/me`. Other roles do not see the card and the handler rejects them.
- Backend already permits super-admin self balance updates; no backend change is required. Amount limits and six-decimal precision reuse existing validation. New frontend release query: `v=20261002.3`.
- All 44 regression tests pass, including self balance precision, `/api/me` consistency, rejection of admin/user edits and invalid amounts, self-role protection and preservation of other accounts. JavaScript handler fixture checks pass for super-admin/admin/user. Syntax and diff checks pass. No production balance was modified for verification.
- Deployed together with downloads on 2026-10-02, release `v=20261002.4`. Own-balance markup and scripts verified publicly; existing super-admin `/api/me` confirmed with a temporary verification session, then session removed. No live balance edit performed.

## 2026-10-02 RMB display only

- All built-in frontend monetary dollar symbols now display `¥`; dollar currency labels now say 人民币. Numeric values, precision, form input values, submitted payloads and JavaScript template expressions are unchanged. This is a display relabeling with no exchange-rate conversion.
- Covers wallet/top-up, dashboard/header balance, model plaza and tier dialog, pricing, token quota, user/customer management, usage ledger and playground charge/refund messages. User-authored content is untouched.
- Backend and regression-test source bytes were verified unchanged from the start of this task. All 43 existing regression tests, Python/JavaScript syntax checks and diff checks passed. Fixture comparisons for guest/user/admin/super-admin roles preserve amount values, input attributes and controls; complete frontend source comparisons permit only the approved text replacements and JS release query.
- Deployed only `api-website.html` and `assets/nbapi.js`, release `v=20261002.2`. Frontend rollback copies: `/opt/nbapi-backups/rmb-display-20261002`. No backend restart, database writes, real recharge or paid model test was needed. Production backend SHA-256 remains `6d7ec3c6f799227f87bb0b18f74124bbe7b9ef15fcba1a965197762b47d7219d`; service and public health check remain healthy.

## 2026-10-02 GPT image supplier management

- `gpt-image-2` now uses explicit supplier selections in the pricing page. The one-time migration preserves the enabled suppliers permitted by its former allowlists, its visibility and its $0.22/task customer price; production assignments remain suppliers 1 and 2.
- Added visible `gpt-image-2-super` with provider label GPT 图片 Super, provider 巧模, OpenAI Images protocol and `/v1/images/generations`. Production assigns only existing `qiaomo` supplier 217. Its initial $0.22/task customer price copies `gpt-image-2`; this is provisional customer pricing, not a confirmed upstream cost. Subsequent administrator supplier/price/visibility edits survive restarts.
- Playground GPT image requests convert ratio/resolution to pixel dimensions, use the documented `size` field and omit the unrelated `image_size`. Completed URL or Base64 results are displayed before considering task IDs, since the supplier returns both a completed URL and task ID.
- `/v1/images/edits` now reads the model from multipart form metadata while forwarding image bytes unchanged. Other protocol routing and billing semantics are unchanged.
- Local and server staging checks passed all 43 regression tests plus JavaScript syntax and focused image request/response checks. Direct upstream and production gateway generation tests returned HTTP 200 with image URLs at 1024x1024; the gateway charged $0.22 and this verification charge was returned through an audited deployment_test_refund.
- Deployed to the current server 195.72.185.130. Rollback source and SQLite snapshot: `/opt/nbapi-backups/image-models-20261002`. JavaScript release query is `v=20261002.1`. Public model catalog and authenticated admin pricing catalog both contain the two models.
- Production gateway multipart image editing also returned HTTP 200 with an image URL; its $0.22 verification charge was returned with a deployment_test_refund audit entry. Generation and editing used synthetic circle/white-background test content. Verified the new card in the public model plaza. Higher resolutions and asynchronous-only image responses have not been live-tested.
- Preserved the production GPT 6.1 Sol seed metadata correction (OpenAI/dialogue) in local source.

## 2026-09-30 GPT 6.1 Sol preparation

- Added `gpt-6.1-sol` as a hidden, explicit-supplier OpenAI Responses model. The one-time seed copies the current `gpt-6-sol` pricing and dynamic tiers, then preserves any later super-admin price changes. It does not change the existing `gpt-6` alias or its canonical `gpt-6-sol` route.
- Before making the new model visible, confirm the upstream supplier accepts the exact model ID `gpt-6.1-sol` through `/v1/responses`, assign that supplier in the model pricing page, and set the customer price from confirmed upstream pricing. The copied `gpt-6-sol` rates are provisional.
- Codex support for the exact new ID depends on its installed client model picker/configuration. Do not repoint the existing `gpt-6` alias; if Codex rejects `gpt-6.1-sol` before sending an HTTP request, verify client support and choose an unused compatible alias only after checking for collisions.
- Local regression tests cover seed idempotency, hidden state, supplier requirement and model discovery. No live upstream or Codex end-to-end verification has been completed for this new model.

## 2026-09-25 Codex compatibility alias

- Added the transparent client alias `gpt-6` for the canonical `gpt-6-sol` model because current Codex clients recognize `gpt-6` but do not expose `gpt-6-sol` in their built-in picker.
- `/v1/models` now publishes both IDs when `gpt-6-sol` is active and allowed for the token. Requests using `gpt-6` are normalized before authorization, supplier routing, reservation, settlement and ledger writes; the supplier always receives `gpt-6-sol`.
- The model plaza labels the Codex compatibility name and remains searchable by either ID. Pricing and historical identity remain attached only to `gpt-6-sol`.
- Deployed to `195.72.185.130` on 2026-09-25. Database and replaced-source backups are in `/opt/nbapi-backups/alias-20260925-123901`; checksums are recorded in that directory.
- Production verification returned HTTP `200` through the `gpt-6` alias with authoritative usage of 3,714 input and 5 output tokens. The ledger recorded canonical model `gpt-6-sol`, charge `$0.007354`, and `openai_compatible` usage; the supplier remained healthy. The verification charge was fully returned to the affected account with a `deployment_test_refund` audit transaction.

## 2026-09-25 explicit model supplier management

- Added `gpt-6-sol` as a hidden OpenAI Responses model with the same approved dynamic two-tier prices and `272K` threshold as `gpt-5.6-sol`. It has no supplier assignment by default and cannot be shown until a super administrator assigns at least one supplier.
- Existing models keep the legacy `channels.allowed_models` routing behavior unchanged. Only newly created models use explicit many-to-many supplier assignments, preserving every historical model/channel relationship.
- The super-admin “供应商对接” area is now “供应商管理” with create, edit, test, enable/disable and delete actions. Deleting the final assigned supplier automatically hides affected explicit models.
- Fixed supplier creation consuming the POST body twice. The create form now validates required fields, shows a submitting state and reports API errors inline.
- Added the OpenAI-compatible `GET /v1/models` catalog for Codex and other clients. It lists active models allowed by the requesting API token, and the playground refreshes its model list when opened or after visibility changes.
- The pricing page can create and configure models with protocol, pricing, visibility and multiple supplier selections. Supported protocol metadata covers OpenAI Chat/Responses, Anthropic Messages, Gemini Generate Content, images and videos.
- `/api/admin/models` provides super-admin model creation/listing; the existing model update endpoint now supports metadata and explicit supplier assignments. Public `/api/models` includes protocol and endpoint metadata without exposing API keys.
- The playground recognizes OpenAI Responses models and extracts Responses API output text. Frontend JavaScript uses release query `v=20260925.3` so the model list refresh fix is not hidden by browser or CDN caches.
- Regression coverage is now 39 tests, including seed idempotency, legacy routing preservation, explicit supplier routing, alias normalization, API validation, model discovery and automatic hiding after supplier deletion.

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
- `tools/test_usage_parsing.py`: 39 regression tests covering usage parsing, dynamic tier selection, supplier routing, model aliases, model management and discovery, approved customer rates, reservations, settlement, refunds, streaming, disconnect behavior, Gemini bridging, ZPAY idempotency, and static assets.
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

Expected regression result: 39 tests pass.

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
