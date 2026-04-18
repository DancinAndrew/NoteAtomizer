#!/usr/bin/env python3
"""
process_note.sh Pass 2 存檔後呼叫：強制 frontmatter 的 up、source 與 note_type 為正確值。
  - up:        若有傳 area，強制為 up: "[[MOC_<area>]]"（YAML 字串，避免 [[…]] 被解析成巢狀陣列；Obsidian 仍視為連結）
  - source:    強制為 source: "[[<vault 相對路徑（無 .md）>]]"
  - note_type: 若模型誤改為 list 或空值，補回 bash 傳入的正確字串

用法：enforce_yaml_source.py <筆記.md> <source_rel_path> <note_type> [area]
      note_type 可傳空字串以略過；area 為 02_Areas 下領域資料夾名（如 01_Machine_Learning）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "用法: enforce_yaml_source.py <筆記.md> <vault 相對路徑，無 .md> [note_type] [area]",
            file=sys.stderr,
        )
        sys.exit(2)
    path = Path(sys.argv[1])
    source_inner = sys.argv[2].strip()
    note_type = sys.argv[3].strip() if len(sys.argv) >= 4 else ""
    area = sys.argv[4].strip() if len(sys.argv) >= 5 else ""

    if not path.is_file():
        sys.exit(0)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    m = re.match(r"^(---\s*\r?\n)(.*?)(\r?\n---\s*\r?\n)", text, re.DOTALL)
    if not m:
        return
    pre, fm, mid = m.group(1), m.group(2), m.group(3)

    # --- 強制 up（必須加引號：裸寫 [[MOC_X]] 在 YAML 會變成 [['MOC_X']]，Dataview 拿不到 .path）---
    if area:
        up_line = f'up: "[[MOC_{area}]]"'
        if re.search(r"^up:\s", fm, re.M):
            fm = re.sub(r"^up:\s.*$", up_line, fm, count=1, flags=re.M)
        else:
            fm = up_line + "\n" + fm

    # --- 強制 source ---
    source_line = f'source: "[[{source_inner}]]"'
    if re.search(r"^source:\s", fm, re.M):
        fm = re.sub(r"^source:\s.*$", source_line, fm, count=1, flags=re.M)
    else:
        fm = fm.rstrip() + "\n" + source_line + "\n"

    # --- 強制 note_type（若有傳入）---
    if note_type:
        nt_line = f'note_type: "{note_type}"'
        # 若 note_type 是 list 形式（模型誤輸出）或空值，強制覆寫整個 note_type 區塊
        # 先嘗試移除可能的 list 形式（多行 note_type:）
        fm = re.sub(
            r"^note_type:[ \t]*\n(?:[ \t]+-[^\n]*\n)+",
            nt_line + "\n",
            fm,
            flags=re.M,
        )
        # 再處理單行 note_type
        if re.search(r"^note_type:\s", fm, re.M):
            fm = re.sub(r"^note_type:\s.*$", nt_line, fm, count=1, flags=re.M)
        else:
            # 不存在則加在 source 後面
            fm = re.sub(
                r"^(source:\s*\".*\")$",
                r"\1\n" + nt_line,
                fm,
                count=1,
                flags=re.M,
            )

    rest = text[len(m.group(0)) :]
    path.write_text(pre + fm + mid + rest, encoding="utf-8")


if __name__ == "__main__":
    main()
