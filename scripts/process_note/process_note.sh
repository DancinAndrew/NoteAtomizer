#!/bin/bash

# ==============================================================================
# Second Brain: FDE 兩階段硬派寫入引擎 (Two-Pass + Bash I/O Control)
# 功能：Pass 1 規劃 Meta (JSON) -> Pass 2 深度萃取 -> Bash 強制存檔
# ==============================================================================

# ------------------------------------------------------------------------------
# 0. 環境設定與初始化 (Environment Setup)
# ------------------------------------------------------------------------------
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
LIB_DIR="$SCRIPT_DIR/lib"

# --- 核心變數配置（從 scripts/config.yaml 讀取）---
_CONFIG="$SCRIPT_DIR/../config.yaml"
_CFG="python3 $SCRIPT_DIR/../lib/pipeline_config.py $_CONFIG"
_RUNNER="python3 $SCRIPT_DIR/../lib/llm_runner.py"

VAULT_ROOT=$($_CFG global vault_root)
PROVIDER=$($_CFG process_note provider)
LLM_BIN=$($_CFG process_note llm_bin)
SELECTED_MODEL=$($_CFG process_note llm_model)
LLM_EXTRA_FLAGS=$($_CFG process_note llm_extra_flags)
COOLDOWN_AFTER_PASS1=$($_CFG process_note cooldown_after_pass1)
COOLDOWN_BETWEEN_PASS2=$($_CFG process_note cooldown_between_pass2)

SYSTEM_RULES_PATH="$PROMPTS_DIR/system_rules.md"

# --- 參數與檔案檢查 ---
if [ -z "$1" ]; then
    echo "❌ 錯誤：請提供筆記的絕對路徑"
    echo "   用法: ./process_note.sh /絕對路徑/筆記.md"
    exit 1
fi

if [ -f "$1" ]; then
    FILE_PATH="$1"
else
    echo "❌ 錯誤：找不到檔案 $1"
    echo "   請確認路徑正確（需為絕對路徑）"
    exit 1
fi

for required in "$SYSTEM_RULES_PATH" \
                "$PROMPTS_DIR/pass1_meta_prompt.txt" \
                "$PROMPTS_DIR/pass2_content_prompt.txt"; do
    if [ ! -f "$required" ]; then
        echo "❌ 錯誤：找不到必要檔案 $required"
        exit 1
    fi
done

TEMPLATES_DIR="$PROMPTS_DIR/templates"
for nt in mechanism concept comparison procedure thesis; do
    if [ ! -f "$TEMPLATES_DIR/body_${nt}.md" ]; then
        echo "❌ 錯誤：找不到 body 模板 $TEMPLATES_DIR/body_${nt}.md"
        exit 1
    fi
done

# --- 讀取系統指令與 prompt 模板 ---
SYSTEM_RULES=$(cat "$SYSTEM_RULES_PATH")
PASS1_TEMPLATE=$(cat "$PROMPTS_DIR/pass1_meta_prompt.txt")
PASS2_TEMPLATE=$(cat "$PROMPTS_DIR/pass2_content_prompt.txt")

# --- 動態擷取 Topic 白名單 ---
TOPIC_WHITELIST=$(sed -n '/📋 已驗證 Topic 白名單/,/```/p' "$SYSTEM_RULES_PATH" | grep -v '📋 已驗證 Topic 白名單' | sed 's/```//g')

# 🛡️ 終極防禦一：巨集遮蔽 (Macro Masking)
FILE_CONTENT=$(cat "$FILE_PATH" | sed 's/@/＠/g')

# --- 歸檔路徑計算 ---
if [[ "$FILE_PATH" == "$VAULT_ROOT/06_finish"* ]]; then
    SOURCE_REL_PATH="${FILE_PATH#$VAULT_ROOT/}"
    SOURCE_REL_PATH="${SOURCE_REL_PATH%.md}"
    ARCHIVE_DEST=""
    SKIP_ARCHIVE_TO_FINISH=1
elif [[ "$FILE_PATH" == "$VAULT_ROOT/03_Resources"* ]]; then
    REL_IN_RES="${FILE_PATH#$VAULT_ROOT/03_Resources/}"
    SOURCE_REL_PATH="06_finish/${REL_IN_RES%.md}"
    ARCHIVE_DEST="$VAULT_ROOT/06_finish/$REL_IN_RES"
    SKIP_ARCHIVE_TO_FINISH=0
else
    BN="$(basename "$FILE_PATH")"
    SOURCE_REL_PATH="06_finish/${BN%.md}"
    ARCHIVE_DEST="$VAULT_ROOT/06_finish/$BN"
    SKIP_ARCHIVE_TO_FINISH=0
fi

