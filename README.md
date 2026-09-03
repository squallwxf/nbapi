# NBAPI

NBAPI 是一个面向 AI 模型聚合分发的站点，目标是对齐 `https://ai.krapi.cn` 的控制台、模型广场和接入方式。

## 当前能力

- 登录 / 退出
- 三层用户等级：超级管理员、管理员、用户
- 令牌创建、禁用、列表、复制完整 API Key
- 模型广场筛选、搜索、价格切换
- 控制台总览、用户管理、渠道管理、日志、系统设置
- 管理员上游 API Key 配置
- 用户管理：管理员可调整用户剩余额度、提升普通用户为管理员；超级管理员还可设置超级管理员角色
- 渠道管理：管理员可新增和编辑渠道名称、上游地址、上游 API Key、优先级、启停状态和备注
- 人工充值订单：用户可提交充值申请，仅超级管理员可审核；订单入账具备事务和幂等保护，ZPAY 自动支付待接入

## 接力文档

- [项目接力说明](./项目接力说明.md)
- [项目接力补充 2026-09-02](./项目接力补充-2026-09-02.md)
- [模型调用文档](./api调用文档(3)(19)(2)(4)(1).md)

## 本地开发

- 当前工作副本目录：`D:\ai web`
- 对外调用地址：`https://nbapi.win/v1`
- 启动后端：`python server.py`
- 启动静态页：`python -m http.server 8000 --bind 127.0.0.1`
- 打开：`http://127.0.0.1:8000/api-website.html`

## ZPAY 配置

ZPAY 参数只放在服务器环境变量中，不要写入代码或 GitHub：

- `NBAPI_ZPAY_PID`：ZPAY 商户 ID
- `NBAPI_ZPAY_KEY`：ZPAY 商户密钥
- `NBAPI_ZPAY_SUBMIT_URL`：默认 `https://zpayz.cn/submit.php`
- `NBAPI_ZPAY_NOTIFY_URL`：默认 `https://nbapi.win/api/payment/zpay/notify`
- `NBAPI_ZPAY_RETURN_URL`：默认 `https://nbapi.win/#wallet`
- `NBAPI_ZPAY_CID`：可选渠道 ID，留空由 ZPAY 自动选择
- 当前充值页面仅启用支付宝；如需启用微信，需要先确认 ZPAY 商户已开通微信渠道，再单独调整代码和配置。
- `NBAPI_ZPAY_MIN_TOPUP`：最低充值金额，默认 `1`

未配置 `NBAPI_ZPAY_PID` 或 `NBAPI_ZPAY_KEY` 时，充值接口会拒绝创建订单，不会产生无法核对的待支付订单。

## 初始管理员

首次初始化数据库时请通过环境变量设置 `NBAPI_SUPER_ADMIN_PASSWORD`，不要使用仓库或网页中公开的默认密码。线上部署后应立即修改初始密码并删除不需要的演示账号。

## 数据位置

- `nbapi.sqlite3`：用户、令牌、余额、计费、模型价格、上游配置、渠道配置
- `nbapi.sqlite3-wal` / `nbapi.sqlite3-shm`：运行时文件，不要提交

## 更新方式

- 只改前端：更新 `api-website.html`，再上传到服务器
- 改后端：更新 `server.py`，上传后重启服务
- 改域名反代：更新 `nbapi.nginx`，重新加载 Nginx
- 本地备份数据库：运行 `python tools/backup_db.py`
- 需要移动数据库时，可设置 `NBAPI_DB_PATH`
- 需要改备份目录时，可设置 `NBAPI_BACKUP_DIR`

## 服务器信息

- 线上服务目录：`/opt/nbapi`
- 线上站点：`https://nbapi.win`
- 后端服务名：`nbapi`

## 重要说明

- `nbapi.sqlite3` 不要上传到 GitHub
- 这个数据库包含用户、令牌、余额、扣费记录和渠道密钥
- 备份文件会放在 `backups/`
- 如需迁移或备份，应该从服务器单独导出
