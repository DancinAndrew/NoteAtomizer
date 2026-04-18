#!/bin/bash

# ==============================================================================
# Vault 初始化：建立 PARA 分層資料夾結構
# 執行後請編輯 scripts/init/areas.txt，再跑 init_areas.sh
# ==============================================================================

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.yaml"

VAULT_ROOT=$(python3 "$SCRIPT_DIR/../lib/pipeline_config.py" "$CONFIG" global vault_root)

if [ -z "$VAULT_ROOT" ]; then
    echo "❌ 無法從 scripts/config.yaml 取得 vault_root，請確認設定正確。"
    exit 1
fi

if [ ! -d "$VAULT_ROOT" ]; then
    echo "❌ Vault 目錄不存在：$VAULT_ROOT"
    echo "   請先建立該目錄，或在 scripts/config.yaml 修改 vault_root。"
    exit 1
fi

echo "Vault：$VAULT_ROOT"
echo "---"

_mkdir() {
    local DIR="$VAULT_ROOT/$1"
    if [ -d "$DIR" ]; then
        echo "· exists  $1"
    else
        mkdir -p "$DIR"
        echo "✓ created $1"
    fi
}

_mkdir "01_Projects"
_mkdir "02_Areas/00_MOC_MAP"
_mkdir "03_Resources"
_mkdir "04_Archive"
_mkdir "05_Journal"
_mkdir "06_finish"
_mkdir "07_temp"
_mkdir "98 Books"
_mkdir "99_Attachments"

echo "---"

AREAS_FILE="$SCRIPT_DIR/areas.txt"
if [ -f "$AREAS_FILE" ]; then
    echo "· exists  scripts/init/areas.txt（已有，不覆蓋）"
else
    cat > "$AREAS_FILE" <<'EOF'
# 在下方列出你要在 02_Areas/ 建立的領域資料夾。
# 規則：
#   - 每行一個領域名稱
#   - 建議採 NN_Name 格式（例：01_Machine_Learning）
#   - 以 # 開頭的行會被忽略
#   - 空行會被忽略
#   - 會自動在每個領域下建立 Content/ 子資料夾
#
# 填寫範例（把 # 拿掉即可生效）：
# 01_Machine_Learning
# 02_Software_Engineering
# 03_System_Design
EOF
    echo "✓ created scripts/init/areas.txt"
fi

echo ""
echo "下一步："
echo "  1. 編輯 scripts/init/areas.txt，填入你要建立的 02_Areas 領域"
echo "  2. 執行 bash scripts/init/init_areas.sh"
