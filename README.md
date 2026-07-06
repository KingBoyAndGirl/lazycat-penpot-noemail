# Penpot for LazyCat (No-Email Edition)

Penpot 开源设计协作平台的 LazyCat LPK 包。

## 特性

- ✅ **无邮箱** — 不需要 SMTP、不需要邮件捕获器
- ✅ **PREPL 管理员创建** — 通过 PREPL 协议自动创建 `admin / admin123`
- ✅ **enable-mcp** — MCP flag 已开启
- ✅ **多实例支持** — 使用 `${LAZYCAT_APP_ORIGIN}` 动态域名

## 架构

```
入口 80/tcp → penpot-frontend (NGINX)
                ├── penpot-backend (6060 + PREPL 6063)
                │     ├── penpot-postgres (5432)
                │     └── penpot-redis (6379)
                ├── penpot-exporter (6061)
                └── penpot-init (一次性，创建管理员后退出)
```

## 开发

```bash
# 构建 LPK
lzc-cli project release -o lpk/io.zeroc.app.penpot-v$(date +%Y.%m.%d).lpk

# 本地测试 (需要 LazyCat 开发环境)
lzc-cli project dev
```

## 自动升级

- `.github/workflows/check-penpot-upgrade.yml` — 每天检查上游 Penpot 新版本
- `.github/workflows/release-lpk.yml` — main push 时自动构建并发布 LPK

## 上游

- Penpot: https://github.com/penpot/penpot
- 懒猫 Registry 镜像由 `zeroc` 维护
