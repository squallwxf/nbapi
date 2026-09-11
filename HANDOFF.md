# NBAPI 接力文档

当前项目仓库：`https://github.com/squallwxf/nbapi.git`

## 最新：KRAPI 对账与耗时标签

- 用户两站截图可按模型和输入/补全 Token 匹配：95646/171 的 gpt-6-astra，KRAPI 总 10s、首字 4.7s，NBAPI 总 22.940s、首响应 17.211s。两指标增量约 12.94s/12.511s，表明额外延迟主要在首响应前。KRAPI 总用时显示有舍入，不能用差值算出精确网络耗时。
- 当前不能单凭截图认定是 DNS、TLS、上传、数据库或上游排队。自动 SSH 读取被服务器关闭，尚未在生产环境取得细分时序。
- NBAPI_STREAM_TIMING 新增 bodyReadMs（读完下游正文）、preparedMs（解析/路由/预扣完成）、upstreamStartMs、connectionMs（连接阶段累计含 DNS/TCP/TLS）、requestSentMs（发送完成）、upstreamWaitHeadersMs。其余时间为从请求起点累计毫秒。默认代理、HTTPS 证书校验和重定向保留；不改计费或篡改耗时。
- 日志两列已合并为“用时/首字”：绿色总用时、首字按 <3s 绿色/<10s 黄色/其余红色分级，有可测首流式数据时显示蓝色“流”。精度显示 1 位秒，悬停查看 3 位秒；未知首字显示 -。历史没有首字不据此断言非流式。
- 15 项后端测试通过，真实 HTTP 分段测试覆盖新的传输计时封装；前端 JS 语法和深浅色窄屏标签渲染检查通过。下一步部署后用同一条请求的两站记录和新增时序定位延迟，当前不能宣称已消除线上延迟。

## 最新：首 Token 已按 New API FRT 口径对齐

- 已下载并查阅 QuantumNous/new-api 提交 `74629e29f83f506bb523c5542aa851947bd423eb`。`relay/helper/stream_scanner.go:272` 在第一条非空且非 [DONE] 的 data 事件处调用 SetFirstResponseTime；`relay/common/relay_info.go:935` 仅记录一次；`service/log_info_generate.go:107` 写入 frt 毫秒，前端除以 1000 显示秒。
- NBAPI 现在同样记录首个 data 事件，不再等待正文/推理/工具调用增量。之前文档中“只有生成内容才计时”的口径已被此项替代。首 Token 标签表示首响应时间，可能由 response.created 等结构事件触发。
- 诊断日志同时保留 firstDataMs、firstContentMs、endMs，用于区分首响应与首正文。非流式与暂不支持的压缩流仍显示 `-`；历史时间无法还原，不改写旧账单。
- 15 项测试通过，包含真实本地 HTTP 分段传输。仍未取得 KRAPI 线上原始时序，不能保证所有请求的首响应一定小于总耗时很多；若上游集中返回，两者确实可能接近。
- 本轮网络曾连接重置，随后恢复并成功读取源码；下文下载失败记录仅为历史过程。

## 现在的状态

- 前端页面：`api-website.html`
- 后端服务：`server.py`
- 服务器域名：`nbapi.win`
- 对外调用地址：`https://nbapi.win/v1`
- 服务器项目目录：`/opt/nbapi`
- 本地项目目录：`D:\ai web`
- Nginx 已开启 443，HTTPS 和 Cloudflare 链路已验证通过
- 供应商管理已完成并可运营；当前是否可调用由各渠道的地址、Key、支持模型列表和健康状态共同决定。
## 下次换电脑怎么继续

1. 克隆仓库
2. 打开项目目录
3. 先看 `README.md`
4. 再看这份 `HANDOFF.md`
5. 需要修改页面就改 `api-website.html`
6. 需要改接口和计费就改 `server.py`
7. 如果继续排查供应商测试，先检查 NB 供应商的上游 API Key、上游地址和认证方式是否完整

## 本地代码上传服务器

推荐流程是“本地修改 -> GitHub -> 服务器拉取”，不需要每次手动上传文件：

### 本地电脑

在 PowerShell 中执行：

```powershell
cd "D:\\nbapi"
python -m py_compile server.py
git diff --check
git status --short
git add server.py api-website.html HANDOFF.md README.md
git commit -m "更新项目"
git push origin main
```

### 服务器

SSH 登录服务器后，逐条执行：

```bash
cd /opt/nbapi
python3 tools/backup_db.py
git pull
```

如果修改了 `server.py`：

```bash
sudo systemctl restart nbapi
curl -i https://nbapi.win/health
```

如果修改了 `nbapi.nginx`：

```bash
nginx -t && systemctl reload nginx
```

只修改 `api-website.html` 时，拉取后刷新浏览器即可；如果仍显示旧页面，使用 `Ctrl+F5`。

### 更新前注意

