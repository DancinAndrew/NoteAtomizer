# `course_note/prompts/` — 課程筆記提示詞模板

## 目的

存放 **Course Note Engine** 使用的純文字 prompt。由 [`../process_course.sh`](../process_course.sh) 以 Bash 讀入並做 placeholder 替換後，經 stdin 傳給 **Gemini CLI**。

## 模板如何被組裝

1. **`base_prompt.txt`**：共用的角色／行為約束（Step 1 與 Step 2 都會在「本輪任務」前附上整份內容）。
2. **Step 1**：在 `step1_prompt.txt` 內替換 `{{TRANSCRIPT}}` → 逐字稿全文（已做 `@` → `＠`），再與 `base_prompt` 接成 `FULL_STEP1_PROMPT`。若有 PDF，腳本會在最前面加上說明與 `@PDF路徑`。
3. **Step 2**：在 `step2_prompt.txt` 內替換：
   - `{{SECTION_TITLE}}` — 當前段落標題  
   - `{{SECTION_TIME_RANGE}}` — 時間區間  
   - `{{FULL_OUTLINE}}` — 由 JSON 大綱展開的可讀文字  
   - `{{TRANSCRIPT}}` — 完整逐字稿（同上遮蔽）  
   再與 `base_prompt`（與可選 PDF 前綴）合併。

**不是**在執行期 import；全是 bash 字串替換。

## 檔案說明

| 檔案 | 職責 |
|------|------|
| [`base_prompt.txt`](base_prompt.txt) | 兩階段共用的基礎指令（語言、角色、輸出風格等） |
| [`step1_prompt.txt`](step1_prompt.txt) | 只產出**時間軸大綱 JSON 陣列**，不含詳細筆記內文；內含 `{{TRANSCRIPT}}` |
| [`step2_prompt.txt`](step2_prompt.txt) | 針對**單一段落**寫深度筆記；含上述四個 placeholder |

## 與其他資料夾的關係

- 執行邏輯與輸出檔名：[`../README.md`](../README.md)
