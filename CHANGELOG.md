# Changelog

## 2026.07.19

### 上游同步
- 已同步 Penpot 上游版本至 `2.16.2`。
- `penpot-frontend`、`penpot-backend`、`penpot-exporter` 继续使用对应 ACR 运行时镜像，不使用 Docker Hub 运行时镜像。

## 2026.07.08

### 打包清理
- 清理未生效的 `mcp-custom.conf` bind 与写死域名的 `penpot-design` resource skill，MCP 改为依赖 Penpot frontend 镜像内置 `/mcp/stream` 路由。

### 导出/缩略图修复
- 通过 `compose_override` 让 backend wrapper 先以 root 启动，修复 `/opt/data/assets` bind 目录为 `1001:1001` 后再降权到 `penpot`；修复 `AccessDeniedException: /opt/data/assets/...` 导致的缩略图/导出失败。

### Mailcatch 子路径修复
- 新增面向 Penpot 邀请/验证流程的友好收件箱，默认展示收件邮箱、主题、打开/复制邀请链接，并保留 `/mailcatch/raw/` 原始 MailCatcher 调试入口。
- MailCatcher 启动参数增加 `--http-path /mailcatch`，让页面输出 `/mailcatch/assets/...`，避免浏览器继续请求 Penpot 根路径 `/assets/...`。
- 为 `penpot-frontend` 增加启动 wrapper，在容器启动时写入 `mailcatch-locations.conf`，将 `/mailcatch` 与 `/mailcatch/*` 代理并重写到 MailCatcher 根路径；避免 LazyCat 路由不能剥离子路径和 compose_override 文件挂载变目录的问题。

- 改为单实例部署，保留官方 Penpot 登录页。
- 固定管理员账号 `admin@qq.com / admin123`。
- 移除免密登录 inject 与 deploy params 残留。
- 新增 backend 内部启动包装脚本，在 `penpot-backend` 容器内等待 PREPL 并自动创建管理员账号，避免依赖 app 容器内的 `docker` / `python3` / `nc`。
- `PENPOT_PUBLIC_URI` 改为基于 `${LAZYCAT_APP_DOMAIN}`，适配 NASW / Canway / 新机器域名。
- 恢复官方开发模式的假邮件系统 `penpot-mailcatch`：backend SMTP 指向本地 mailcatcher，用户可在 `/mailcatch` 查看验证邮件并点击注册链接。

## v2026.07.06

### 变更
- 初始版本：基于 Penpot 2.16.2
- 移除 penpot-mailcatch 邮件捕获器
- 移除 SMTP 环境变量和 enable-smtp flag
- 添加 penpot-init 容器通过 PREPL 自动创建管理员 (admin / admin123)
- 添加 enable-mcp flag

---