- 服务器首次配置 Git 时，需要先在 `/opt/nbapi` 克隆仓库；以后直接使用 `git pull`。
- 不要把本地 `nbapi.sqlite3` 推送后覆盖线上数据库。
- 线上数据库包含用户、余额、API Key、扣费记录和渠道密钥，更新前应先备份。
- 上游 API Key、管理员密码和服务器密码不要写入代码或提交到 GitHub；线上应通过环境变量或后台安全配置管理。

## 令牌安全规则

- API Key 创建成功时，完整值只在创建响应中返回一次。
- 令牌列表只返回脱敏值；服务端使用 SHA-256 哈希鉴权，不保存可复制的明文 Key。
- 令牌停用后立即不能继续调用；令牌所属用户必须处于启用状态。
- 数据库升级会清理旧版本遗留的明文令牌副本，但不会影响已有哈希鉴权。
- 为方便日常使用，当前浏览器会按用户名在本地缓存新建令牌的完整值，令牌列表可直接复制；更换设备或清理浏览器数据后无法恢复遗失的 Key。
- 令牌创建表单支持分组、过期时间、批量数量、额度/无限额度、模型白名单和 IP/CIDR 白名单。
- 模型白名单、IP 白名单、令牌额度和过期时间会在真实 `/v1`/`/v1beta` 调用时校验。
- 令牌列表支持单个/批量启用、禁用和删除；删除令牌前会解除账单关联，但历史扣费记录保留。
- 新增“操练场”页面：使用当前浏览器中缓存的用户令牌测试完整模型列表；对话、Gemini、图片和视频模型会根据模型类型选择对应端点。
- 操练场调用走真实上游代理，会执行令牌限制、余额检查和模型计费；没有可复制的完整 Key 时不能发起测试。
- 渠道地址可填写站点根地址，也可误填带 `/v1`/`/v1beta` 的地址，后端会自动去除版本后缀，避免重复拼接。
- 操练场图片模型提交任务后，会轮询 `/v1/images/tasks/{task_id}`，成功时展示图片地址和预览；轮询不会重复计费。
- 操练场图片和视频任务如果后续轮询到 `failed` / `error` / `cancelled`，后端会自动把本次按次扣费退回，并写入 `balance_transactions`。
- `sora-v4-*` 走 `/v1/videos`，提交体按 `duration + metadata.modeType=text2video` 发送，视频轮询已延长；不要再用旧的 `seconds` 逻辑去套它。
- 操练场调用完成后会读取服务器 `/api/me` 刷新余额，并读取 `X-NBAPI-Charged`/`X-NBAPI-Balance` 显示本次实际扣费和最新余额。
- 使用日志已改为真实账单页：按时间、令牌、模型、分组、Request ID、计费类型筛选，显示令牌归属、IP、耗时、输入/输出 Token、花费，并支持统计、详情展开、分页和每页数量。
- `ledger` 会自动增加 `client_ip`、`latency_ms`、`request_path`、`request_id` 字段；旧线上数据库启动时会自动迁移，旧记录的新增字段为空是正常现象。
- 生产环境建议设置 `NBAPI_SUPER_ADMIN_PASSWORD`（仅首次初始化新数据库时使用）和 `NBAPI_ALLOWED_ORIGINS`；已有超级管理员密码不会在每次启动时被重置。
- `GET /health` 可用于 Nginx、systemd 或监控探针；登录用户可通过 `POST /api/auth/password` 修改自己的密码，新密码至少 12 位。
- 登录和注册接口按客户端 IP 做基础限流（每分钟最多 10 次），跨域响应只允许 `NBAPI_ALLOWED_ORIGINS` 中的来源。
- 密码找回功能已加入：用户通过注册邮箱申请一次性重置链接，令牌只保存 SHA-256 哈希、默认 30 分钟有效且只能使用一次；重置成功会撤销该账号所有现有登录会话。SMTP 配置仅放服务器 `/etc/nbapi.env`：`NBAPI_SMTP_HOST`、`NBAPI_SMTP_PORT`、`NBAPI_SMTP_USERNAME`、`NBAPI_SMTP_PASSWORD`、`NBAPI_SMTP_FROM`，如使用 465 端口需设置 `NBAPI_SMTP_USE_SSL=1`；网站地址可由 `NBAPI_PUBLIC_BASE_URL` 配置。未配置邮件服务时接口会明确返回未配置，未知邮箱不会被枚举。
- `GET /api/dashboard` 返回实时模型数、启用渠道数，以及当前登录用户的今日调用、本月消耗、平均延迟和余额；首页统计不再使用硬编码演示数字。
- 上游调用会按渠道优先级依次尝试最多 `NBAPI_UPSTREAM_MAX_ATTEMPTS` 个渠道（默认 2）；网络错误、超时和 5xx 会记录失败并自动尝试下一渠道，3 次连续失败的渠道会熔断 5 分钟后再试。可通过 `NBAPI_UPSTREAM_TIMEOUT` 调整单次上游超时（默认 90 秒）。渠道管理页会显示真实健康状态和最近错误。
- 2026-09-09 已完善 ZPAY 订单链路：`POST /api/wallet/orders` 创建 ZPAY 待支付订单并返回标准页面跳转地址；`GET/POST /api/payment/zpay/notify` 接收回调，校验 `pid`、`TRADE_SUCCESS`、支付方式、订单金额和 MD5 签名后才自动入账。回调入账使用 SQLite 事务和订单状态保护，重复通知不会重复充值。待支付订单可通过 `POST /api/wallet/orders/{id}/sync` 由服务器向 ZPAY 查询结果，解决回调延迟或支付完成返回网站后尚未到账的情况；查询不会向浏览器泄露商户密钥，也不会重复入账。
- 钱包管理页面的充值档位固定为 `10/20/50/100` 元人民币，后端同步强制校验这四个档位；消费统计提供今日、本周、本月三个周期，并由服务器按北京时间计算边界，只计算 `ledger.status='charged'` 的真实调用，不包含充值、预扣和退款。充值采用 1 元人民币 = 1 个账户余额单位，模型余额显示仍沿用美元格式。
- 使用日志权限：普通用户和普通管理员只能查看自己的日志；超级管理员在日志页可选择“我的日志”或“所有用户”，后端通过 `scope=self/all` 强制过滤，默认重置为“我的日志”。
- 2026-09-09 Token 计费复核：所有按 Token 模型均按上游响应的真实输入/补全/缓存用量，以每 1M Token 的模型定价结算。已修复 Claude 原生 usage 中 `input_tokens` 不含 `cache_read_input_tokens` 却被二次减除的问题；Claude 现在分别结算普通输入、缓存读取、缓存写入和补全。OpenAI-compatible 与 Gemini 的总输入包含缓存 Token，仍会先剔除缓存部分再按缓存价计算。新增模型的零价格会在服务启动时仅补齐缺失价格，已存在的超级管理员自定义价格不会被覆盖。
- 已修复切换用户后使用日志沿用旧账号分页页码的问题：切换或退出账号时会重置日志页码、筛选状态、统计卡和列表，日志请求也会校验当前会话和用户 ID，旧账号的延迟响应不能覆盖新账号页面。
- 生产环境的 `/etc/nbapi.env` 必须自行配置 `NBAPI_ZPAY_PID`、`NBAPI_ZPAY_KEY`、`NBAPI_ZPAY_NOTIFY_URL=https://nbapi.win/api/payment/zpay/notify`、`NBAPI_ZPAY_RETURN_URL=https://nbapi.win/#wallet`、`NBAPI_ZPAY_MIN_TOPUP=1` 和 `NBAPI_ZPAY_MAX_TOPUP=10000`。可选的 `NBAPI_ZPAY_CID` 仅在 ZPAY 后台已确认支付宝渠道 ID 时设置；商户密钥绝不进入仓库。
- ZPAY 上线前必须在服务器配置 `NBAPI_ZPAY_PID`、`NBAPI_ZPAY_KEY`，并确认 `NBAPI_ZPAY_NOTIFY_URL=https://nbapi.win/api/payment/zpay/notify` 可从公网访问；配置后重启 `nbapi` 服务。未配置商户参数时，充值接口会返回 `zpay_not_configured`。
- ZPAY 回调还会拒绝已绑定到其他订单的 `trade_no`；数据库对非空商户订单号和上游交易号均建立唯一索引。
- 当前 ZPAY 商户仅开通支付宝，充值页面已隐藏微信选项，后端也会拒绝非支付宝支付方式。
- 模型价格已统一为客户价格：按 Token 的模型以每 1M Tokens 计费并区分输入、输出和缓存读写价格；按次模型以每次计费。价格初始化为参考截图价格的 2 倍，并通过 `pricing_schema_version` 防止每次启动覆盖超级管理员修改。
- 模型价格修改权限仅限超级管理员；后端 `/api/admin/models/{name}` 会拒绝普通管理员，模型广场只为超级管理员显示编辑控件。
- `D:\ai web\nbapi模型价格模板.xlsx` 是模型定价模板；本次已按用户修改后的有效价格更新后端，并将 `pricing_schema_version` 升级为 `4`，线上执行一次启动迁移后会持久化这些价格。
- 权限规则：管理员仅可查看用户列表和创建普通用户；超级管理员继承上述权限，并可设置用户余额、通过控制台的“模型定价”页面修改模型价格。模型广场仅用于查看模型与价格，不再提供改价入口。
- 2026-09-03 权限调整已写入代码：管理员创建的账号固定为普通用户且初始余额为 0；管理员不能修改已有用户。超级管理员只可设置用户余额。渠道管理、上游配置和充值审核接口已关闭；超级管理员的模型定价独立位于控制台“模型定价”页面。

