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

## 重要提醒

- `nbapi.sqlite3` 不要提交到 GitHub
- 用户余额、API Key、扣费记录都在数据库里
- 本地备份命令：`python tools/backup_db.py`
- 数据库路径可通过 `NBAPI_DB_PATH` 改
- 备份目录可通过 `NBAPI_BACKUP_DIR` 改
- 服务器改动后要记得同步到仓库
