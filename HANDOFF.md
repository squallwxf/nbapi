# NBAPI 项目接力

更新：2026-10-15（北京时间）。先读本文、`MEMORY.md`、`AGENTS.md`，再按任务局部搜索代码。聊天记录不会随 Git 同步，关键结论在本文。

## 当前仓库与服务器

- GitHub：https://github.com/squallwxf/nbapi ，分支 `main`。
- 本机真实源码：`C:\Users\Administrator\Documents\ChatGPT\NBAPI`。聊天登记目录 `C:\Users\Administrator\Documents\ChatGPT\nbapi 2` 不是实际源码目录，勿维护错副本。
- 当前生产：`154.36.173.186:/opt/nbapi`，网站 https://nbapi.win ，`nbapi.service`，Python监听 `127.0.0.1:8765`，Nginx反代。
- 10-15已SSH只读核实 nbapi/nginx 均active，后端 `/health` 返回ok。旧 `195.72.185.130` 已退役，禁止按历史记录部署到旧IP。
- SSH身份root，本机密钥 `%USERPROFILE%\.ssh\nbapi_admin`；服务用户nbapi，环境文件 `/etc/nbapi.env`。密钥不在Git，新电脑须安全配置访问权限。
- 仓库 service/nginx 是模板，不等于完整线上配置，不能直接覆盖。

## 已完成功能

| 功能 | 当前状态与保护点 |
| --- | --- |
| 用户/权限/令牌 | 注册登录、邮箱找回密码、用户数据隔离；超级管理员日志支持自己/全部。维护不重建账号令牌。 |
| 钱包/ZPAY | 固定10/20/50/100充值、充值记录、今日/本周/本月消费与模型图表；用户确认支付多次测试成功。1元充值=1余额，目前显示人民币，不做汇率换算。 |
| 计费 | 权威usage、缓存读写、动态阶梯、原子预扣、幂等结算与失败退款。用户确认token扣费已校准，不把旧问题重复当现状。 |
| 模型 | Chat/Responses/Anthropic/Gemini/图像视频，显式协议优先；不得仅凭厂商品牌转换协议。 |
| 流式/用时 | 逐行转发，响应禁用Nginx缓冲；区分首数据、首内容与总时长。客户端断开仍读上游并结算。 |
| 首页/操练场/广场 | 双主题、真实统计、筛选与动态价格详情；保护DOM ID、路由、请求和事件。 |
| 余额API | `GET /v1/account/balance`，API Key身份、CNY六位小数字符串、no-store、10次/60秒；见 `docs/ACCOUNT_BALANCE_API.md`。 |
| 联系我们 | `#contact`，QQ客服群1109594338、邮箱yk@nb-api.cn、复制及邮件入口；无微信二维码或二维码后台编辑。 |
| NB ai工具下载 | `#downloads`，公开已发布目录，仅超级管理员管理；每包1GiB、8MiB顺序分片、SHA-256、Range、多平台安装包及截图。支持Android APK/iOS IPA及扫码下载；IPA仍需签名/分发资格。 |
| NB画布 | 独立工程曾在 `D:\NB助手`，软件下载不等于完整画布在线运行移植，独立工程不会自动随本仓库同步。 |

## 各会话成果与部署记录

- **异步图片任务查错供应商修复（10-15）**：香蕉Pro创建经巧模217成功，后续GET不带模型名，原逻辑按全局渠道查询而404；并非生成失败。media_tasks新增channel_id，提交时记录实际成功供应商，后续按用户+令牌+任务绑定查询，禁止失败后切换其他供应商；旧未绑定记录暂沿用兼容路由，不能猜测供应商批量回填。已根据journal确证将 `Xa-bWvbRm9fbDNJq_Uzu7s2wr-UuaHWh` 对应任务绑定217，网关GET实测200/succeeded、任务completed，余额未变（原已扣0.36元）。日志已存在ledger；后台可用全部用户范围及Request ID查找，不将轮询另计消费。59项回归、Python及四份JS语法、diff检查通过。已仅部署server.py到154.36.173.186并重启，内外health200；备份 `/opt/nbapi-backups/task-routing-20261015/`，未重新生成图片/重复扣费。
- **香蕉供应商配置（10-15）**：`T香蕉2`、`T香蕉pro` 一次性从legacy转换为explicit，后台模型定价可点击配置选择供应商；保留原可用关联并加入已有巧模/qiaomo，管理员后续移除不会被重启重新添加。价格、显隐、协议和endpoint保持不变。58项Python回归、Python编译、四份JS语法检查及diff检查通过；未执行收费生图调用。已向154.36.173.186仅合并该迁移并重启nbapi，本机/公网health均200、nginx检查通过；线上两模型关联1、2、217，217显示qiaomo。源码与SQLite一致性备份在 `/opt/nbapi-backups/banana-config-20261015/`，未覆盖用户数据、密钥或其他线上代码。源码与本文随本次提交同步仓库。
- **主线迁移**：10-12旧服务器迁至154.36.173.186，包含真实源码、DB、环境及软件存储，停止旧写入后最终备份。迁移时users45、tokens16、ledger15407等摘要一致，仅为历史快照。备份 `/root/nbapi-migration-20261012`；本机同级迁移目录含敏感材料，不入Git。
- **新加板块**：联系页10-13只更新生产静态文件，未重启后端；备份 `/opt/nbapi-backups/contact-20261013`。
- **工具下载页面**：移动平台10-13部署，备份 `/opt/nbapi-backups/mobile-20261013`；原未提交代码本次收回。10-15从线上额外收回二维码实现、MIT生成库及浏览器测试，避免换机漏功能。
- **继续主线**：`9e82508` 联系页面和Gemini Chat多模态修复原已提交但未成功推送，本次一并上传；前一提交 `bed7a5e` 是余额API。
- **模型添加**：新模型显隐、价格、供应商关系多为生产DB配置，不是代码部署，见下表。
- **网络排查**：旧机器部分失败来包未见guest网卡，具体外部故障点未最终证实，勿沿用“必需供应商放行旧IP”的旧推断。曾授权开CF Zero Trust免费版并配置恢复Tunnel，不代表当前主域经Tunnel。用户后来改回直连并申请HTTPS证书；当前访问策略须现场核实。