echo "=============================================================================="
echo " 🔍 啟動 [Two-Pass 兩階段萃取] x [Bash 強制寫入管線]"
echo "=============================================================================="
if [[ "$SKIP_ARCHIVE_TO_FINISH" -eq 0 ]]; then
    echo "📌 脫水完成後原始長文將移至: ${ARCHIVE_DEST#$VAULT_ROOT/}"
    echo "📌 原子筆記 source 將寫為: [[$SOURCE_REL_PATH]]"
else
    echo "📌 來源已在 06_finish，不重複搬移；source: [[$SOURCE_REL_PATH]]"
fi

# ------------------------------------------------------------------------------
# 1. 物理特徵掃描 (Physical Context Extraction)
# ------------------------------------------------------------------------------

# --- 1-1. 動態自適應量測 ---
LINE_COUNT=$(wc -l < "$FILE_PATH" | xargs)
echo "📏 文本長度偵測: 共 $LINE_COUNT 行"

if [ "$LINE_COUNT" -lt 150 ]; then
    EXPECTED_NOTES="1 到 2"
elif [ "$LINE_COUNT" -lt 400 ]; then
    EXPECTED_NOTES="2 到 4"
elif [ "$LINE_COUNT" -lt 800 ]; then
    EXPECTED_NOTES="4 到 8"
elif [ "$LINE_COUNT" -lt 1200 ]; then
    EXPECTED_NOTES="6 到 12"
elif [ "$LINE_COUNT" -lt 1600 ]; then
    EXPECTED_NOTES="8 到 16"
else
    EXPECTED_NOTES="12 到 18"
fi
echo "🎯 動態拆分策略: 建議生成 $EXPECTED_NOTES 篇原子筆記"

# --- 1-2. 提取現有筆記名單 ---
echo "🔗 正在建構現有知識節點 (filename + Topic + Summary) 映射表..."
EXISTING_NOTES_CONTEXT=$(python3 "$LIB_DIR/extract_existing_notes.py" "$VAULT_ROOT" 2>/dev/null)

if [ -z "$EXISTING_NOTES_CONTEXT" ]; then
    EXISTING_NOTES_CONTEXT="(目前無現存筆記)"
fi

echo "🔗 已載入現有節點庫，準備提供關聯上下文"
echo "------------------------------------------------------------------------------"

# ------------------------------------------------------------------------------
# 2. Pass 1: Meta 規劃階段 (Planning Phase)
# ------------------------------------------------------------------------------
echo "🪜 [Pass 1] 正在進行 MECE 維度分析與歸檔規劃..."

# 模板變數替換
META_PROMPT="${PASS1_TEMPLATE//\{\{SYSTEM_RULES\}\}/$SYSTEM_RULES}"
META_PROMPT="${META_PROMPT//\{\{EXPECTED_NOTES\}\}/$EXPECTED_NOTES}"
META_PROMPT="${META_PROMPT//\{\{TOPIC_WHITELIST\}\}/$TOPIC_WHITELIST}"
META_PROMPT="${META_PROMPT//\{\{FILE_CONTENT\}\}/$FILE_CONTENT}"

# 🛡️ 終極防禦二：使用標準輸入流 (Pipe) 傳遞 Prompt
RAW_META_OUTPUT=$(echo "$META_PROMPT" | $_RUNNER \
    --provider "$PROVIDER" --bin "$LLM_BIN" --model "$SELECTED_MODEL" \
    --extra-flags "$LLM_EXTRA_FLAGS")

# 防彈級 JSON 解析
META_JSON=$(echo "$RAW_META_OUTPUT" | python3 "$LIB_DIR/parse_meta_json.py" 2>/dev/null)

if [ -z "$META_JSON" ] || ! echo "$META_JSON" | jq . >/dev/null 2>&1; then
    echo "❌ Pass 1 失敗：Meta 資料解析錯誤。模型未回傳合法 JSON，或觸發了安全攔截。"
    echo "--- 💡 診斷資訊 (模型原始輸出) ---"
    echo "$RAW_META_OUTPUT"
    echo "--------------------------------"
    exit 1
fi

NUM_NOTES=$(echo "$META_JSON" | jq '. | length')
echo "📦 規劃完成！預計生成 $NUM_NOTES 篇長青筆記。"

# --- 自動更新白名單 ---
echo "🔍 比對 Pass 1 產生的 topic 是否有新詞彙..."
SYSTEM_RULES_PATH="$SYSTEM_RULES_PATH" META_JSON_DATA="$META_JSON" python3 "$LIB_DIR/sync_topic_whitelist.py"

echo "------------------------------------------------------------------------------"