## 第五阶段：自动支付与订阅

ZPAY 支付订单、标准页面跳转、支付宝限制、MD5 签名校验、异步回调、自动到账、服务端查单、重复通知幂等和充值上限已经实现。当前仍待 ZPAY 商户审核通过并完成真实支付宝支付联调；退款、套餐和订阅有效期暂未开放。

开始第五阶段前需要准备：

- 支付平台名称（支付宝、微信支付、Stripe 等）
- 商户号、应用/账户标识和回调域名要求
- API 密钥、证书或 Webhook 签名密钥（只放服务器环境变量，不提交 Git）
- 测试环境或沙箱账号

在支付渠道申请完成前，继续使用人工充值审核流程，不要把测试密钥写入仓库。

## 重要提醒

- `nbapi.sqlite3` 不要提交到 GitHub
- 用户余额、API Key、扣费记录都在数据库里
- 本地备份命令：`python tools/backup_db.py`
- 数据库路径可通过 `NBAPI_DB_PATH` 改
- 备份目录可通过 `NBAPI_BACKUP_DIR` 改
- 服务器改动后要记得同步到仓库
- 证书内容不要提交到 GitHub，只保留 Nginx 配置文件

## 2026-09-04 ZPAY 联调状态

- GitHub 已有 ZPAY 充值实现及“仅支付宝、回调验签自动到账”的代码，当前基线提交为 `4e42202`；该版本已移除超级管理员人工审核/手动入账界面和接口。
- 服务器 `/etc/nbapi.env` 已确认 `NBAPI_ZPAY_PID=2026090213005330`，且运行中的 `nbapi` 服务可读取 `NBAPI_ZPAY_KEY`。密钥绝不能写入仓库或聊天记录。
- 访问 `https://nbapi.win/api/payment/zpay/notify` 会返回 HTTP 400 和 `fail`，这是未携带真实支付通知参数时的正常结果，说明公网回调地址可到达。
- 当前支付跳转返回“商户尚未开通或开启支付宝渠道，请先开通或开启”。已确认 NBAPI 使用 `type=alipay` 且服务器 PID 与 ZPAY 后台 PID 一致；下一步应在 ZPAY 后台“支付渠道 -> 我的支付渠道”确认支付宝通道为已开通、已启用状态，并记录页面显示的渠道 ID（CID）。只有后台确有 CID 时，才将其填入服务器 `/etc/nbapi.env` 的 `NBAPI_ZPAY_CID` 后重启 `nbapi`。
- 云服务器 SSH 密码登录目前不稳定/可能拒绝认证；可通过云服务商网页 VNC/控制台进入服务器，再在 `/opt/nbapi` 执行 `git pull --ff-only origin main`、`systemctl restart nbapi` 和 `systemctl is-active nbapi` 完成部署。数据库 `nbapi.sqlite3` 与 `/etc/nbapi.env` 不在 Git 中，不能被 `git pull` 覆盖。
- 2026-09-04 已修复图片/视频任务查询遇到 gzip 响应时的后端异常：上游请求不再转发 `Accept-Encoding`，响应检查前会解压 gzip/deflate，二进制内容不会再触发 `UnicodeDecodeError`。

