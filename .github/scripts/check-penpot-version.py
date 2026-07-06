#!/usr/bin/env python3
"""Check upstream Penpot releases and prepare upgrade notes.

Checks the latest Penpot release against the tracked version in UPSTREAM_VERSION.
Only notifies — does NOT automatically update images, since LazyCat registry images
use content hashes that need manual mapping.
"""

from __future__ import annotations

import os
import re
import urllib.request
import json
from pathlib import Path
from typing import Optional

UPSTREAM_REPO = "penpot/penpot"
VERSION_FILE = Path("UPSTREAM_VERSION")
CHANGELOG_PATH = Path("CHANGELOG.md")

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def semver_key(tag: str) -> Optional[tuple[int, int, int]]:
    match = SEMVER_RE.match(tag)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def latest_upstream_tag() -> str:
    """Get the latest semver release tag from Penpot."""
    url = f"https://api.github.com/repos/{UPSTREAM_REPO}/releases?per_page=10"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "Penpot-Check-Workflow",
    })
    with urllib.request.urlopen(req) as resp:
        releases = json.load(resp)

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


def write_github_output(values: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    upstream_version = latest_upstream_tag()
    current_version = current_tracked_version()
    current_key = semver_key(current_version)
    upstream_key = semver_key(upstream_version)

    print(f"当前追踪版本: {current_version}")
    print(f"上游最新版本: {upstream_version}")

    if not upstream_key:
        raise RuntimeError(f"无法解析上游版本: {upstream_version}")

    if current_key and upstream_key <= current_key:
        print("当前已是最新 upstream 版本，无需创建升级 PR")
        write_github_output({
            "changed": "false",
            "current_version": current_version,
            "upstream_version": upstream_version,
        })
        return 0

    # Update the tracked version
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

    print(f"已更新追踪版本至 {upstream_version}")
    write_github_output({
        "changed": "true",
        "current_version": current_version,
        "upstream_version": upstream_version,
    })
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"::error::{exc}", file=__import__("sys").stderr)
        raise
