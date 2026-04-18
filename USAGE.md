# 使用指南

> 架構設計與技術細節見 **[scripts/README.md](scripts/README.md)**。

`cd /Users/andrew-ideaslab/Documents/Obsidian`

---

## 初始化空白 Vault（第一次使用）

在空的 Obsidian Vault 中建立完整的 PARA 資料夾結構：

```bash
# 確認 scripts/config.yaml 的 vault_root 指向你的 Vault 路徑
# 然後執行：

bash scripts/init/init_vault.sh
```

這會建立以下頂層資料夾（已存在的不覆蓋）：

| 資料夾 | 用途 |
|--------|------|
| `01_Projects/` | 有截止日期的短期專案 |
| `02_Areas/` | 長期知識領域（含 `00_MOC_MAP/`） |
| `03_Resources/` | 長文、講義等原料（管線入口） |
| `04_Archive/` | 冷封存 |
| `05_Journal/` | 每日日誌 |
| `06_finish/` | 脫水完成的歸檔區 |
| `07_temp/` | 暫存工作區 |
| `98 Books/` | 書籍筆記 |
| `99_Attachments/` | 圖片、PDF 等附件 |

接著編輯 `scripts/init/areas.txt`，填入你要在 `02_Areas/` 底下建立的領域（建議格式 `NN_Name`，例如 `01_Machine_Learning`）：

```
# scripts/init/areas.txt
01_Machine_Learning
02_Software_Engineering
03_System_Design
```

填好後執行：

```bash
bash scripts/init/init_areas.sh
```

每個領域會自動建立 `Content/` 子資料夾（原子筆記落點）。兩支腳本均為冪等，重跑安全。

---

## 依賴安裝

### 選擇 LLM（擇一即可）

**Gemini CLI**
```bash
# https://github.com/google-gemini/gemini-cli
# 安裝後登入 Google 帳號
```

**Claude Code**
```bash
npm install -g @anthropic-ai/claude-code
# 安裝後執行 claude 登入
```

### 共同工具

```bash
# CLI 工具
brew install jq

# Python 套件
pip install -r scripts/requirements.txt
```

Obsidian 端需安裝 **Dataview** 插件（Area MOC 的 DataviewJS 才能動態渲染）。

---

## 選擇 LLM 供應商

在 `scripts/config.yaml` 的 `llm.provider` 設定全域預設：

```yaml
llm:
  provider: "gemini"    # 改成 "claude" 即可切換全部管線
```

### 單管線獨立覆寫

只想讓某條管線用 Claude，其他維持 Gemini：

```yaml
process_note:
  provider: "claude"    # 只有此管線切換

course_note:
  provider: ""          # 空白 = 繼承全域 llm.provider
```

### 模型設定

```yaml
gemini:
  model: "gemini-3.1-pro-preview"
  fallback_model: "gemini-2.5-pro"

claude:
  model: "claude-opus-4-7"
```

各管線可用 `model:` 個別覆寫（留空繼承 provider 預設）。

---

## 主管線：長文原子化（`process_note.sh`）

### 執行

```bash
scripts/process_note/process_note.sh "/絕對路徑/你的長文.md"
```

長文放在 `03_Resources/<主題資料夾>/`（推薦）或任意絕對路徑皆可。

### 完整流程

```
wc -l 動態量測
  → Pass 1：MECE 拆解規劃（輸出 JSON 藍圖）
  → 白名單：新 topic 自動追加至 scripts/process_note/prompts/system_rules.md
  → 30s 冷卻（避免 API 限流）
  → Pass 2：逐篇深度萃取 → 02_Areas/$AREA/Content/<檔名>.md
  → enforce_yaml_source：source wikilink 強制指向 06_finish 對應路徑
  → 原始長文自動 mv 至 06_finish/（保留 03_Resources 下子資料夾層級）
  → 可選：互動確認後 git push
```

### 調整模型

```yaml
# scripts/config.yaml
process_note:
  model: ""             # 留空繼承 <provider>.model；填入值則僅此管線覆寫
```

---

## 課程筆記管線（`process_course.sh`）

專門處理**課程影片逐字稿 + 講義 PDF**，輸出單一深度課程筆記（保留時間軸、整合概念解釋）。

```bash
# 有 PDF 講義
scripts/course_note/process_course.sh \
  /path/to/07_temp/Security_Class_01/transcript.md \
  /path/to/07_temp/Security_Class_01/slides.pdf

# 沒有 PDF
scripts/course_note/process_course.sh \
  /path/to/07_temp/Security_Class_01/transcript.md
```

輸出自動寫入逐字稿所在資料夾的 `note.md`。

### PDF 支援

Gemini CLI 與 Claude Code 均以 `@pdf路徑` 語法原生支援 PDF，無需額外轉換。切換 provider 時 PDF 功能照常運作。

### 流程

```
逐字稿 + PDF（可選）
  → Step 1：LLM 分析課程時間軸，產出 JSON 大綱（段落標題 + 時間區間）
  → 60s 冷卻
  → Step 2：逐段呼叫 LLM，產出深度筆記（詳盡摘要 + Concept 解釋 + 深度補充）
  → Shell >> append 寫入 note.md（每段完成即寫入，失敗可重試）
  → 段落間冷卻
```

Prompt 模板在 `scripts/course_note/prompts/`：`base_prompt.txt`（角色／格式）、`step1_prompt.txt`、`step2_prompt.txt`。

---

## 來源連結（`source`）與歸檔

- 原子筆記的 `source` 使用 **Vault 相對路徑、無 `.md`** 的 wikilink，存檔後由 `enforce_yaml_source.py` 強制對齊。
- 脫水完成後，來源檔自動進 `06_finish/`；若原本在 `03_Resources/AI/某篇.md`，則移到 `06_finish/AI/某篇.md`。
- **舊筆記的 source 路徑飄移**：編輯 `scripts/rewrite_note_sources/rewrite_note_sources.yaml` 後執行：