## 2026-09-03 计费审计

- 已对照 New API 的计费思路检查 NBAPI：上游成功后只使用上游响应中的真实输入/补全 Token 进行结算，并使用整数微美元计算，避免浮点误差。
- Token 模型不再使用请求长度或 `max_tokens` 估算值扣费；如果上游没有返回可拆分的输入和补全用量，则返回 `upstream_usage_unavailable`，本次不执行扣费。
- 已支持 OpenAI-compatible 的 `prompt_tokens/completion_tokens`、Gemini 的 `promptTokenCount/candidatesTokenCount`，以及流式 SSE 中最后带有 usage 的 JSON 数据。
- OpenAI-compatible 缓存输入会从普通输入 Token 中扣除后再按缓存读取价格计费，避免重复收费；缓存相关 Token 和输入/补全 Token 会写入使用日志。
- `/api/billing/call` 已停用。该旧接口允许客户端自行提交 usage，存在伪造低用量的风险；真实计费只允许走带用户 API Key 的 `/v1` 代理接口。
- 当前仍建议上线后用测试账号分别验证：普通对话、流式对话、Gemini、图片/视频按次模型、余额不足、重复 `Idempotency-Key`、上游无 usage 响应和缓存 Token。
- 2026-09-03 后续加固已增加 `billing_reservations`：按次模型和 Token 模型在请求上游前先预留余额/令牌额度；上游失败或 Token 用量不可核验时退款；成功后按真实用量补扣或退回差额，并再写入 `ledger`。重复请求使用同一幂等键时不会重复建立预留或账单。
- Token 预留使用请求体长度和 `max_tokens` 做调用前授权估算，最终账单仍只使用上游真实 usage；若实际用量超过预留，会在同一事务中补扣差额，避免上游已成功但 NBAPI 漏记账。
- 使用日志已补充计费审计字段：预扣金额、实际结算差额、缓存读/写 Token、用量来源（OpenAI-compatible/Gemini/按次）和请求路径；日志详情中可核对预扣与最终实际扣费是否一致。
- 2026-09-03 异步任务计费已补全：按次模型提交返回任务号时写入 `media_tasks`；后续查询接口返回成功会标记完成，返回失败/取消会原子退回该账单金额和令牌额度，并将原使用日志状态改为 `refunded`。退款操作具备状态保护，不会重复退款；日志统计不会把已退款记录计入净花费。