## 模型记录与未完成验收

| 模型 | 配置/风险与验证边界 |
| --- | --- |
| gpt-6-sol / gpt-6 | gpt-6是透明兼容别名，固定指向gpt-6-sol，不改指6.1。客户端可选名称以实际版本为准。 |
| gpt-6.1-sol | 源码一次性隐藏种子复制6-sol价格，保留后续后台改价。生产显隐与路由查DB，种子状态不等于当前线上状态。 |
| grok-4.7 | 巧模217，openai_responses，/v1/responses；记录售价输入0.60/输出1.80每百万。Chat混用零input/output及非零prompt/completion造成解析歧义，暂用Responses；未实测真实网关扣费。 |
| gemini-3.8-flash | 巧模217，openai_chat，/v1/chat/completions；输入1.125/输出5.625每百万，缓存按输入价。不能强制native。 |
| gpt-image-2.5 | 巧模217，openai_images，/v1/images/generations；上游0.12/次，批准2.5倍，售价0.30/次。上游文字生图成功；编辑接口直接测试503 `No available compatible accounts`，截图网关约90秒502且0.30已退回；不能宣称编辑可用。 |

这些是批准/配置时记录，不替代当前后台数据。Gemini修复保留显式Chat媒体与max_tokens，具体供应商音视频语义支持仍未验收。历史两次错误转换媒体的扣费未退款，详情见归档，不擅自改账。gpt-image-2-super早期0.22是暂定价，不当作供应商确认成本。

## 本次源码对比与收回范围

生产Git工作区有大量未提交/未跟踪文件，HEAD不代表实际部署。10-15只读下载比较：核心代理/计费逻辑一致，usage测试仅换行差异，软件后端及测试哈希一致。

- 收回线上二维码CSS/JS、QR库与测试，保留本地 `assets/contact.js`；线上同等复制处理附在主JS，不单独加载contact.js。
- 仓库静态白名单同时允许contact.js及qrcode.js；线上仅后者。HTML脚本组织、缓存版本和CSS注释存在差异，不能只替换其中一个文件。
- 除静态组织、版本及换行外，本次所比较源文件未发现其他核心差异。线上构建输出、备份和业务存储不收进Git。
- 本次仅整理、回收源码、测试与推送，**未部署、未重启、未修改线上账务/配置**。不要把Git已上传等同生产已按新提交发布。

## 换电脑步骤

本地PowerShell：

```powershell
git clone https://github.com/squallwxf/nbapi.git
cd nbapi
git status -sb
git log -3 --oneline
```

已有正确仓库先看 `git status -sb`，干净才 `git pull --ff-only`，有改动先审阅保存，不reset。新会话选真实源码目录，让它读HANDOFF/MEMORY/AGENTS即可接手，不必复制全部旧聊天。

```powershell
python -m py_compile server.py software_downloads.py
python -m unittest tools.test_usage_parsing tools.test_software_downloads -q
node --check assets/nbapi.js
node --check assets/contact.js
node --check assets/software.js
node --check assets/qrcode.js
git diff --check
```

QR测试另需Playwright/jsqr及可用浏览器，设置NODE_PATH后 `node tools/test_software_qr.cjs`；QR_TEST_CHROME可指定浏览器。它用模拟目录、截图写系统临时目录，不消耗线上模型和余额。

本次合并实际验证：57项Python回归通过，Python编译与四份JS语法检查通过；QR浏览器测试通过桌面/390px手机解码、目录/详情显示、草稿不显示二维码、无横向溢出及无页面错误。未执行真实充值或付费模型调用。

## 部署与备份

1. Git只同步源码/文档，不恢复用户、令牌、余额、模型配置、订单或安装包。
2. 另备份SQLite一致性快照（`tools/backup_db.py`或SQLite backup API）、software-storage、环境、证书、Nginx/systemd。WAL活跃时不能仅复制主DB，切流避免双写。
3. 当前生产脏工作区不能盲目git pull或整目录覆盖；先比对文件哈希、合并线上独有改动并备份源码与DB，确认目标IP。
4. 隔离目录/测试DB先验证，再按清单发布。保护 `/etc/nbapi.env`、DB、证书及存储；仅静态修改不必重启后端。
5. 发布后检查服务、`nginx -t`、本机及公网health、页面实际引用资源、受影响权限及账务。真实收费测试须受控账户与授权，逐项对账，模拟测试不能当真实支付验收。

## 下一步

- 上游修复image2.5编辑账户池后，单独做低成本编辑与网关账务验收。
- 建立生产可审阅发布基线，当前未清理生产脏文件/修改生产Git。
- 建立DB和软件存储异机备份、恢复演练；GitHub不是业务数据备份。
- 每会话完成后记录修改文件、测试边界、提交/推送、是否部署、目标服务器、备份及未验收项。

旧完整接力已归档 `docs/HANDOFF_SNAPSHOT_2026-10-15.md`；更早的 `docs/HANDOFF_HISTORY.md`、`项目接力补充-2026-09-02.md` 仅历史参考，冲突以本文和当前证据为准。
