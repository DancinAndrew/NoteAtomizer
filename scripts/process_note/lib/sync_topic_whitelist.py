#!/usr/bin/env python3
"""
比對 Pass 1 產生的 topic 是否有新詞彙，自動追加到 system_rules.md 白名單。
環境變數：
  SYSTEM_RULES_PATH - system_rules.md 的絕對路徑
  META_JSON_DATA    - Pass 1 輸出的 JSON 字串
"""
import json
import os
import re
import sys


def main() -> None:
    rules_path = os.environ.get("SYSTEM_RULES_PATH", "")
    meta_json = os.environ.get("META_JSON_DATA", "")

    if not rules_path or not meta_json:
        print("SKIP: missing env vars")
        return

    try:
        meta = json.loads(meta_json)
    except Exception:
        print("SKIP: meta parse error")
        return

    with open(rules_path, "r", encoding="utf-8") as f:
        content = f.read()

    wl_pos = content.find("已驗證 Topic 白名單")
    if wl_pos == -1:
        print("SKIP: whitelist marker not found")
        return

    block_open = content.find("```", wl_pos)
    block_body_start = block_open + 3
    block_close = content.find("```", block_body_start)
    whitelist_body = content[block_body_start:block_close]

    existing = set(re.findall(r"^- (\w+)", whitelist_body, re.MULTILINE))

    new_entries = []
    seen = set(existing)
    for note in meta:
        topics = note.get("topic", [])
        if isinstance(topics, str):
            topics = [topics]
        area = note.get("area", "unknown")
        for t in topics:
            if t and t not in seen:
                new_entries.append((t, area))
                seen.add(t)

    if not new_entries:
        print("OK: no new topics")
        return

    new_lines = "\n# 自動新增 (Auto-added by process_note.sh)\n"
    for topic, area in sorted(new_entries):
        new_lines += f"- {topic:<22}：（自動新增，area: {area}，請補充說明）\n"
        print(f"  ✅ 新增 topic: {topic}（area: {area}）")

    new_content = content[:block_close] + new_lines + content[block_close:]
    with open(rules_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("📝 system_rules.md 白名單已自動更新")


if __name__ == "__main__":
    main()
