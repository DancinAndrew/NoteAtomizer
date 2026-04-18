#!/bin/bash

# ==============================================================================
# Course Note Engine: 兩階段課程筆記自動化
# Step 1: 產出時間軸大綱 (JSON) -> Step 2: 逐段深度筆記 -> Bash append 寫入
# ==============================================================================

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# --- 核心變數（從 scripts/config.yaml 讀取）---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"

_CONFIG="$SCRIPT_DIR/../config.yaml"
_CFG="python3 $SCRIPT_DIR/../lib/pipeline_config.py $_CONFIG"
_RUNNER="python3 $SCRIPT_DIR/../lib/llm_runner.py"

PROVIDER=$($_CFG course_note provider)
LLM_BIN=$($_CFG course_note llm_bin)
SELECTED_MODEL=$($_CFG course_note llm_model)
FALLBACK_MODEL=$($_CFG course_note llm_fallback_model)
LLM_EXTRA_FLAGS=$($_CFG course_note llm_extra_flags)
COOLDOWN_AFTER_STEP1=$($_CFG course_note cooldown_after_step1)
COOLDOWN_BETWEEN_STEP2=$($_CFG course_note cooldown_between_step2)
RETRY_COOLDOWN=$($_CFG course_note retry_cooldown)

# --- 用法說明 ---
usage() {
    echo "用法: $0 <逐字稿路徑> [PDF路徑]"
    echo ""
    echo "範例:"
    echo "  $0 /path/to/07_temp/Security_Class_01/transcript.md"
    echo "  $0 /path/to/07_temp/Security_Class_01/transcript.md /path/to/07_temp/Security_Class_01/slides.pdf"
    echo ""
    echo "輸出會寫入逐字稿所在資料夾的 note.md"
    exit 1
}

# --- 參數檢查 ---
if [ -z "$1" ]; then
    echo "❌ 錯誤：請提供逐字稿的路徑"
    usage
fi

TRANSCRIPT_PATH="$1"
PDF_PATH="${2:-}"

