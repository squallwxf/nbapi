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

## 默认账号

- 超级管理员：`squallwxf` / `Aa19860120`
- 管理员：`admin` / `admin123`
- 普通用户：`demo` / `demo123`

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