## 2026-09-06 最新状态

- 最新 GitHub 提交：`b183214`，已推送到 `squallwxf/nbapi` 的 `main` 分支。
- 已新增超级管理员专用“供应商对接”页面，可新增、修改、启用、停用供应商渠道，设置渠道名称、上游地址、API Key、优先级和备注。
- 供应商 API Key 只在数据库中使用，页面只显示脱敏提示；普通管理员和普通用户不能读取或修改供应商配置。
- 供应商配置接口为 `GET/POST /api/admin/channels`、`PATCH/DELETE /api/admin/channels/{id}`，统一要求超级管理员权限。
- 模型定价页面已增加模型状态和操作：超级管理员可隐藏、恢复显示或永久删除模型。隐藏模型不会出现在普通用户模型广场、操练场和接口文档，也不能被调用；隐藏模型仍会显示在超级管理员定价页。
- 模型目录接口对普通用户只返回启用模型；超级管理员通过 `includeInactive=1` 查看隐藏模型。模型删除后不会通过前端备用列表恢复。
- 当前模型列表已包含 `gpt-6-astra`，按 OpenAI 兼容接口 `/v1/chat/completions` 接入；其价格暂时沿用 `gpt-5.5`，需要在模型定价页确认后再正式开放。
- Krapi 模型广场确认没有 GROK 模型，相关 GROK 模型应隐藏。Sora 模型虽在上游显示，但调用返回 403 时要核对上游 API Key 的渠道权限、分组和实际接口。

### 最新服务器更新步骤

```bash
cd /opt/nbapi
git pull --ff-only origin main
systemctl daemon-reload
systemctl restart nbapi
systemctl is-active nbapi
```

数据库 `nbapi.sqlite3` 和 `/etc/nbapi.env` 不在 Git 更新范围内，不能用仓库文件覆盖线上数据和密钥。

## 2026-09-07 失败退款与幂等加固

- 已检查所有模型代理调用的失败退款路径：上游返回非 2xx、Token 模型上游未返回可核验 usage、异步图片/视频任务失败或取消、预扣长期未结算，都会把已预扣金额退回用户余额并回退令牌已用额度。
- 普通上游失败和 usage 不可核验退款现在会写入 `balance_transactions`，并写入一条 `ledger.status='refunded'` 的使用日志，方便超级管理员和用户后续对账。
- 失败退款响应会附带 `X-NBAPI-Refunded`、`X-NBAPI-Refunded-Amount`、`X-NBAPI-Balance`；操练场收到这些信息后会提示“预扣费用已自动退回”。
- 已修复一个关键幂等风险：相同 `Idempotency-Key` 已经存在预扣或账单时，NBAPI 现在直接返回 `409 duplicate_idempotency_key`，不再继续请求上游，避免“上游重复扣费但 NBAPI 不重复扣费”的亏损风险。
- 控制台首页的今日请求和本月消耗现在只统计 `ledger.status='charged'` 的成功扣费记录，已退款失败记录不会计入净消耗。
- 本次未修改模型参数、供应商渠道、模型价格或令牌生成逻辑。

## 2026-09-07 接口文档完善与调用验证

- 控制台“接口文档”已统一为真实推荐鉴权方式：优先使用 `X-NBAPI-Key: nb_sk_xxx`，同时说明仍兼容 `Authorization: Bearer nb_sk_xxx`。
- 文档示例已补充每次新调用必须使用唯一 `Idempotency-Key`，并说明重复幂等键会返回 `409 duplicate_idempotency_key`。
- 图片和视频文档已明确任务查询也需要携带 NBAPI 令牌，并补充异步失败退款响应头说明。
- 已新增 OpenAI SDK / Codex 可用的接入示例：`baseURL=https://nbapi.win/v1`，API Key 使用用户在令牌管理中创建的 `nb_sk_...`。
- 已用临时本地数据库验证：页面可打开、测试用户可注册登录、可创建 API Key，`X-NBAPI-Key` 和 `Authorization: Bearer nb_sk_...` 两种方式都能通过鉴权进入 `/v1/chat/completions` 代理层；临时环境未配置上游 Key 时按预期返回 `upstream_api_key_not_configured`。

## 2026-09-07 Codex++ 站外接入 413 修复

