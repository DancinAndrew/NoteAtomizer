# `course_note/lib/` — 課程筆記輔助腳本

## 目的

提供 **Step 2** 模型輸出後的輕量文字清理，供 [`../process_course.sh`](../process_course.sh) 以 **stdin/stdout** 串接使用。

## 檔案說明

| 檔案 | 職責 |
|------|------|
| [`strip_font_backticks.py`](strip_font_backticks.py) | 移除誤加在 `<font color="...">...</font>` 外層的 Markdown **行內反引號**（`` ` ``），避免顯示異常；以 regex 反覆替換直到穩定 |

## 呼叫方式

腳本中為：先以內嵌 Python 剝除最外層 Markdown 程式碼區塊，再 **pipe** 進本工具：

```bash
... | python3 "$SCRIPT_DIR/lib/strip_font_backticks.py" | sed 's/＠/@/g'
```

## 與其他資料夾的關係

- 主流程：[`../README.md`](../README.md)
