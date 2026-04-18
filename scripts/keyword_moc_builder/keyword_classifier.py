"""
LLM-agnostic keyword classifier：送 unique keywords + 使用者需求，
一次呼叫回傳分組 JSON。支援 Gemini CLI 與 Claude Code。

底層透過 scripts/lib/llm_runner.py 呼叫，provider 由呼叫端傳入。

回傳 JSON 結構：
  {
    "moc_title": "Backend_Interview",
    "groups": {
      "Flask": ["Flask", "Jinja2", "Werkzeug"],
      "PostgreSQL": ["PostgreSQL", "SQL", "ACID"]
    }
  }
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# llm_runner 在 scripts/lib/，動態加入路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from llm_runner import run_llm  # noqa: E402

DEFAULT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_GEMINI_BIN = "/opt/homebrew/bin/gemini"
DEFAULT_CLAUDE_BIN = "/opt/homebrew/bin/claude"


def mask_at_for_cli(s: str) -> str:
    """半形 @ → 全形 ＠，避免 CLI 路徑注入解析。"""
    return s.replace("@", "＠")


def _extract_json_object(raw: str) -> str:
    """從 CLI stdout 提取第一個 {...} 區段。"""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```\s*$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("stdout 中找不到 JSON object")
    return raw[start : end + 1]


def classify_keywords_by_request(
    user_request: str,
    keywords: list[str],
    *,
    provider: str,
    bin_path: str,
    model: str,
    extra_flags: str = "",
    timeout: int = 600,
) -> dict[str, Any]:
    """
    送 user_request + keywords 給指定 LLM，回傳 {moc_title, groups}。

    groups: { "分類名稱": ["keyword1", "keyword2", ...], ... }
    moc_title: 根據需求自動命名（英文底線，用於檔名）
    """
    if not keywords:
        return {"moc_title": "Custom_MOC", "groups": {}}

    kw_list = "\n".join(f"- {k}" for k in keywords)
    prompt = f"""You are a PKM (Personal Knowledge Management) assistant helping a user prepare study materials.

## User's request
{user_request}

## Available keywords (from note metadata in the vault)
{kw_list}

## Your task
1. From the keyword list above, identify ALL keywords that are relevant to the user's request.
2. Group those relevant keywords into logical topic clusters (e.g. "Flask", "PostgreSQL", "RESTful API").
   - Group names should be concise and descriptive (2-4 words max).
   - A keyword may appear in at most ONE group (choose the most relevant one).
   - Discard keywords that are not relevant to the user's request.
3. Generate a short MOC title (English, underscores, no spaces) that summarizes the user's goal.
   Example: if the user wants to review Flask and PostgreSQL for a backend interview → "Backend_Interview"

## Output format
Output ONLY a valid JSON object. No markdown fences. No explanation. Start with {{ and end with }}.

{{
  "moc_title": "<short_title_with_underscores>",
  "groups": {{
    "<Group Name 1>": ["keyword_a", "keyword_b"],
    "<Group Name 2>": ["keyword_c", "keyword_d"]
  }}
}}
"""
    prompt = mask_at_for_cli(prompt)

    raw_out = run_llm(
        prompt,
        provider=provider,
        bin_path=bin_path,
        model=model,
        timeout=timeout,
        extra_flags=extra_flags,
    )

    try:
        json_str = _extract_json_object(raw_out)
        result = json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"無法從 CLI 輸出解析 JSON object:\n{raw_out[:2500]}", file=sys.stderr)
        raise RuntimeError("invalid JSON from LLM CLI") from e

    if not isinstance(result.get("groups"), dict):
        raise RuntimeError(f"回傳 JSON 缺少 'groups' 欄位: {json_str[:500]}")

    if not result.get("moc_title", "").strip():
        result["moc_title"] = "Custom_MOC"

    return result


def offline_classify_guess(user_request: str, keywords: list[str]) -> dict[str, Any]:
    """
    --offline 模式：不呼叫任何 LLM，
    用陽春關鍵字比對直接把符合的 keyword 塞進一個「All」分組，用於測試流程。
    """
    words = re.findall(r"\w+", user_request.lower())
    matched = [k for k in keywords if any(w in k.lower() for w in words)]
    if not matched:
        matched = keywords[:10]
    return {
        "moc_title": "Offline_Test",
        "groups": {"All (offline mode)": matched},
    }
