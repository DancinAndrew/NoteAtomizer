# `process_note/prompts/templates/` — Body 結構模板

## 目的

為 Pass 2 提供依 **`note_type`** 固定的**正文章節結構**（各檔為 Markdown 片段）。[`../process_note.sh`](../../process_note.sh) 依 Pass 1 JSON 的 `note_type` 欄位選擇對應檔案，將全文讀入變數 `BODY_TEMPLATE`，再替換進 [`../pass2_content_prompt.txt`](../pass2_content_prompt.txt) 的 `{{BODY_TEMPLATE}}`。

- 若某 `note_type` 檔不存在，腳本會 **fallback** 到 `body_mechanism.md`。

## 檔案與 note_type 對應

| 檔案 | `note_type` | 用途（摘要） |
|------|-------------|----------------|
| [`body_mechanism.md`](body_mechanism.md) | `mechanism` | 機制／原理類筆記的預設結構 |
| [`body_concept.md`](body_concept.md) | `concept` | 名詞／定義為主 |
| [`body_comparison.md`](body_comparison.md) | `comparison` | 對照、比較架構 |
| [`body_procedure.md`](body_procedure.md) | `procedure` | 步驟、操作流程 |
| [`body_thesis.md`](body_thesis.md) | `thesis` | 論點、主張、觀點 |

Pass 1 的 JSON 正規化與預設值見 [`../../lib/parse_meta_json.py`](../../lib/parse_meta_json.py)（合法集合含上表五類，其餘值可保留但模板檔需存在或走 fallback）。

## 與 Pass 2 的關係

模型在 Pass 2 被要求**只使用**注入的 body 模板標題與章節，不得混用其他 `note_type` 的章節；實際欄位與禁令見 `pass2_content_prompt.txt` 內文。

## 與其他資料夾的關係

- 上層 prompt 說明：[`../README.md`](../README.md)
- 管線總覽：[`../../README.md`](../../README.md)