- Codex++ 调用 `https://nbapi.win/v1/responses` 时出现 `413 Payload Too Large`，原因是站外工具会发送较长上下文，请求体被 Nginx 默认大小限制拦截。
- 已将 `nbapi.nginx` 增加 `client_max_body_size 50m;`，并将后端 `MAX_REQUEST_BODY` 改为可通过 `NBAPI_MAX_REQUEST_BODY` 环境变量配置，默认 50MB。
- 服务器更新代码后，还需要把仓库里的 `nbapi.nginx` 同步到 `/etc/nginx/sites-available/nbapi`，执行 `nginx -t`，再 reload Nginx；只重启 `nbapi` 服务不能修复 Nginx 层 413。
- 如果后续 Codex++ 上下文特别大仍出现 413，可继续把 `client_max_body_size` 和 `NBAPI_MAX_REQUEST_BODY` 提高到 100MB。

## 2026-09-09 Gemini 3.1 Pro 计费修复

- 已对照 New API 的 Gemini `usageMetadata` 口径修复 `gemini-3.1-pro-preview` 的真实 Token 结算：输入按 `promptTokenCount + toolUsePromptTokenCount`，补全按 `candidatesTokenCount + thoughtsTokenCount`。
- `cachedContentTokenCount` 已从普通输入 Token 中剔除，并只按模型的缓存读取价格结算，避免 Codex++ 长上下文命中缓存时被普通输入价和缓存价重复扣费。
- 使用日志仍保留上游完整输入、补全、缓存读取 Token，便于将 NBAPI 日志与 KRAPI 的上游账单逐条核对。

## 2026-09-09 Claude 流式 Token 用量对账修复

- 已确认 `claude-fable-5` 的差异根因：Claude SSE 会在 `message_start` 返回输入 Token 和占位的 `output_tokens=0`，在最终 `message_delta` 才返回真实输出 Token。旧代理只抽取一段 usage，导致可把有实际输出的调用记成输出 0。
- `server.py` 现在合并整段 SSE 的 usage：保留开始事件的输入/缓存字段，并采用结束事件的非零输出字段后再结算。例如上游的输入 6、补全 626 将按 6/626 落入 NBAPI 使用日志和余额账单。
- 已兼容 OpenAI Responses API 的嵌套 `response.usage`；使用日志会明确标识 `anthropic`、`gemini`、`openai_responses` 或 `openai_compatible` 用量来源。
- 当响应已经含有文本、推理或工具调用等生成内容，但上游仍未给出可信的正数补全 Token，NBAPI 不再按补全 0 少扣：会触发既有 `upstream_usage_unavailable` 自动退款路径并留下退款日志，等待上游返回可审计 usage 后再允许结算。
- 新增 `tools/test_usage_parsing.py`，覆盖 Claude SSE 合并、输出 0 防低扣、OpenAI Responses、Gemini 思考 Token 与 Claude/OpenAI 缓存计费。执行：`python -m unittest tools.test_usage_parsing -v`。

## 2026-09-09 供应商管理运营化

- 超级管理员的“供应商对接”现在可为每个渠道维护支持模型列表；每行一个模型名，留空表示该渠道支持所有模型。
- 模型调用只会路由到“已启用、未熔断且声明支持该模型”的渠道，再按优先级尝试；没有合格渠道会返回 `no_eligible_upstream_channel`，不会绕过模型白名单盲目发往其他上游。
- 每个渠道新增“测试渠道”操作：只请求上游 `/v1/models` 验证地址与上游 Key，不会创建用户调用、预扣余额或产生模型费用；结果会更新健康状态、最后错误和成功时间。
- 当前仍使用被动熔断：连续 3 次网络错误、超时或上游 5xx 后暂停该渠道 5 分钟。后续如接入不同协议或没有 `/v1/models` 的供应商，需要为该供应商增加专用健康检测路径。

## 2026-09-09 当前接力状态

### 2026-09-09 Claude 操练场 502 修复

- 已确认操练场之前把 Claude 模型错误发送到 `/v1/chat/completions`，导致上游返回 502；Claude 必须使用原生 `/v1/messages` 和 `messages/max_tokens` 请求结构。
- `api-website.html` 现在会按 Anthropic 模型走 `/v1/messages`，并读取返回的 `content[].text`。
- `server.py` 现在对 `/v1/messages` 补充 `x-api-key` 和默认 `anthropic-version: 2023-06-01`，同时不再向上游转发下游用户的 `X-NBAPI-Key` 和 `Idempotency-Key`。
- 已通过 `python3 -m unittest tools.test_usage_parsing -v` 和前端 JavaScript 语法检查；代码已进入 GitHub `main`，服务器部署后即可生效。

### 已完成的用户与权限功能

- 超级管理员可在“用户管理”中将普通用户升级为管理员，也可将普通管理员降为普通用户；后端接口严格要求超级管理员，超级管理员账号自身不可降级。管理员降级时会自动解除其名下客户归属。

