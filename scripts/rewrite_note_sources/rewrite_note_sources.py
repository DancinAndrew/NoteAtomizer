#!/usr/bin/env python3
"""
歸檔長文搬移後，批次修正 02_Areas 筆記 frontmatter 的 `source:` wikilink。

設定檔：scripts/rewrite_note_sources/rewrite_note_sources.yaml
  - exact：整行字串替換（最優先）
  - prefix_in_link：只處理 source 行，替換 [[ 與 ]] 內路徑的前綴

  python3 scripts/rewrite_note_sources/rewrite_note_sources.py
  python3 scripts/rewrite_note_sources/rewrite_note_sources.py --dry-run

  # 使用 pipeline config 自動解析 vault 路徑與規則檔位置
  python3 scripts/rewrite_note_sources/rewrite_note_sources.py --pipeline-config scripts/config.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# pipeline_config 在 scripts/lib/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pipeline_config import load_config as _load_pipeline_config, resolve_vault_root  # noqa: E402


def load_rules(cfg_path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    with cfg_path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    exact = []
    for item in cfg.get("exact", []) or []:
        a, b = item.get("from"), item.get("to")
        if a is not None and b is not None:
            exact.append((str(a), str(b)))
    prefix = []
    for item in cfg.get("prefix_in_link", []) or []:
        a, b = item.get("from"), item.get("to")
        if a is not None and b is not None:
            prefix.append((str(a), str(b)))
    return exact, prefix


def apply_prefix_to_sources(text: str, prefix: list[tuple[str, str]]) -> str:
    if not prefix:
        return text

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        for old, new in prefix:
            if inner.startswith(old):
                inner = new + inner[len(old) :]
                break
        return f'source: "[[{inner}]]"'

    return re.sub(
        r'^source:\s*"\[\[([^\]]+)\]\]"\s*$',
        repl,
        text,
        flags=re.MULTILINE,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "rewrite_note_sources.yaml",
        help="連結替換規則檔（預設：rewrite_note_sources.yaml）",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--vault",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Vault 根目錄（預設：repo 根目錄）",
    )
    ap.add_argument(
        "--pipeline-config",
        type=Path,
        default=None,
        metavar="PATH",
        help="pipeline config 路徑（scripts/config.yaml）；若提供則覆寫 --vault 與 --config 預設值",
    )
    args = ap.parse_args()

    # --pipeline-config 優先覆寫 vault 與規則檔預設
    if args.pipeline_config is not None:
        if not args.pipeline_config.is_file():
            print(f"找不到 pipeline config: {args.pipeline_config}", file=sys.stderr)
            return 1
        pc = _load_pipeline_config(args.pipeline_config)
        args.vault = resolve_vault_root(args.pipeline_config.resolve(), pc)
        rns = pc.get("rewrite_note_sources") or {}
        rules_rel = (rns.get("rules_file") or "").strip()
        if rules_rel:
            args.config = args.vault / rules_rel

    if not args.config.is_file():
        print(f"找不到設定: {args.config}", file=sys.stderr)
        return 1

    exact, prefix = load_rules(args.config)
    scan = args.vault / "02_Areas"
    if not scan.is_dir():
        print(f"找不到 {scan}", file=sys.stderr)
        return 1

    changed = 0
    for md in sorted(scan.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        new = text
        for a, b in exact:
            new = new.replace(a, b)
        new = apply_prefix_to_sources(new, prefix)
        if new != text:
            changed += 1
            print(md.relative_to(args.vault))
            if not args.dry_run:
                md.write_text(new, encoding="utf-8")

    print(f"已變更 {changed} 個檔案" + ("（dry-run，未寫入）" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
