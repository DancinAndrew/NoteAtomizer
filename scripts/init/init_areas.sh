#!/bin/bash

# ==============================================================================
# 02_Areas 領域資料夾初始化
# 讀取 scripts/init/areas.txt，在 02_Areas/ 建立對應的 <NAME>/Content/ 結構
# 請先跑 init_vault.sh，再填好 areas.txt，最後執行此腳本
# ==============================================================================

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.yaml"
AREAS_FILE="$SCRIPT_DIR/areas.txt"

VAULT_ROOT=$(python3 "$SCRIPT_DIR/../lib/pipeline_config.py" "$CONFIG" global vault_root)

if [ -z "$VAULT_ROOT" ]; then
    echo "❌ 無法從 scripts/config.yaml 取得 vault_root，請確認設定正確。"
    exit 1
fi

if [ ! -d "$VAULT_ROOT/02_Areas" ]; then
    echo "❌ 找不到 $VAULT_ROOT/02_Areas"
    echo "   請先執行 bash scripts/init/init_vault.sh"
    exit 1
fi

if [ ! -f "$AREAS_FILE" ]; then
    echo "❌ 找不到 scripts/init/areas.txt"
    echo "   請先執行 bash scripts/init/init_vault.sh，再填寫 areas.txt"
    exit 1
fi

echo "Vault：$VAULT_ROOT"
echo "---"

created=0
skipped=0

while IFS= read -r line; do
    # 去掉前後空白
    name="${line#"${line%%[![:space:]]*}"}"
    name="${name%"${name##*[![:space:]]}"}"

    # 跳過空行與註解行
    [[ -z "$name" || "$name" == \#* ]] && continue

    TARGET="$VAULT_ROOT/02_Areas/$name/Content"
    if [ -d "$TARGET" ]; then
        echo "· exists  02_Areas/$name/Content"
        ((skipped++))
    else
        mkdir -p "$TARGET"
        echo "✓ created 02_Areas/$name/Content"
        ((created++))
    fi
done < "$AREAS_FILE"

echo "---"

if [ $((created + skipped)) -eq 0 ]; then
    echo "⚠️  areas.txt 內沒有有效的領域項目。"
    echo "   請編輯 scripts/init/areas.txt 後重新執行。"
    exit 1
fi

echo "完成：建立 $created 個，已存在跳過 $skipped 個。"
