# NBAPI 接力文档

当前项目仓库：`https://github.com/squallwxf/nbapi.git`

## 现在的状态

- 前端页面：`api-website.html`
- 后端服务：`server.py`
- 服务器域名：`nbapi.win`
- 对外调用地址：`https://nbapi.win/v1`
- 服务器项目目录：`/opt/nbapi`
- 本地项目目录：`D:\ai web`

## 下次换电脑怎么继续

1. 克隆仓库
2. 打开项目目录
3. 先看 `README.md`
4. 再看这份 `HANDOFF.md`
5. 需要修改页面就改 `api-website.html`
6. 需要改接口和计费就改 `server.py`

## 本地代码上传服务器

推荐流程是“本地修改 -> GitHub -> 服务器拉取”，不需要每次手动上传文件：

### 本地电脑

在 PowerShell 中执行：

```powershell
cd "D:\\ai web"
git add .
git commit -m "更新网站"
git push
```

### 服务器

SSH 登录服务器后，逐条执行：

```bash
cd /opt/nbapi
git pull
```

如果修改了 `server.py`：

```bash
systemctl restart nbapi
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
- 操练场调用完成后会读取服务器 `/api/me` 刷新余额，并读取 `X-NBAPI-Charged`/`X-NBAPI-Balance` 显示本次实际扣费和最新余额。
- 使用日志已改为真实账单页：按时间、令牌、模型、分组、Request ID、计费类型筛选，显示令牌归属、IP、耗时、输入/输出 Token、花费，并支持统计、详情展开、分页和每页数量。
- `ledger` 会自动增加 `client_ip`、`latency_ms`、`request_path`、`request_id` 字段；旧线上数据库启动时会自动迁移，旧记录的新增字段为空是正常现象。
- 生产环境建议设置 `NBAPI_SUPER_ADMIN_PASSWORD`（仅首次初始化新数据库时使用）和 `NBAPI_ALLOWED_ORIGINS`；已有超级管理员密码不会在每次启动时被重置。
- `GET /health` 可用于 Nginx、systemd 或监控探针；登录用户可通过 `POST /api/auth/password` 修改自己的密码，新密码至少 12 位。
- 登录和注册接口按客户端 IP 做基础限流（每分钟最多 10 次），跨域响应只允许 `NBAPI_ALLOWED_ORIGINS` 中的来源。
- `GET /api/dashboard` 返回实时模型数、启用渠道数，以及当前登录用户的今日调用、本月消耗、平均延迟和余额；首页统计不再使用硬编码演示数字。
- 上游调用会按渠道优先级依次尝试最多 `NBAPI_UPSTREAM_MAX_ATTEMPTS` 个渠道（默认 2）；网络错误、超时和 5xx 会记录失败并自动尝试下一渠道，3 次连续失败的渠道会熔断 5 分钟后再试。可通过 `NBAPI_UPSTREAM_TIMEOUT` 调整单次上游超时（默认 90 秒）。渠道管理页会显示真实健康状态和最近错误。
- 充值订阅已提供人工审核 MVP：用户可在“充值订阅”提交充值申请，`GET /api/wallet` 查看订单和余额；管理员通过 `GET /api/admin/wallet/orders` 查看申请，并对订单调用 `POST /api/admin/wallet/orders/{id}`（`{"action":"approve"}` 或 `{"action":"reject"}`）处理。审核通过会增加余额并写入 `balance_transactions`，暂未接入自动支付。
- 模型价格已统一为客户价格：按 Token 的模型以每 1M Tokens 计费并区分输入、输出和缓存读写价格；按次模型以每次计费。价格初始化为参考截图价格的 2 倍，并通过 `pricing_schema_version` 防止每次启动覆盖超级管理员修改。
- 模型价格修改权限仅限超级管理员；后端 `/api/admin/models/{name}` 会拒绝普通管理员，模型广场只为超级管理员显示编辑控件。
- `D:\ai web\nbapi模型价格模板.xlsx` 是模型定价模板；本次已按用户修改后的有效价格更新后端，并将 `pricing_schema_version` 升级为 `4`，线上执行一次启动迁移后会持久化这些价格。
- 权限规则：管理员仅可查看用户列表和创建普通用户；超级管理员继承上述权限，并可设置用户余额、通过控制台的“模型定价”页面修改模型价格。模型广场仅用于查看模型与价格，不再提供改价入口。
- 2026-09-03 权限调整已写入代码：管理员创建的账号固定为普通用户且初始余额为 0；管理员不能修改已有用户。超级管理员只可设置用户余额。渠道管理、上游配置和充值审核接口已关闭；超级管理员的模型定价独立位于控制台“模型定价”页面。

## 重要提醒

- `nbapi.sqlite3` 不要提交到 GitHub
- 用户余额、API Key、扣费记录都在数据库里
- 本地备份命令：`python tools/backup_db.py`
- 数据库路径可通过 `NBAPI_DB_PATH` 改
- 备份目录可通过 `NBAPI_BACKUP_DIR` 改
- 服务器改动后要记得同步到仓库

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
