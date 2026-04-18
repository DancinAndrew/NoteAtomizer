#!/usr/bin/env python3
"""
Keyword MOC Builder

從 Obsidian 筆記 YAML frontmatter 的 `keywords:` 收集所有唯一關鍵字，
送給 LLM CLI（Gemini 或 Claude）配合使用者需求做語意篩選與分組，
產出單一聚合 MOC 檔至 02_Areas/00_MOC_MAP/。

LLM 供應商由 scripts/config.yaml 的 `llm.provider` 控制（預設 gemini）。

用法：
  python3 build_keyword_mocs.py --request "我下週面試後端，想複習 Flask 和 PostgreSQL"
  python3 build_keyword_mocs.py --request "..." --moc-name "My_Study_Plan"
  python3 build_keyword_mocs.py --request "..." --dry-run
  python3 build_keyword_mocs.py --request "..." --offline   # 不呼叫 LLM，僅測試流程
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from keyword_classifier import (
    DEFAULT_MODEL,
    classify_keywords_by_request,
    offline_classify_guess,
)

# pipeline_config 在 scripts/lib/，與此腳本不在同一目錄，動態加入路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from pipeline_config import expand_for_keyword_moc, resolve_llm_bin  # noqa: E402

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL)


@dataclass
class NoteRecord:
    rel_path: str  # vault-relative posix path, no .md suffix
    title: str
    summary: str | None
    keywords_raw: list[str] = field(default_factory=list)


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def vault_root_from_config(config_path: Path, cfg: dict[str, Any]) -> Path:
    vr = (cfg.get("vault_root") or "").strip()
    if vr:
        return Path(vr).expanduser().resolve()
    # default: scripts/keyword_moc_builder/ → vault root
    return (config_path.parent.parent.parent).resolve()


def should_skip_file(rel_posix: str, exclude_substrings: list[str]) -> bool:
    return any(sub and sub in rel_posix for sub in exclude_substrings)


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, content
    if not isinstance(meta, dict):
        return None, content
    return meta, content[m.end():]


def collect_notes(
    vault: Path,
    scan_roots: list[str],
    exclude_substrings: list[str],
) -> list[NoteRecord]:
    notes: list[NoteRecord] = []
    for root in scan_roots:
        base = vault / root
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            rel = path.relative_to(vault).as_posix()
            if should_skip_file(rel, exclude_substrings):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            meta, _ = parse_frontmatter(text)
            if not meta:
                continue
            raw_kw = meta.get("keywords")
            if raw_kw is None:
                continue
            if isinstance(raw_kw, str):
                kws = [raw_kw]
            elif isinstance(raw_kw, list):
                kws = [str(x) for x in raw_kw if str(x).strip()]
            else:
                continue
            if not kws:
                continue
            summary = meta.get("summary")
            if summary is not None:
                summary = str(summary).strip() or None
            notes.append(
                NoteRecord(
                    rel_path=rel[:-3] if rel.endswith(".md") else rel,
                    title=path.stem,
                    summary=summary,
                    keywords_raw=kws,
                )
            )
    return notes


def unique_keywords_in_order(notes: list[NoteRecord]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for n in notes:
        for k in n.keywords_raw:
            k = str(k).strip()
            if k and k not in seen:
                seen.add(k)
                out.append(k)
    return out


def build_keyword_index(notes: list[NoteRecord]) -> dict[str, list[NoteRecord]]:
    """keyword (case-folded) → list of NoteRecord"""
    idx: dict[str, list[NoteRecord]] = defaultdict(list)
    seen: dict[str, set[str]] = defaultdict(set)
    for note in notes:
        for raw in note.keywords_raw:
            kn = raw.strip().casefold()
            if kn and note.rel_path not in seen[kn]:
                idx[kn].append(note)
                seen[kn].add(note.rel_path)
    return dict(idx)


def safe_moc_filename(title: str) -> str:
    t = re.sub(r'[<>:"/\\|?*\s]', "_", title)
    t = t.strip("_") or "Custom_MOC"
    return f"MOC_{t}.md"


def render_grouped_moc(
    moc_title: str,
    groups: dict[str, list[NoteRecord]],
    user_request: str,
) -> str:
    escaped_request = user_request.replace('"', '\\"')
    lines = [
        "---",
        "tags:",
        "  - type/moc",
        "  - moc/keyword",
        f'request: "{escaped_request}"',
        f"generated: {date.today().isoformat()}",
        "---",
        "",
        f"# MOC — {moc_title.replace('_', ' ')}",
        "",
        f"> 由 `build_keyword_mocs.py` 依需求「{user_request}」自動篩選相關筆記後產出；更新時請再執行腳本。",
        "",
    ]
    for group_name, notes in groups.items():
        if not notes:
            continue
        lines.append(f"## {group_name}")
        lines.append("")
        for n in sorted(notes, key=lambda x: x.rel_path.casefold()):
            link = f"[[{n.rel_path}]]"
            if n.summary:
                lines.append(f"- {link} — {n.summary}")
            else:
                lines.append(f"- {link}")
        lines.append("")
    return "\n".join(lines)


def run_smart_mode(
    cfg: dict[str, Any],
    vault: Path,
    notes: list[NoteRecord],
    user_request: str,
    moc_name_override: str | None,
    *,
    offline: bool,
    dry_run: bool,
) -> int:
    # 從 expand_for_keyword_moc 轉換後的 cfg 讀取 llm 設定
    llm_cfg = cfg.get("llm") if isinstance(cfg.get("llm"), dict) else {}
    provider = cfg.get("provider") or "gemini"
    model = (llm_cfg.get("model") or DEFAULT_MODEL).strip()
    extra_flags = (llm_cfg.get("extra_flags") or "").strip()

    unique = unique_keywords_in_order(notes)
    print(f"唯一關鍵字數（去重）: {len(unique)}")
    if not unique:
        print("沒有關鍵字，無法產生 MOC。", file=sys.stderr)
        return 1

    if offline:
        print("模式: --offline（不呼叫 LLM，陽春關鍵字比對）")
        result = offline_classify_guess(user_request, unique)
    else:
        llm_bin = (llm_cfg.get("bin") or "").strip()
        if not llm_bin:
            llm_bin = resolve_llm_bin(cfg, provider)
        assert llm_bin, f"找不到 {provider} CLI 執行檔"
        print(f"模式: {provider} CLI `{llm_bin}` model={model}")
        print(f"需求: {user_request}")
        result = classify_keywords_by_request(
            user_request,
            unique,
            provider=provider,
            bin_path=llm_bin,
            model=model,
            extra_flags=extra_flags,
        )

    moc_title = moc_name_override or result.get("moc_title") or "Custom_MOC"
    raw_groups: dict[str, list[str]] = result.get("groups") or {}

    print(f"MOC 標題: {moc_title}")
    for gname, kws in raw_groups.items():
        print(f"  [{gname}] {len(kws)} 個關鍵字: {', '.join(kws[:8])}{'…' if len(kws) > 8 else ''}")

    # 建立 keyword index，用 groups 反查筆記
    kw_index = build_keyword_index(notes)
    grouped_notes: dict[str, list[NoteRecord]] = {}
    total_notes = 0
    seen_paths: set[str] = set()

    for group_name, kw_list in raw_groups.items():
        group_notes: list[NoteRecord] = []
        for kw in kw_list:
            for note in kw_index.get(kw.strip().casefold(), []):
                if note.rel_path not in seen_paths:
                    group_notes.append(note)
                    seen_paths.add(note.rel_path)
        if group_notes:
            grouped_notes[group_name] = group_notes
            total_notes += len(group_notes)

    print(f"列入 MOC 的筆記總數: {total_notes} 篇（{len(grouped_notes)} 個分組）")

    if not grouped_notes:
        print("⚠️  沒有筆記符合 Gemini 回傳的關鍵字，請確認 vault 內筆記的 keywords 欄位是否正確。", file=sys.stderr)
        return 1

    out_dir = vault / (cfg.get("output_dir") or "02_Areas/00_MOC_MAP")
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_moc_filename(moc_title)
    path = out_dir / fname

    body = render_grouped_moc(moc_title, grouped_notes, user_request)
    print(f"輸出: {path.relative_to(vault)}")

    if not dry_run:
        path.write_text(body, encoding="utf-8")
    else:
        print("(dry-run：未寫入)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="依使用者需求語意篩選 keywords，產生聚合 MOC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python3 build_keyword_mocs.py --request "我下週面試後端，想複習 Flask 和 PostgreSQL"
  python3 build_keyword_mocs.py --request "系統設計面試準備" --moc-name "System_Design_Prep"
  python3 build_keyword_mocs.py --request "複習 REST API" --dry-run
  python3 build_keyword_mocs.py --request "測試流程" --offline
""",
    )
    ap.add_argument(
        "--request",
        required=True,
        metavar="TEXT",
        help="自然語言需求，例如：「我下週面試後端，想複習 Flask 和 PostgreSQL」",
    )
    ap.add_argument(
        "--moc-name",
        metavar="TITLE",
        help="強制指定 MOC 標題（英文底線，不含 MOC_ 前綴）；省略則由 Gemini 自動命名",
    )
    ap.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "config.yaml",
        help="設定檔路徑（預設：scripts/config.yaml；仍支援舊的 keyword_moc_builder/config.yaml）",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="只印出結果，不實際寫入 MOC 檔",
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="不呼叫 Gemini CLI，用陽春規則比對（僅測試流程用）",
    )
    args = ap.parse_args()

    raw_cfg = load_config(args.config)
    # 若為 pipeline config（含 keyword_moc 鍵），展開成 legacy 格式
    cfg = expand_for_keyword_moc(args.config.resolve(), raw_cfg)
    vault = vault_root_from_config(args.config.resolve(), cfg)
    if not vault.is_dir():
        print(f"vault_root 不是目錄: {vault}", file=sys.stderr)
        return 1

    provider = cfg.get("provider") or "gemini"
    llm_cfg = cfg.get("llm") if isinstance(cfg.get("llm"), dict) else {}
    llm_bin = (llm_cfg.get("bin") or "").strip() or resolve_llm_bin(cfg, provider)
    if not args.offline and not llm_bin:
        print(
            f"找不到 `{provider}` CLI（請安裝並設定 scripts/config.yaml 的 {provider}.bin）；"
            "亦可用 --offline 測試。",
            file=sys.stderr,
        )
        return 1

    scan_roots = cfg.get("scan_roots") or ["02_Areas"]
    exclude_substrings = cfg.get("exclude_path_substrings") or []

    notes = collect_notes(vault, scan_roots, exclude_substrings)
    print(f"Vault: {vault}")
    print(f"掃描到含 keywords 的筆記: {len(notes)}")

    return run_smart_mode(
        cfg,
        vault,
        notes,
        user_request=args.request,
        moc_name_override=args.moc_name,
        offline=args.offline,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
