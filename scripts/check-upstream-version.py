#!/usr/bin/env python3
"""Check upstream Penpot releases and create upgrade PR via GitHub API.

Runs as a Hermes Studio Cron Job (NOT GitHub Actions).
Creates a PR when a new upstream version is detected.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.request
import json
from pathlib import Path
from typing import Optional

# === Configuration ===
UPSTREAM_REPO = "penpot/penpot"
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "KingBoyAndGirl/lazycat-penpot-noemail")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
VERSION_FILE = Path("UPSTREAM_VERSION")
CHANGELOG_PATH = Path("CHANGELOG.md")

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
GITHUB_API = "https://api.github.com"
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")


def log(msg: str) -> None:
    print(f"[penpot-check] {msg}")


def semver_key(tag: str) -> Optional[tuple[int, int, int]]:
    match = SEMVER_RE.match(tag)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def github_api(method: str, path: str, data: dict | None = None) -> dict:
    """Call GitHub REST API."""
    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Penpot-Cron-Job",
    }
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        log(f"GitHub API error: {method} {path} → HTTP {exc.code}")
        if detail:
            log(f"  {detail[:500]}")
        raise


def latest_upstream_tag() -> str:
    """Get the latest semver release tag from Penpot."""
    releases = github_api("GET", f"/repos/{UPSTREAM_REPO}/releases?per_page=5")
    candidates = []
    for release in releases:
        tag = release["tag_name"]
        key = semver_key(tag)
        if key:
            candidates.append((key, tag))
    if not candidates:
        raise RuntimeError(f"未在 {UPSTREAM_REPO} 找到语义化版本 release")
    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]


def current_tracked_version() -> str:
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def create_or_update_pr(upstream_version: str, current_version: str) -> int:
    """Create or update an upgrade PR on GitHub."""
    branch = f"automation/penpot-{upstream_version}"
    title = f"feat: Penpot 上游更新至 {upstream_version}"
    body = (
        f"自动检查发现 Penpot 有新版本。\n\n"
        f"- 上游版本：`{upstream_version}`\n"
        f"- 当前追踪版本：`{current_version}`\n"
        f"- 上游 Release：https://github.com/penpot/penpot/releases/tag/{upstream_version}\n\n"
        f"⚠️ **本 PR 仅更新追踪版本号，不包含镜像变更。**\n\n"
        f"需要人工完成以下步骤：\n"
        f"1. 检查懒猫 Registry 是否有对应的新镜像\n"
        f"2. 更新 `lzc-manifest.yml` 中的镜像 tag\n"
        f"3. 更新 `CHANGELOG.md`\n"
        f"4. 本地测试 LPK\n"
        f"5. 合并 PR → 自动发布新 LPK\n"
    )

    if DRY_RUN:
        log(f"[DRY RUN] 将创建 PR: {title}")
        return 0

    # Git setup
    run(["git", "config", "user.name", "Hermes Agent"])
    run(["git", "config", "user.email", "wangw9475@agent.qq.com"])

    # checkout or create branch
    run(["git", "checkout", "-B", branch])
    run(["git", "fetch", "origin", branch], check=False)

    # Check if remote branch exists
    result = run(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"], check=False)
    if result.returncode == 0:
        run(["git", "stash", "push", "--include-untracked", "-m", f"upgrade-{upstream_version}"])
        run(["git", "reset", "--hard", f"refs/remotes/origin/{branch}"])
        run(["git", "stash", "pop"], check=False)

    # Stage changes
    run(["git", "add", "UPSTREAM_VERSION", "CHANGELOG.md"])

    # Check if there are changes
    result = run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        log("No changes to commit")
        # Still try to update PR
        pass
    else:
        run(["git", "commit", "-m", title])
        # Push with token
        owner_repo = GITHUB_REPO
        push_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{owner_repo}.git"
        run(["git", "push", "--force-with-lease", push_url, branch])

    # Check if PR already exists
    owner, repo = GITHUB_REPO.split("/", 1)
    existing = github_api("GET", f"/repos/{GITHUB_REPO}/pulls?state=open&head={owner}:{branch}&base=main")
    if existing:
        pr_number = existing[0]["number"]
        github_api("PATCH", f"/repos/{GITHUB_REPO}/pulls/{pr_number}", {"title": title, "body": body})
        log(f"Updated PR #{pr_number}: https://github.com/{GITHUB_REPO}/pull/{pr_number}")
    else:
        pr = github_api("POST", f"/repos/{GITHUB_REPO}/pulls", {"title": title, "body": body, "head": branch, "base": "main"})
        pr_number = pr["number"]
        log(f"Created PR #{pr_number}: https://github.com/{GITHUB_REPO}/pull/{pr_number}")

    return pr_number


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    log(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def main() -> int:
    if not GITHUB_TOKEN:
        log("FATAL: GITHUB_TOKEN 未设置，无法创建 PR")
        return 1

    upstream_version = latest_upstream_tag()
    current_version = current_tracked_version()
    current_key = semver_key(current_version)
    upstream_key = semver_key(upstream_version)

    log(f"当前追踪: {current_version}")
    log(f"上游最新: {upstream_version}")

    if not upstream_key:
        log(f"FATAL: 无法解析上游版本: {upstream_version}")
        return 1

    if current_key and upstream_key <= current_key:
        log("已是最新版本，无需更新")
        return 0

    # Update version file
    VERSION_FILE.write_text(f"{upstream_version}\n", encoding="utf-8")

    # Update changelog
    if CHANGELOG_PATH.exists():
        changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
        section = (
            f"## v{upstream_version}\n\n"
            f"### 上游更新\n"
            f"- Penpot 上游发布 [{upstream_version}](https://github.com/penpot/penpot/releases/tag/{upstream_version})\n"
            f"- ⚠️ 需要人工检查懒猫 Registry 镜像并更新 manifest\n"
            f"\n---\n"
        )
        if f"## v{upstream_version}" not in changelog:
            CHANGELOG_PATH.write_text(section + "\n" + changelog, encoding="utf-8")

    # Create PR
    create_or_update_pr(upstream_version, current_version)
    log("升级检查完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"ERROR: {exc}")
        raise
