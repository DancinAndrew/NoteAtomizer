#!/usr/bin/env python3
"""
從模型原始輸出（stdin）提取合法 JSON 陣列。
正規化規則：
  - topic  → string list（1–3 個），單一字串自動包成 list
  - note_type → 單一字串；非白名單值保留原樣（允許擴充）；缺失則補 "mechanism"
成功時印出 JSON 並 exit 0；失敗 exit 1。
"""
import json
import sys

VALID_NOTE_TYPES = {"mechanism", "concept", "comparison", "procedure", "thesis"}
DEFAULT_NOTE_TYPE = "mechanism"


def _normalize_topics(data: list) -> None:
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        t = item.get("topic")
        if isinstance(t, str):
            item["topic"] = [t] if t else []
        elif isinstance(t, list):
            cleaned = [str(x).strip() for x in t if x and str(x).strip()]
            if len(cleaned) > 3:
                print(
                    f"process_note: 警告：第 {i} 筆 topic 超過 3 個，已截斷至前 3 個：{cleaned!r}",
                    file=sys.stderr,
                )
                cleaned = cleaned[:3]
            item["topic"] = cleaned
        elif t is None:
            item["topic"] = []
        else:
            item["topic"] = [str(t)]


def _normalize_note_types(data: list) -> None:
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        nt = item.get("note_type")
        if isinstance(nt, list):
            # 若模型誤輸出 list，只取第一項
            if len(nt) > 1:
                print(
                    f"process_note: 警告：第 {i} 筆 Pass1 輸出含多個 note_type，已只保留第一項：{nt!r}",
                    file=sys.stderr,
                )
            nt = (nt[0] if nt else "") or ""
            item["note_type"] = nt
        elif nt is None or nt == "":
            print(
                f"process_note: 注意：第 {i} 筆 Pass1 缺少 note_type，已補預設值 '{DEFAULT_NOTE_TYPE}'",
                file=sys.stderr,
            )
            item["note_type"] = DEFAULT_NOTE_TYPE
            continue
        elif not isinstance(nt, str):
            item["note_type"] = str(nt)

        # 非白名單但非空的值保留（允許擴充），只記錄 warning
        nt_final = item.get("note_type", "")
        if nt_final and nt_final not in VALID_NOTE_TYPES:
            print(
                f"process_note: 注意：第 {i} 筆 note_type='{nt_final}' 不在預設白名單，"
                "若為新類型請確認已在 system_rules.md 定義其 body 模板。",
                file=sys.stderr,
            )


def main() -> None:
    text = sys.stdin.read()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        sys.exit(1)
    json_str = text[start : end + 1]
    try:
        data = json.loads(json_str)
    except Exception:
        sys.exit(1)
    if not isinstance(data, list):
        sys.exit(1)
    _normalize_topics(data)
    _normalize_note_types(data)
    print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