echo "⏳ [系統防護] 避免觸發嚴格限流，Pass 1 結束後強制冷卻 ${COOLDOWN_AFTER_PASS1} 秒..."
sleep "$COOLDOWN_AFTER_PASS1"

# ------------------------------------------------------------------------------
# 3. Pass 2: Content 萃取階段 (Execution Phase)
# ------------------------------------------------------------------------------

BATCH_FILES=$(echo "$META_JSON" | jq -r '.[].file_name' | paste -sd ", " -)

SAVED_REL_PATHS=()
append_saved_summary() {
    local r="${1#$VAULT_ROOT/}"
    SAVED_REL_PATHS+=("${r#02_Areas/}")
}

for (( i=0; i<$NUM_NOTES; i++ )); do
    FILE_NAME=$(echo "$META_JSON" | jq -r ".[$i].file_name")
    AREA=$(echo "$META_JSON" | jq -r ".[$i].area")

    # topic：Pass1 已正規化為 list（parse_meta_json.py），生成多行 YAML
    TOPIC_YAML=$(echo "$META_JSON" | jq -r ".[$i].topic[]?" 2>/dev/null | sed 's/^/  - /' | paste -sd $'\n' -)
    if [ -z "$TOPIC_YAML" ]; then
        TOPIC_YAML="  - (未分類)"
    fi

    # note_type：Pass1 已正規化；缺失時 parse_meta_json.py 已補 "mechanism"
    NOTE_TYPE=$(echo "$META_JSON" | jq -r ".[$i].note_type // \"mechanism\"")
    if [ -z "$NOTE_TYPE" ] || [ "$NOTE_TYPE" = "null" ]; then
        NOTE_TYPE="mechanism"
    fi

    # 載入對應 note_type 的 body 模板（找不到時 fallback 到 mechanism）
    BODY_TEMPLATE_FILE="$TEMPLATES_DIR/body_${NOTE_TYPE}.md"
    if [ ! -f "$BODY_TEMPLATE_FILE" ]; then
        echo "⚠️ 找不到 body 模板 body_${NOTE_TYPE}.md，改用 mechanism"
        BODY_TEMPLATE_FILE="$TEMPLATES_DIR/body_mechanism.md"
    fi
    BODY_TEMPLATE=$(cat "$BODY_TEMPLATE_FILE")

    KEYWORDS_RAW=$(echo "$META_JSON" | jq -c ".[$i].keywords // empty")
    if [ -n "$KEYWORDS_RAW" ] && echo "$KEYWORDS_RAW" | grep -q '^\['; then
        KEYWORDS_YAML=$(echo "$META_JSON" | jq -r ".[$i].keywords[]" | sed 's/^/  - /' | paste -sd $'\n' -)
    else
        KEYWORDS_YAML="  - (無)"
    fi

    SUMMARY=$(echo "$META_JSON" | jq -r ".[$i].summary")
    CONTENT_HINT=$(echo "$META_JSON" | jq -r ".[$i].content_hint")

    TARGET_DIR="$VAULT_ROOT/02_Areas/$AREA/Content"
    TARGET_FILE="$TARGET_DIR/${FILE_NAME}.md"

    # 排除自身，避免 AI 把當前筆記連結到自己
    BATCH_FILES_EXCL_SELF=$(echo "$META_JSON" | jq -r '.[].file_name' | grep -v "^${FILE_NAME}$" | paste -sd ", " -)

    echo "⏳ [Pass 2] 正在深度萃取 ($((i+1))/$NUM_NOTES): $FILE_NAME ..."

    mkdir -p "$TARGET_DIR"

    # 模板變數替換
    CONTENT_PROMPT="${PASS2_TEMPLATE//\{\{SYSTEM_RULES\}\}/$SYSTEM_RULES}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{CONTENT_HINT\}\}/$CONTENT_HINT}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{AREA\}\}/$AREA}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{SOURCE_REL_PATH\}\}/$SOURCE_REL_PATH}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{NOTE_TYPE\}\}/$NOTE_TYPE}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{TOPIC_YAML\}\}/$TOPIC_YAML}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{KEYWORDS_YAML\}\}/$KEYWORDS_YAML}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{SUMMARY\}\}/$SUMMARY}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{EXISTING_NOTES_CONTEXT\}\}/$EXISTING_NOTES_CONTEXT}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{BATCH_FILES\}\}/$BATCH_FILES_EXCL_SELF}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{BODY_TEMPLATE\}\}/$BODY_TEMPLATE}"
    CONTENT_PROMPT="${CONTENT_PROMPT//\{\{FILE_CONTENT\}\}/$FILE_CONTENT}"

    RAW_MD=$(echo "$CONTENT_PROMPT" | $_RUNNER \
        --provider "$PROVIDER" --bin "$LLM_BIN" --model "$SELECTED_MODEL" \
        --extra-flags "$LLM_EXTRA_FLAGS")

    if [ -z "$RAW_MD" ]; then
        echo "❌ 警告：模型沒有回傳任何內容 (可能是 API Timeout 或安全限制)。"
        echo "" > "$TARGET_FILE"
        echo "💾 已存檔至: $TARGET_FILE"
        append_saved_summary "$TARGET_FILE"
        continue
    fi

    # 🛡️ 終極防禦三：剝除外層 wrapper + 還原 ＠
    PROCESSED_MD=$(export RAW_MD_ENV="$RAW_MD"; python3 "$LIB_DIR/strip_markdown_wrapper.py" | sed 's/＠/@/g')

    if [ -z "$PROCESSED_MD" ]; then
        echo "⚠️ 警告：模型輸出格式異常 (找不到 YAML 標頭)，已強制寫入原始輸出避免資料遺失。"
        printf '%s\n' "$RAW_MD" | sed 's/＠/@/g' > "$TARGET_FILE"
    else
        echo "$PROCESSED_MD" > "$TARGET_FILE"
    fi

    python3 "$VAULT_ROOT/scripts/process_note/lib/enforce_yaml_source.py" "$TARGET_FILE" "$SOURCE_REL_PATH" "$NOTE_TYPE" "$AREA"

    echo "💾 已存檔至: $TARGET_FILE"
    append_saved_summary "$TARGET_FILE"

    echo "⏳ 暫停 ${COOLDOWN_BETWEEN_PASS2} 秒，等待 API 冷卻..."
    sleep "$COOLDOWN_BETWEEN_PASS2"
