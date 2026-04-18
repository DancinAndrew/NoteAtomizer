#!/usr/bin/env python3
"""
patch_connections.py — 事後雙向補連結腳本

邏輯：
  1. 讀取「本次新生成的筆記」列表
  2. 對每一個新筆記，解析其 🔗 相關知識連結 (Connections) 區塊裡的所有 [[WikiLink]]
  3. 找到被連結的目標筆記（在任意 02_Areas/*/Content/ 下）
  4. 若目標筆記的 🔗 區塊「尚未反向連結回新筆記」，就自動補入

用法：
  python3 patch_connections.py <vault_root> <new_file1.md> [<new_file2.md> ...]
"""
import os
import re
import sys
import glob


CONNECTIONS_HEADER = "## 🔗 相關知識連結 (Connections)"
EMPTY_PLACEHOLDER = "*(目前無現存相關筆記)*"


def _get_summary(yaml_block: str) -> str:
    m = re.search(r'^summary:\s*"?(.+?)"?\s*$', yaml_block, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else ""


def _parse_yaml(content: str) -> str:
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            return content[3:end]
    return ""


def _extract_connections_links(content: str) -> list[str]:
    """從 🔗 區塊抽出所有 [[WikiLink]] 名稱（不含副檔名）。"""
    m = re.search(
        rf"{re.escape(CONNECTIONS_HEADER)}\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    if not m:
        return []
    block = m.group(1)
    return re.findall(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]", block)


def _build_index(vault_root: str) -> dict[str, str]:
    """回傳 {stem: abs_path} for all 02_Areas/*/Content/*.md"""
    index = {}
    pattern = os.path.join(vault_root, "02_Areas", "*", "Content", "*.md")
    for fpath in glob.glob(pattern):
        stem = os.path.splitext(os.path.basename(fpath))[0]
        index[stem] = fpath
    return index


def _inject_backlink(target_path: str, source_stem: str, source_summary: str) -> bool:
    """
    在 target_path 的 🔗 區塊裡新增一條指向 source_stem 的連結。
    若已存在，跳過。回傳是否有實際寫入。
    """
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 已存在就跳過
    if f"[[{source_stem}]]" in content:
        return False

    # 找 🔗 區塊
    header_pos = content.find(CONNECTIONS_HEADER)
    if header_pos == -1:
        # 沒有 🔗 區塊，附加到檔案尾端
        new_entry = f"\n{CONNECTIONS_HEADER}\n- [[{source_stem}]]：{source_summary}\n"
        new_content = content.rstrip() + "\n" + new_entry
    else:
        # 找到區塊結束位置（下一個 ## 或 EOF）
        after_header = content[header_pos + len(CONNECTIONS_HEADER):]
        next_section = re.search(r"\n## ", after_header)
        block_end_rel = next_section.start() if next_section else len(after_header)

        block_start = header_pos + len(CONNECTIONS_HEADER)
        block_end = block_start + block_end_rel

        current_block = content[block_start:block_end]
        new_line = f"\n- [[{source_stem}]]：{source_summary}"

        # 移除空白佔位符
        current_block_cleaned = current_block.replace(EMPTY_PLACEHOLDER, "").replace(
            "*(目前無現存相關筆記)*", ""
        )

        new_content = (
            content[:block_start]
            + current_block_cleaned.rstrip()
            + new_line
            + "\n"
            + content[block_end:]
        )

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python3 patch_connections.py <vault_root> <new_file1.md> [...]")
        sys.exit(1)

    vault_root = sys.argv[1]
    new_files = sys.argv[2:]

    note_index = _build_index(vault_root)
    patched_count = 0

    for new_file in new_files:
        if not os.path.isfile(new_file):
            print(f"⚠️  找不到檔案，跳過: {new_file}")
            continue

        source_stem = os.path.splitext(os.path.basename(new_file))[0]

        with open(new_file, "r", encoding="utf-8") as f:
            source_content = f.read()

        source_summary = _get_summary(_parse_yaml(source_content))
        if not source_summary:
            source_summary = f"參見 {source_stem}"

        linked_stems = _extract_connections_links(source_content)

        for linked_stem in linked_stems:
            # 排除自我連結（二重保險）
            if linked_stem == source_stem:
                continue

            target_path = note_index.get(linked_stem)
            if not target_path:
                continue

            injected = _inject_backlink(target_path, source_stem, source_summary)
            if injected:
                print(f"🔗 雙向補連結: {source_stem} → {linked_stem} (已在 {linked_stem} 補入反向連結)")
                patched_count += 1

    if patched_count == 0:
        print("✅ 雙向連結檢查完成，無需補入。")
    else:
        print(f"✅ 雙向補連結完成，共補入 {patched_count} 條反向連結。")


if __name__ == "__main__":
    main()