if [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo "❌ 錯誤：找不到逐字稿 $TRANSCRIPT_PATH"
    exit 1
fi

if [ -n "$PDF_PATH" ] && [ ! -f "$PDF_PATH" ]; then
    echo "❌ 錯誤：找不到 PDF $PDF_PATH"
    exit 1
fi

# prompt 模板檢查
for tmpl in base_prompt.txt step1_prompt.txt step2_prompt.txt; do
    if [ ! -f "$PROMPTS_DIR/$tmpl" ]; then
        echo "❌ 錯誤：找不到 prompt 模板 $PROMPTS_DIR/$tmpl"
        exit 1
    fi
done

# --- 路徑推算 ---
WORK_DIR="$(cd "$(dirname "$TRANSCRIPT_PATH")" && pwd)"
FOLDER_NAME="$(basename "$WORK_DIR")"
OUTPUT_FILE="$WORK_DIR/note.md"

echo "=============================================================================="
echo " 📚 啟動 Course Note Engine (兩階段課程筆記自動化)"
echo "=============================================================================="
echo "📂 工作目錄: $WORK_DIR"
echo "📝 逐字稿:   $TRANSCRIPT_PATH"
if [ -n "$PDF_PATH" ]; then
    echo "📄 PDF 講義: $PDF_PATH"
else
    echo "📄 PDF 講義: (無)"
fi
echo "💾 輸出檔案: $OUTPUT_FILE"
echo "------------------------------------------------------------------------------"

# --- 讀取模板 ---
BASE_PROMPT=$(cat "$PROMPTS_DIR/base_prompt.txt")
STEP1_TEMPLATE=$(cat "$PROMPTS_DIR/step1_prompt.txt")
STEP2_TEMPLATE=$(cat "$PROMPTS_DIR/step2_prompt.txt")

# 巨集遮蔽：防止 gemini-cli 觸發 @ 檔案路徑解析
TRANSCRIPT_CONTENT=$(cat "$TRANSCRIPT_PATH" | sed 's/@/＠/g')

# ==============================================================================
# Step 1: 產出時間軸大綱
# ==============================================================================
echo ""
echo "🪜 [Step 1] 正在分析課程內容，產出時間軸大綱..."

# 將逐字稿注入 step1 模板
STEP1_PROMPT="${STEP1_TEMPLATE//\{\{TRANSCRIPT\}\}/$TRANSCRIPT_CONTENT}"

# 組合完整 prompt：base + step1
FULL_STEP1_PROMPT="${BASE_PROMPT}

${STEP1_PROMPT}"

# 若有 PDF，在 prompt 前面加上 PDF 引用指示
if [ -n "$PDF_PATH" ]; then
    PDF_INSTRUCTION="以下是課程的 PDF 講義，請一併參考：
@${PDF_PATH}

"
    FULL_STEP1_PROMPT="${PDF_INSTRUCTION}${FULL_STEP1_PROMPT}"
fi

# 呼叫 LLM CLI（主模型 → 失敗時自動切換備援模型）
RAW_STEP1_OUTPUT=$(echo "$FULL_STEP1_PROMPT" | $_RUNNER \
    --provider "$PROVIDER" --bin "$LLM_BIN" --model "$SELECTED_MODEL" \
    --extra-flags "$LLM_EXTRA_FLAGS")
if [ -z "$RAW_STEP1_OUTPUT" ] && [ -n "$FALLBACK_MODEL" ]; then
    echo "⚠️  主模型無回應，切換備援模型 $FALLBACK_MODEL ..."
    RAW_STEP1_OUTPUT=$(echo "$FULL_STEP1_PROMPT" | $_RUNNER \
        --provider "$PROVIDER" --bin "$LLM_BIN" --model "$FALLBACK_MODEL" \
        --extra-flags "$LLM_EXTRA_FLAGS")
fi

# 防彈 JSON 解析
OUTLINE_JSON=$(python3 -c "
import sys, json
text = sys.stdin.read()
start = text.find('[')
end = text.rfind(']')
if start != -1 and end != -1:
    json_str = text[start:end+1]
    try:
        data = json.loads(json_str)
        # 驗證結構
        for item in data:
            assert 'title' in item and 'time_range' in item
        print(json_str)
    except Exception:
        sys.exit(1)
else:
    sys.exit(1)
" <<< "$RAW_STEP1_OUTPUT" 2>/dev/null)

if [ -z "$OUTLINE_JSON" ] || ! echo "$OUTLINE_JSON" | jq . >/dev/null 2>&1; then
    echo "❌ Step 1 失敗：無法解析大綱 JSON"
    echo "--- 💡 診斷資訊 (模型原始輸出) ---"
    echo "$RAW_STEP1_OUTPUT"
    echo "-----------------------------------"
    exit 1
fi

NUM_SECTIONS=$(echo "$OUTLINE_JSON" | jq '. | length')
echo "📦 大綱產出完成！共 $NUM_SECTIONS 個段落："
echo ""

# 顯示大綱
for (( i=0; i<$NUM_SECTIONS; i++ )); do
    TITLE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].title")
    TIME_RANGE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].time_range")
    echo "  $((i+1)). [$TIME_RANGE] $TITLE"
done

echo ""
echo "⏳ [系統防護] Step 1 結束後冷卻 ${COOLDOWN_AFTER_STEP1} 秒..."
sleep "$COOLDOWN_AFTER_STEP1"

# ==============================================================================
# Step 2: 逐段產出深度筆記
# ==============================================================================

# 構建可讀的完整大綱文字（給 Step 2 當上下文）
OUTLINE_TEXT=""
for (( i=0; i<$NUM_SECTIONS; i++ )); do
    TITLE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].title")
    TIME_RANGE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].time_range")
    OUTLINE_TEXT="${OUTLINE_TEXT}$((i+1)). [$TIME_RANGE] $TITLE
"
done

# 清空/建立輸出檔，先寫入 metadata header
CURRENT_DATE=$(date +"%Y-%m-%d")
cat > "$OUTPUT_FILE" <<HEADER
---
title: "${FOLDER_NAME} 課程筆記"
date: ${CURRENT_DATE}
transcript: "$(basename "$TRANSCRIPT_PATH")"
pdf: "$([ -n "$PDF_PATH" ] && basename "$PDF_PATH" || echo '無')"
---

HEADER

echo "------------------------------------------------------------------------------"