done

echo "------------------------------------------------------------------------------"

# ------------------------------------------------------------------------------
# 4. 檔案生命週期管理 (Lifecycle Management)
# ------------------------------------------------------------------------------

# --- 4-1. 原始長文歸檔至 06_finish/ ---
if [[ "${SKIP_ARCHIVE_TO_FINISH:-0}" -eq 1 ]]; then
    echo "📂 略過搬移（來源已在 06_finish）。"
elif [[ -n "${ARCHIVE_DEST:-}" ]] && [[ -f "$FILE_PATH" ]]; then
    mkdir -p "$(dirname "$ARCHIVE_DEST")"
    echo "📦 原始長文歸檔: $FILE_PATH"
    echo "        → $ARCHIVE_DEST"
    mv "$FILE_PATH" "$ARCHIVE_DEST"
    echo "✅ 已移至 06_finish（原子筆記 source 已預先指向此路徑）。"
else
    echo "⚠️ 無法歸檔：來源檔不存在或 ARCHIVE_DEST 未設定。"
fi

# --- 4-2. 雙向連結補丁 (Bidirectional Connection Patch) ---
if [ ${#SAVED_REL_PATHS[@]} -gt 0 ]; then
    echo "🔗 執行雙向連結補丁..."
    # 將相對路徑還原為絕對路徑（SAVED_REL_PATHS 是去掉 02_Areas/ 前綴的相對路徑）
    ABS_NEW_FILES=()
    for rel in "${SAVED_REL_PATHS[@]}"; do
        ABS_NEW_FILES+=("$VAULT_ROOT/02_Areas/$rel")
    done
    python3 "$LIB_DIR/patch_connections.py" "$VAULT_ROOT" "${ABS_NEW_FILES[@]}"
fi

# --- 4-3. GitHub 雲端同步 ---
echo "✅ 兩階段萃取處理完成！"
if [ ${#SAVED_REL_PATHS[@]} -gt 0 ]; then
    echo ""
    echo "📋 本次 Pass 2 寫入摘要（不含 02_Areas/ 前綴）："
    for rel in "${SAVED_REL_PATHS[@]}"; do
        echo "💾 已存檔至: $rel"
    done
    echo ""
fi
read -p "⚠️ 請檢查 Obsidian Vault。確認要同步到 GitHub 嗎？ (y/N): " confirm_sync

if [[ "$confirm_sync" =~ ^[Yy]$ ]]; then
    echo "🚀 啟動同步至 GitHub..."
    FILENAME=$(basename "$FILE_PATH")
    CURRENT_DATE=$(date +"%Y-%m-%d")

    sed -i '' "s/\*Last Updated: .*\*/\*Last Updated: $CURRENT_DATE\*/" "$VAULT_ROOT/README.md" 2>/dev/null

    git -C "$VAULT_ROOT" add .
    git -C "$VAULT_ROOT" commit -m "Auto-process note (Two-Pass Plan B): $FILENAME"
    git -C "$VAULT_ROOT" push
    echo "✨ 同步完成！"
else
    echo "🛑 已跳過 GitHub 同步。"
fi
