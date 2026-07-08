# Penpot for LazyCat

Penpot 开源设计协作平台的 LazyCat LPK 包。

## 当前特性

- 官方 Penpot 登录/注册页，不做免密登录改造。
- 单实例部署。
- 首次安装自动初始化管理员：`admin@qq.com / admin123`。
- 本地 MailCatcher 假邮件系统：注册验证、团队邀请邮件不走外网 SMTP。
- 友好邮件收件箱：`/mailcatch/`，并保留原始调试入口 `/mailcatch/raw/`。
- Penpot MCP：`/mcp/stream`。
- 支持 `.penpot` 文件下载与画板 PDF 导出。

## 架构

```text
入口 → penpot-frontend:8080
       ├── penpot-backend:6060 / PREPL 6063
       │   ├── penpot-postgres:5432
       │   ├── penpot-redis:6379
       │   └── penpot-mailcatch:1025
       ├── penpot-exporter:6061
       └── penpot-mcp:4401/4402
```

## 关键路径

- Penpot：`/`
- MailCatcher 友好收件箱：`/mailcatch/`
- 原始 MailCatcher：`/mailcatch/raw/`
- MCP：`/mcp/stream`
- assets 目录：`/lzcapp/var/data` → `/opt/data/assets`

## 构建

```bash
lzc-cli project release -o lpk/io.zeroc.app.penpot-v$(date +%Y.%m.%d).lpk
```

## 上游

- Penpot: https://github.com/penpot/penpot
