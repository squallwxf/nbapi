# NBAPI

NBAPI 是一个 API 聚合网关项目，包含前端页面、后端服务、模型广场、令牌管理和计费逻辑。

## 本地项目

- 代码目录：`D:\ai web`
- 前端页面：`api-website.html`
- 后端服务：`server.py`
- Nginx 配置：`nbapi.nginx`
- systemd 服务：`nbapi.service`

## 换电脑继续开发

1. 在新电脑安装 `Git`
2. 执行：

```bash
git clone https://github.com/squallwxf/nbapi.git
```

3. 进入项目目录继续修改
4. 修改完成后再提交并推送到 GitHub

## 服务器上的项目

- 线上服务目录：`/opt/nbapi`
- 线上站点：`https://nbapi.win`
- 后端服务名：`nbapi`

## 更新方式

- 只改前端：更新 `api-website.html`，再上传到服务器
- 改后端：更新 `server.py`，上传后重启服务
- 改域名反代：更新 `nbapi.nginx`，重新加载 Nginx

## 重要说明

- `nbapi.sqlite3` 不要上传到 GitHub
- 这个数据库包含用户、令牌、余额和扣费记录
- 如需迁移或备份，应该从服务器单独导出

