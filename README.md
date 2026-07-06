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

## 自动升级（Hermes Studio Cron Job）

本项目不使用 GitHub Actions，而是通过 **Hermes Studio Cron Job** 实现自动升级检查。

### 设置 Job

在 Hermes Studio Web UI → 定时任务 → 新建：

- **名称**: Check Penpot Upgrade
- **调度**: `0 10 * * *`（每天 10:00）
- **工作目录**: `/home/agent/.hermes/workspace/lazycat-penpot-noemail`
- **运行脚本**:
  ```bash
  python3 scripts/check-upstream-version.py
  ```
- **环境变量**:
  - `GITHUB_TOKEN`: GitHub Personal Access Token（用于创建 PR）

### Job 行为

1. 检查 Penpot 上游 (`penpot/penpot`) 最新 Release tag
2. 与 `UPSTREAM_VERSION` 对比
3. 发现新版本 → 更新版本号 + CHANGELOG → 通过 GitHub API 创建 PR
4. PR 需要人工检查镜像可用性后合并

## 上游

- Penpot: https://github.com/penpot/penpot
- 懒猫 Registry 镜像由 `zeroc` 维护
