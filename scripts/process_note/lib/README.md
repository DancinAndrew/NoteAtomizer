# `process_note/lib/` — 長文原子化輔助模組

## 目的

供 [`../process_note.sh`](../process_note.sh) 呼叫的 **Python** 小工具：解析模型輸出、維護規則檔、掃描既有筆記、強制 frontmatter、補雙向連結。

## 檔案與呼叫關係

| 檔案 | 呼叫者 | 輸入／輸出（摘要） |
|------|--------|---------------------|
| [`parse_meta_json.py`](parse_meta_json.py) | Pass1 後 `echo "$RAW" \| python3 ...`（stdin） | 從 stdout 擷取 JSON 陣列；正規化 `topic`／`note_type` 為單一字串；缺 `note_type` 時預設 `mechanism` |
| [`sync_topic_whitelist.py`](sync_topic_whitelist.py) | 設定 env：`SYSTEM_RULES_PATH`、`META_JSON_DATA` 後 `python3 ...` | 比對 Pass1 的 topic，將新詞追加寫回 `system_rules.md` 白名單區塊 |
| [`extract_existing_notes.py`](extract_existing_notes.py) | `python3 ... "$VAULT_ROOT"` | 掃描 `02_Areas/*/Content/*.md`，輸出文字映射表（檔名、note_type、topic、summary、摘錄）至 stdout 供 Pass2 替換 `{{EXISTING_NOTES_CONTEXT}}` |
| [`strip_markdown_wrapper.py`](strip_markdown_wrapper.py) | env：`RAW_MD_ENV` 設為模型輸出後 `python3 ...` | 剝除外層 code fence；從合法 YAML frontmatter 起點輸出；處理重複 frontmatter 邊緣情況 |
| [`enforce_yaml_source.py`](enforce_yaml_source.py) | 每篇 Pass2 存檔後：`python3 ... <筆記.md> <source_rel無副檔名> <note_type> <area>` | 強制 `up: "[[MOC_<area>]]"`（引號包住 wikilink，避免 YAML 誤解析）、`source:`、`note_type:` 與腳本預期一致 |
| [`patch_connections.py`](patch_connections.py) | Pass2 全部完成後：`python3 ... <vault_root> <新檔1> [新檔2]...` | 解析新筆「🔗 相關知識連結」中的 `[[連結]]`，向被連結筆記補反向連結 |

## 與其他資料夾的關係

- 主腳本與流程：[`../README.md`](../README.md)
- 全域設定載入：[`../../lib/pipeline_config.py`](../../lib/README.md)（本目錄**不**含 `pipeline_config`，該檔在 `scripts/lib/`）
