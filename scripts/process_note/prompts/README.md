# `process_note/prompts/` — 長文原子化提示詞

## 目的

存放 **Two-Pass** 管線的系統規則與 Pass1／Pass2 純文字模板。由 [`../process_note.sh`](../process_note.sh) 讀入後以 **Bash 字串替換** 填入 placeholder，再 pipe 至 **Gemini CLI**（非執行期載入模板引擎）。

## 檔案角色

| 檔案 | 職責 |
|------|------|
| [`system_rules.md`](system_rules.md) | 全域寫作規範、topic 粒度、`note_type` 分類、**已驗證 Topic 白名單**（程式碼區塊內列表）；Pass1／Pass2 都會注入 |
| [`pass1_meta_prompt.txt`](pass1_meta_prompt.txt) | Pass 1：輸出**單一 JSON 陣列**（檔名、area、note_type、topic、keywords、summary、content_hint 等） |
| [`pass2_content_prompt.txt`](pass2_content_prompt.txt) | Pass 2：依單筆 meta 與 **`{{BODY_TEMPLATE}}`** 產出完整一篇 Markdown（含 YAML frontmatter） |

## Pass 1 主要 placeholder

（實際替換變數名以腳本為準）

| Placeholder | 含義 |
|-------------|------|
| `{{SYSTEM_RULES}}` | 整份 `system_rules.md` |
| `{{EXPECTED_NOTES}}` | 依長度估算的建議篇數區間字串 |
| `{{TOPIC_WHITELIST}}` | 從 `system_rules.md` 內「已驗證 Topic 白名單」區段擷取之列表文字 |
| `{{FILE_CONTENT}}` | 已遮蔽 `@` 後的全文 |

## Pass 2 主要 placeholder

| Placeholder | 含義 |
|-------------|------|
| `{{SYSTEM_RULES}}` | 同上 |
| `{{CONTENT_HINT}}`、`{{AREA}}`、`{{SOURCE_REL_PATH}}`、`{{NOTE_TYPE}}` | 單筆 meta 與歸檔路徑 |
| `{{TOPIC_YAML}}`、`{{KEYWORDS_YAML}}`、`{{SUMMARY}}` | frontmatter 用 |
| `{{BODY_TEMPLATE}}` | 自 [`templates/body_<note_type>.md`](templates/README.md) 讀入 |
| `{{EXISTING_NOTES_CONTEXT}}` | 既有 `02_Areas` 筆記摘要 |
| `{{BATCH_FILES}}` | 同批次其他檔名（排除自己，供連結） |
| `{{FILE_CONTENT}}` | 原文 |

## 子目錄

- [`templates/`](templates/README.md)：各 `note_type` 對應的 body 結構模板。

## 與其他資料夾的關係

- 主流程與後處理：[`../README.md`](../README.md)、[`../lib/README.md`](../lib/README.md)