```bash
# 先 dry-run 確認影響範圍
python3 scripts/rewrite_note_sources/rewrite_note_sources.py --pipeline-config scripts/config.yaml --dry-run

# 確認無誤後實際寫入
python3 scripts/rewrite_note_sources/rewrite_note_sources.py --pipeline-config scripts/config.yaml
```

---

## Keyword MOC

從各篇 `keywords:` 抽取所有唯一關鍵字（不送正文），一次送給 LLM 配合你的需求做語意篩選與分組，產出單一聚合 MOC 至 `02_Areas/00_MOC_MAP/`。

```bash
python3 scripts/build_keyword_mocs.py --request "你的需求"
```

模型、`output_dir`、`scan_roots` 等設定統一在 `scripts/config.yaml` 的 `keyword_moc` 區塊調整。

### 參數

| 參數 | 說明 |
|------|------|
| `--request TEXT` | 必填。自然語言需求，例如「我下週面試後端，想複習 Flask 和 PostgreSQL」或貼入 JD |
| `--moc-name TITLE` | 選填。強制指定 MOC 標題（英文底線，不含 `MOC_` 前綴）；省略則由 LLM 自動命名 |
| `--dry-run` | 只印出會寫入的路徑與筆記數，不實際寫檔 |
| `--offline` | 不呼叫任何 LLM，用陽春關鍵字比對（僅測試流程用） |

### 範例

```bash
# 後端面試複習（使用 config.yaml 中的預設 provider）
python3 build_keyword_mocs.py \
  --request "我下週面試後端工程師，想複習 Flask 和 PostgreSQL，以下是 JD：..."

# 先 dry-run 確認結果
python3 build_keyword_mocs.py \
  --request "系統設計面試準備" \
  --moc-name "System_Design_Prep" \
  --dry-run

# 不想等 LLM，測試流程
python3 build_keyword_mocs.py --request "Flask REST" --offline
```

### 輸出格式

產出單一 `MOC_<title>.md`，內依 LLM 判斷的語意分組排成 H2 區塊：

```markdown
## Flask
- [[02_Areas/02_Software_Engineering/Content/Flask_Application_Factory...]] — Flask 工廠模式...
- [[02_Areas/02_Software_Engineering/Content/Jinja2_Template_Engine...]] — Jinja2 模板...

## PostgreSQL
- [[02_Areas/05_Database/Content/Why_CSV_Fails...]] — 為什麼 CSV 不能當資料庫...
```

### Token 消耗

約 **~1000 tokens，一次呼叫**（送所有 unique keywords + 需求；不送正文）。

---

## 手寫 MOC（選做）

完全手動在 `02_Areas/00_MOC_MAP/` 寫主題頁，代表**你自己的理解路徑**：

```markdown
# MOC_Flask.md
## 核心架構
- [[Flask_Application_Factory]] - 工廠模式讓 App 可測試
## 部署
- [[Gunicorn_Worker_Model]] - Worker 數量與模型選擇
```

---

## 輔助腳本一覽（`scripts/`）

| 路徑 | 說明 |
|------|------|
| `config.yaml` | **全域設定**：vault 路徑、LLM provider、各管線模型與冷卻參數 |
| `init/init_vault.sh` | **初始化**：建立 PARA 頂層資料夾結構 + 產生 `areas.txt` 樣板 |
| `init/init_areas.sh` | **初始化**：依 `areas.txt` 在 `02_Areas/` 建立領域與 `Content/` |
| `init/areas.txt` | 使用者填寫的領域清單（`init_vault.sh` 首次執行時自動產生） |
| `lib/pipeline_config.py` | 設定載入器（bash 與 Python 腳本共用） |
| `lib/llm_runner.py` | **LLM 抽象層**：統一 Gemini CLI / Claude Code 呼叫介面 |
| `process_note/process_note.sh` | 主管線：長文 → 原子筆記 |
| `process_note/prompts/system_rules.md` | 知識原子化系統指令（含 topic 白名單） |
| `process_note/lib/enforce_yaml_source.py` | Pass 2 後強制 `source` wikilink 對齊 |
| `process_note/lib/extract_existing_notes.py` | 掃描 02_Areas 現有筆記的 topic/summary |
| `process_note/lib/parse_meta_json.py` | 從模型原始輸出提取合法 JSON |
| `process_note/lib/strip_markdown_wrapper.py` | 剝除 LLM 輸出的外層 Markdown fence |
| `process_note/lib/sync_topic_whitelist.py` | 比對新 topic，自動追加至 system_rules.md |
| `course_note/process_course.sh` | 課程逐字稿 + PDF → 深度筆記 |
| `keyword_moc_builder/build_keyword_mocs.py` | 需求驅動 Keyword MOC |
| `keyword_moc_builder/keyword_classifier.py` | LLM-agnostic 關鍵字語意分類模組 |
| `rewrite_note_sources/` | 批次修正歷史 `source` wikilink（無 LLM 呼叫） |
| `Daily_Template.md` | 日誌模板 |

> **為什麼把 `system_rules.md` 放在 `prompts/` 而不是 Vault 根目錄？**
> Claude Code 會自動把 CWD 到 `.git` 根目錄沿途的所有 `CLAUDE.md` 注入每次呼叫；Gemini 會注入 `GEMINI.md`。放在根目錄會讓 `course_note/`、`keyword_moc_builder/` 也吃到這份 system prompt，造成意外影響。現在只由 `process_note.sh` 透過 `cat` 讀取後 pipe 注入，完全隔離。
