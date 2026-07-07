# Changelog

## 2026.07.08
- 改为单实例部署，保留官方 Penpot 登录页。
- 固定管理员账号 `admin@qq.com / admin123`。
- 移除免密登录 inject 与 deploy params 残留。
- 新增 backend 内部启动包装脚本，在 `penpot-backend` 容器内等待 PREPL 并自动创建管理员账号，避免依赖 app 容器内的 `docker` / `python3` / `nc`。
- `PENPOT_PUBLIC_URI` 改为基于 `${LAZYCAT_APP_DOMAIN}`，适配 NASW / Canway / 新机器域名。

## v2026.07.06

### 变更
- 初始版本：基于 Penpot 2.16.2
- 移除 penpot-mailcatch 邮件捕获器
- 移除 SMTP 环境变量和 enable-smtp flag
- 添加 penpot-init 容器通过 PREPL 自动创建管理员 (admin / admin123)
- 添加 enable-mcp flag
- 镜像来自懒猫 Registry (zeroc/penpotapp + zeroc/zeroc0077)

---