- 普通用户和普通管理员的使用日志严格限定为当前账号；超级管理员可在“使用日志”中选择“我的日志”或“所有用户”。后端通过 `scope=self/all` 校验权限，普通账号即使手动传入 `scope=all` 也只能查询自己的记录。
- 已修复切换账号后的日志显示问题：切换或退出账号会清空旧日志、统计卡、筛选条件并重置到第一页；延迟返回的旧账号请求不会覆盖新账号页面。
- 令牌功能本轮未修改数据库结构、令牌生成、停用或删除逻辑。曾出现 `/api/tokens` 的 502，是日志范围字段误引用 `log_scope` 导致的服务端变量错误；该错误只影响令牌列表读取，不会删除令牌数据，修复后令牌会按所属 `user_id` 正常显示。
- 钱包数据同样按当前账号会话和 `user_id` 隔离，切换账号时旧账号的充值记录、消费统计和模型图表会清空，旧请求不能覆盖新账号数据。
- 注册页已经移除会暴露后台账户、余额和内部运营规则的说明卡；“指定管理员”功能仍保留。

### 已完成的计费审计与修复

- 所有按 Token 模型最终都只按上游真实 usage 结算，不使用请求字符数或 `max_tokens` 作为最终扣费。价格采用每 1M Token 的整数微美元计算。
- 已修复 Claude 原生 usage 的关键问题：`input_tokens` 不包含 `cache_read_input_tokens`，不能再次从输入中扣除。现在 Claude 按普通输入、缓存读取、缓存写入和补全分别乘以对应价格。
- OpenAI-compatible 和 Gemini 的总输入包含缓存 Token，仍按其协议先扣除缓存部分，再分别使用普通输入价和缓存读取价，避免重复收费。
- 已覆盖 Claude、OpenAI-compatible、Gemini 缓存与非缓存的本地计费测试；所有 Token 模型的输入价、补全价完整性检查通过。
- 已增加价格缺失回填：数据库中新增模型或价格为 0 时，服务启动时仅补齐缺失价格，不覆盖超级管理员已经设置的价格。`gpt-6-astra` 的旧数据库零价格问题已纳入回填。
- 失败退款、预扣、真实 usage 结算、幂等键和异步图片/视频失败退款逻辑仍保持启用；退款记录会写入余额流水和 `ledger.status='refunded'`，不计入净消费。

### 钱包与 ZPAY 当前状态

- “充值订阅”已更名为“钱包管理”。充值档位固定为 `10/20/50/100` 元人民币，后端也强制拒绝其他金额。兑换规则为 `1 元人民币 = 1 个账户余额单位`。充值订单显示人民币金额，模型余额和消费金额仍沿用美元显示格式。
- 钱包页面显示当前账号最近 50 条充值订单和支付状态；待支付 ZPAY 订单可以点击“查询支付结果”，由服务器向 ZPAY 查单，支付成功后自动入账。
- 消费统计支持“今日 / 本周 / 本月”，服务器按北京时间计算自然日、周一到周日自然周和自然月；统计只计算当前用户 `ledger.status='charged'` 的真实消费。
- 钱包消费统计已增加按模型横向条形图，显示当前用户在所选周期内每个模型的消费金额和调用次数。
- ZPAY 已实现支付宝标准页面支付、MD5 签名校验、金额核对、支付方式核对、异步回调幂等和服务端查单。商户 PID、KEY、回调地址必须只配置在服务器 `/etc/nbapi.env`，不能提交仓库。
- ZPAY 已完成 3 次真实支付宝支付联调并确认正常：订单创建、支付跳转、异步回调、查单入账、余额变化和重复通知幂等均已验证。当前无需重复支付测试，后续重点转向运营安全和异常场景。

### 当前最新代码与部署

- 当前接力文档对应的最新代码包含上述全部修复；仓库 `main` 最新提交为 `302f1f9`，包含 Claude 原生消息修复、超级管理员角色调整和公告管理。Token 扣费已完成真实对账验证，支付已完成 3 次真实支付宝测试。
- GitHub 仓库：`https://github.com/squallwxf/nbapi.git`。本地项目目录：`D:\ai web`。服务器目录：`/opt/nbapi`。
- 直接从本地上传服务器时，至少同步 `server.py`、`api-website.html` 和 `HANDOFF.md`。数据库 `nbapi.sqlite3`、服务器环境文件 `/etc/nbapi.env` 和证书目录不能覆盖或提交。
- 后端代码更新后在服务器执行 `python3 -m py_compile /opt/nbapi/server.py`、`systemctl restart nbapi`、`systemctl is-active nbapi`。只改页面时无需重启，使用 `Ctrl+F5` 刷新。

### 下一步建议

1. 完成一次生产环境部署后的健康检查，确认服务器运行的是仓库 `main` 最新版本，并备份线上数据库。
2. 继续做运营前安全检查：余额不足、重复幂等键、上游失败自动退款、异步图片/视频失败退款、令牌额度和隐藏模型调用限制。
3. 检查超级管理员公告、角色调整、供应商管理、模型定价和客户归属在不同角色下的可见性与权限边界。
4. 基础运营稳定后，再规划退款、套餐、订阅有效期、充值对账和运营报表等扩展功能。

## 2026-09-09 AI Neural Grid 视觉改版

