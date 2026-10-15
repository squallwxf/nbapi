# NBAPI 项目备忘录

更新：2026-10-15。这是随Git同步的项目约定，不是全局Codex记忆或完整聊天记录。当前状态见HANDOFF。

## 关键约定

- 本机真实源码 `C:\Users\Administrator\Documents\ChatGPT\NBAPI`，不是聊天登记的nbapi 2目录。
- 生产 `154.36.173.186:/opt/nbapi`，网站https://nbapi.win ，nbapi/nginx服务；旧195.72.185.130不可部署。
- 功能稳定、准确计费、用户隔离优先。视觉修改不顺带动代理、支付、权限；保留DOM ID、API路径和字段。
- 充值1元=1余额，当前人民币显示不换算；账务整数micros，不随意用浮点改金额。
- 用户已确认token计费校准及支付多次成功，新增修复仍需回归，但不重开旧问题。
- gpt-6别名固定指向gpt-6-sol，不改成6.1；模型名、协议、供应商和价格分别配置。
- 显式Chat Gemini保留媒体/max_tokens，不按品牌强制native；无可信usage不估算扣费，客户端断开仍完成上游读取和结算。
- 钱包/日志/令牌默认本人，超级管理员全体视图需明确权限；普通维护不重建用户及token。
- 下载管理仅超级管理员，公开只允许已发布文件；8MiB分片、1GiB上限及SHA-256保护不降低。二维码本地生成同源URL，IPA签名分发另行解决。
- 联系页只有QQ和邮箱，不重新引入用户已删除的微信二维码管理。

## 代码入口

| 文件 | 职责 |
| --- | --- |
| api-website.html | 结构、ID、导航及资源版本 |
| assets/nbapi.css | 双主题、响应式布局 |
| assets/nbapi.js | 浏览器主状态、请求、渲染与事件 |
| assets/contact.js | 仓库版联系复制事件 |
| assets/software.js / qrcode.js | 下载管理和MIT二维码库 |
| software_downloads.py | 分片、发布、截图及下载权限 |
| server.py | API、认证、迁移、代理、计费、ZPAY、SMTP及静态白名单 |
| tools/test_usage_parsing.py | 计费/协议/流式/支付/权限/余额回归 |
| tools/test_software_downloads.py | 下载HTTP与隔离DB测试 |
| tools/test_software_qr.cjs | 模拟浏览器二维码解码和桌面/手机布局 |
| tools/backup_db.py | SQLite一致性备份 |

## 跨会话维护

先fetch查看差异，多个会话共享工作区，不假设未提交改动都是自己的；不回滚别人修改。结束记录原因、文件、测试、限制、提交/推送/部署状态及备份位置。

Git不带DB、供应商配置、环境、SSH密钥、证书或安装包，不记录密码。不要git add .误收压缩包；`nbapi-model-discovery-hotfix.tar.gz`未审查留本地。

生产有未提交代码，不能只看HEAD或直接整包覆盖；禁止reset --hard、重建DB和本地测试DB覆盖线上。仓库与生产静态组织差异见HANDOFF。

网络401只证明到达鉴权，不证明模型成功；上游文字生图成功不证明编辑/网关账务成功。模拟回归、只读诊断和真实收费验收要分别记录。

精准搜索及局部读取，避免整份大源码/日志重复进入超长对话。完成阶段后更新HANDOFF和本文，让新会话从文档继续。
