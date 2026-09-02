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
- 上游 API Key 和服务器密码不要写入代码或提交到 GitHub。

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

## 重要提醒

- `nbapi.sqlite3` 不要提交到 GitHub
- 用户余额、API Key、扣费记录都在数据库里
- 本地备份命令：`python tools/backup_db.py`
- 数据库路径可通过 `NBAPI_DB_PATH` 改
- 备份目录可通过 `NBAPI_BACKUP_DIR` 改
- 服务器改动后要记得同步到仓库