for (( i=0; i<$NUM_SECTIONS; i++ )); do
    SECTION_TITLE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].title")
    SECTION_TIME_RANGE=$(echo "$OUTLINE_JSON" | jq -r ".[$i].time_range")

    echo ""
    echo "⏳ [Step 2] 正在產出 ($((i+1))/$NUM_SECTIONS): [$SECTION_TIME_RANGE] $SECTION_TITLE ..."

    # 注入變數到 step2 模板
    STEP2_PROMPT="${STEP2_TEMPLATE//\{\{SECTION_TITLE\}\}/$SECTION_TITLE}"
    STEP2_PROMPT="${STEP2_PROMPT//\{\{SECTION_TIME_RANGE\}\}/$SECTION_TIME_RANGE}"
    STEP2_PROMPT="${STEP2_PROMPT//\{\{FULL_OUTLINE\}\}/$OUTLINE_TEXT}"
    STEP2_PROMPT="${STEP2_PROMPT//\{\{TRANSCRIPT\}\}/$TRANSCRIPT_CONTENT}"

    FULL_STEP2_PROMPT="${BASE_PROMPT}

${STEP2_PROMPT}"

    if [ -n "$PDF_PATH" ]; then
        PDF_INSTRUCTION="以下是課程的 PDF 講義，請一併參考：
@${PDF_PATH}

"
        FULL_STEP2_PROMPT="${PDF_INSTRUCTION}${FULL_STEP2_PROMPT}"
    fi

    # 呼叫 LLM CLI（主模型 → 失敗時切換備援模型）
    RAW_STEP2_OUTPUT=$(echo "$FULL_STEP2_PROMPT" | $_RUNNER \
        --provider "$PROVIDER" --bin "$LLM_BIN" --model "$SELECTED_MODEL" \
        --extra-flags "$LLM_EXTRA_FLAGS")

    if [ -z "$RAW_STEP2_OUTPUT" ] && [ -n "$FALLBACK_MODEL" ]; then
        echo "⚠️  主模型無回應，冷卻 ${RETRY_COOLDOWN} 秒後切換備援模型 $FALLBACK_MODEL ..."
        sleep "$RETRY_COOLDOWN"
        RAW_STEP2_OUTPUT=$(echo "$FULL_STEP2_PROMPT" | $_RUNNER \
            --provider "$PROVIDER" --bin "$LLM_BIN" --model "$FALLBACK_MODEL" \
            --extra-flags "$LLM_EXTRA_FLAGS")
    fi

    if [ -z "$RAW_STEP2_OUTPUT" ]; then
        echo "❌ 警告：段落 [$SECTION_TITLE] 產出失敗（已重試），跳過此段落"
        echo "" >> "$OUTPUT_FILE"
        echo "<!-- ❌ 段落產出失敗: [$SECTION_TIME_RANGE] $SECTION_TITLE -->" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        continue
    fi

    # 清理輸出：剝除最外層 code block wrapper，還原 ＠ 為 @
    CLEANED_MD=$(export RAW_MD_ENV="$RAW_STEP2_OUTPUT"; python3 <<'PYEOF' | python3 "$SCRIPT_DIR/lib/strip_font_backticks.py" | sed 's/＠/@/g'
import os
lines = os.environ.get('RAW_MD_ENV', '').splitlines()
# 剝除最外層 Markdown code block wrapper
if lines and lines[0].strip().startswith('```'):
    lines = lines[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
# 移除開頭空行
while lines and lines[0].strip() == '':
    lines = lines[1:]
print('\n'.join(lines))
PYEOF
)

    if [ -z "$CLEANED_MD" ]; then
        echo "⚠️  警告：清理後內容為空，寫入原始輸出"
        printf '%s\n' "$RAW_STEP2_OUTPUT" | sed 's/＠/@/g' >> "$OUTPUT_FILE"
    else
        printf '%s\n' "$CLEANED_MD" >> "$OUTPUT_FILE"
    fi

    # 段落間分隔（非最後一段才加）
    if [ $i -lt $((NUM_SECTIONS - 1)) ]; then
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi

    echo "✅ 段落 $((i+1))/$NUM_SECTIONS 已寫入"

    # 段落間冷卻（非最後一段才等）
    if [ $i -lt $((NUM_SECTIONS - 1)) ]; then
        echo "⏳ 冷卻 ${COOLDOWN_BETWEEN_STEP2} 秒..."
        sleep "$COOLDOWN_BETWEEN_STEP2"
    fi
done

echo ""
echo "=============================================================================="
echo "✅ 課程筆記產出完成！"
echo "💾 檔案位置: $OUTPUT_FILE"
echo "📊 共處理 $NUM_SECTIONS 個段落"
echo "=============================================================================="
