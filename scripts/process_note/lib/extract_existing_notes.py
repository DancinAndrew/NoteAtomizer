#!/usr/bin/env python3
"""
掃描 02_Areas/*/Content/*.md，輸出 filename + note_type + topic + summary + 核心概念摘錄映射表。
用法: python3 extract_existing_notes.py <vault_root>

note_type 感知：
  - 所有 note_type 的第一個正文 section 都以 ## 📌 開頭，故 snippet 抽取邏輯不變。
  - 輸出行新增 note_type，讓 Pass 2 在建立關聯時有更豐富的上下文。
  - 若筆記無 note_type（舊筆記向後相容），顯示「-」。
"""
import os
import re
import glob
import sys


# 各 note_type 的第一個 section 標題前綴（用於 snippet 抽取的 fallback 指引）
_NOTE_TYPE_FIRST_SECTION = {
    "mechanism":  "核心概念",
    "concept":    "核心定義",
    "comparison": "比較對象",
    "procedure":  "目標",
    "thesis":     "核心主張",
}


def _extract_snippet(body: str, note_type: str) -> str:
    """從 body 擷取首個 ## 📌 區塊的前兩句。
    所有標準 note_type 的第一個 section 均為 ## 📌 開頭，故此 regex 適用全部類型。
    對無 note_type 的舊筆記同樣有效（舊模板首個 section 也是 ## 📌 核心概念）。
    """
    m = re.search(r"##\s*📌[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
    if not m:
        # fallback：取開頭前兩個非空段落的第一句
        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.startswith("#")]
        text = " ".join(paragraphs[:2])
    else:
        text = m.group(1).strip()

    # 取前兩個句子
    sentences = re.split(r"(?<=[。！？.!?])\s*", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    snippet = " ".join(sentences[:2])
    return snippet[:200] if len(snippet) > 200 else snippet


def main() -> None:
    vault = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VAULT_ROOT", "")
    if not vault:
        print("(目前無現存筆記)")
        return

    result = []
    for fpath in sorted(glob.glob(os.path.join(vault, "02_Areas", "*", "Content", "*.md"))):
        fname = os.path.splitext(os.path.basename(fpath))[0]
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            yaml_block = ""
            body = content
            if content.startswith("---"):
                end = content.find("\n---", 3)
                if end != -1:
                    yaml_block = content[3:end]
                    body = content[end + 4:]

            # note_type（新欄位，舊筆記無此欄位則顯示 "-"）
            nt_m = re.search(r'^note_type:\s*"?([^"\n]+)"?\s*$', yaml_block, re.MULTILINE)
            note_type = nt_m.group(1).strip() if nt_m else "-"

            # topic
            topic_m = re.search(r"^topic:(.*?)(?=^\S|\Z)", yaml_block, re.MULTILINE | re.DOTALL)
            if topic_m:
                topic_raw = topic_m.group(1)
                items = re.findall(r"^\s*-\s*(.+)", topic_raw, re.MULTILINE)
                if items:
                    topic = ", ".join(t.strip().strip("\"'") for t in items)
                else:
                    topic = topic_raw.strip().strip("\"'")
            else:
                topic = "未分類"

            # summary
            summary_m = re.search(r'^summary:\s*"?(.+?)"?\s*$', yaml_block, re.MULTILINE)
            summary = summary_m.group(1).strip().strip('"') if summary_m else "尚無摘要"

            # snippet
            snippet = _extract_snippet(body, note_type)
            snippet_part = f" | 摘錄：{snippet}" if snippet else ""

            result.append(
                f"- [[{fname}]] (分類: {topic or '未分類'}) (type: {note_type}) - {summary or '尚無摘要'}{snippet_part}"
            )
        except Exception:
            pass

    print("\n".join(result) if result else "(目前無現存筆記)")


if __name__ == "__main__":
    main()