- 第一阶段已完成控制台首页、操练场和模型广场的双主题视觉升级：浅色模式保持清爽可读，深色模式增强 AI 科技感；两种主题共用状态色和布局语义。
- 首页新增纯品牌用途的 AI 核心节点视觉和轻量网格背景，保留 NB 字标；网络图不代表真实渠道健康状态，不会误导运营判断。
- 统计、公告、操练场参数/对话区、模型广场筛选和模型卡片统一了边框、层级、状态点和交互悬停效果。
- 动效仅包含轻量节点呼吸、悬停和过渡，并支持 `prefers-reduced-motion`；未修改后端接口、数据库、计费、支付、权限、令牌或任何业务事件逻辑。
- 本次仅修改 `api-website.html`，服务器部署后刷新页面即可；当前代码已推送到 GitHub `main`。

## 2026-09-10 最新接力状态

- 已移除控制台首页右侧的“快捷信息”展示卡片；该区域不包含业务操作、接口请求或事件监听。
- 为避免移除右栏后留下空白，`.console-shell` 已改为单列布局；控制台数据、菜单入口、权限判断和业务逻辑均未修改。
- 最新 GitHub 提交为 `7b60c40 移除控制台快捷信息面板`，已推送到 `https://github.com/squallwxf/nbapi.git` 的 `main` 分支。
- 本地未跟踪的 `api-website.html.before-ai-redesign.bak` 是视觉改版备份，`zhengshu/` 是证书目录；两者均未上传，也不要加入 Git。

### 明天换电脑继续

1. 克隆仓库或进入已有项目目录。
2. 阅读 `README.md` 和本文件，确认线上 `/etc/nbapi.env` 与数据库不从仓库覆盖。
3. 如需更新服务器，在服务器 `/opt/nbapi` 执行 `git pull --ff-only origin main`。
4. 本次仅改前端页面，拉取后浏览器执行 `Ctrl+F5`；若后续修改 `server.py`，再执行 `systemctl restart nbapi` 并检查服务状态。
5. 下一步优先做生产环境回归：登录/注册、密码找回、令牌、操练场文本/图片/视频、计费日志、钱包支付、供应商和超级管理员权限。

## 2026-09-11 使用日志字段优化

### 首 Token 计时后续修复

### 线上首 Token 接近总耗时：仍待定位

- 用户在 f0ab685 后仍观察到多个模型首 Token 接近总耗时。不能凭截图认定是上游缓冲或已彻底修复。
- 新增真实本地 HTTP 分段响应测试：上游在 NBAPI 检测到输出增量后才发结束事件，验证当前读取路径能在响应结束前计时；14 项测试通过。这不是 KRAPI 线上验证。
- 新增 NBAPI_STREAM_TIMING 服务日志，包含 requestId、channelId、响应头/首行/首个 data/首个生成增量/结束时间及最多 12 个事件分类。不记录 Key、提示词或响应正文；计费规则不变。
- 部署后正常发起一次流式调用，执行 `journalctl -u nbapi -n 200 --no-pager | grep NBAPI_STREAM_TIMING`，据此区分上游数据到达较晚和增量漏识别。
- 用户要求对照 QuantumNous/new-api 的计时实现。本轮 GitHub 克隆和 raw 源码直链均连接重置，系统代理 127.0.0.1:7897 不可连接；尚未成功读取参考源码，待网络恢复继续，不能宣称已对照完成。

- 修复 Responses 协议字符串 delta 被漏判、最终 response.completed 快照被误判为首 Token 的问题。使用独立的流式增量判断，覆盖文本、推理、工具参数、Claude 和 Gemini 输出，排除结束快照、空增量和角色事件。
- 首 Token 指从代理开始处理到 NBAPI 收到上游首段生成内容的时间；现有代理仍完整读取并结算后返回客户端，不代表客户端首字可见时间。上游自身缓冲时，接收时间仍可能接近总耗时。
- 只有最终快照、非流式和未支持的压缩流无法可靠测量时显示 `-`。已写入的历史错误计时无法从账单恢复真实值，本次不修改历史数据。
- 已通过 13 项回归测试及差异检查；更新 `server.py` 后需重启 nbapi，新请求开始采用修复后的计时。

- 使用日志已移除“分组”筛选项和表格列；令牌管理中的令牌分组功能保留不变。
- “用时”现在以秒显示，保留 3 位小数。
- 新增“首 Token（秒）”列。后端对流式 SSE 响应在第一个真实生成内容事件到达时记录首 Token 用时；非流式调用、历史记录或无法识别首内容的响应显示 `-`，不会用估算值伪造。
- `ledger.first_token_ms` 会在服务启动时自动迁移；旧数据库和旧日志数据不会丢失。
- 本次修改涉及 `server.py`、`api-website.html` 和 `tools/test_usage_parsing.py`，未修改计费金额、余额扣除、令牌、权限或上游调用协议。
- 已通过 Python 语法检查、JavaScript 语法检查、`git diff --check` 和 10 项用量解析回归测试。
