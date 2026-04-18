#!/usr/bin/env python3
"""
剝除 Gemini 輸出最外層的 Markdown code block wrapper，
並從第一個 '---' 行開始輸出（YAML frontmatter 起點）。
原始內容透過環境變數 RAW_MD_ENV 傳入。

Double-YAML 防護：若輸出包含多個 YAML frontmatter（LLM 生成兩次），
只保留「最後一個完整 frontmatter」開始的內容。
"""
import os
import re


def _find_last_complete_frontmatter_start(text: str) -> int:
    """
    找到最後一個合法的 YAML frontmatter 起點。
    合法 frontmatter 定義：緊接著 --- 有 tags: 或 source: 或 up: 這類 YAML key。
    """
    positions = [m.start() for m in re.finditer(r'(^|\n)---\ntags:', text)]
    if positions:
        return positions[-1] if positions[-1] != 0 else 0
    # fallback：找第一個 ---
    m = re.search(r'(^|\n)---\n', text)
    return m.start() if m else 0


def main() -> None:
    raw = os.environ.get("RAW_MD_ENV", "")

    lines = raw.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

    text = "\n".join(lines)

    # 找合法的 YAML 起點
    for i, line in enumerate(lines):
        if line.strip() == "---":
            text = "\n".join(lines[i:])
            break

    # Double-YAML 防護：若有多個 frontmatter，取最後一個
    occurrences = [m.start() for m in re.finditer(r'(^|\n)---\ntags:', text)]
    if len(occurrences) > 1:
        import sys
        print("[strip_markdown_wrapper] ⚠️ 偵測到多個 YAML frontmatter，保留最後一個。", file=sys.stderr)
        last_pos = occurrences[-1]
        # 如果不是在行首，往前找換行
        if last_pos > 0 and text[last_pos] == '\n':
            last_pos += 1
        text = text[last_pos:]

    print(text)


if __name__ == "__main__":
    main()
