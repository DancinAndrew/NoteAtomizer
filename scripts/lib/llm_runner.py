#!/usr/bin/env python3
"""
統一 LLM CLI 包裝層（Gemini CLI ↔ Claude Code 雙 provider 支援）。

兩種使用方式：

1. Python import（供 keyword_moc_builder 等 Python 腳本使用）：
   from llm_runner import run_llm

2. CLI stdin→stdout（供 bash 腳本使用）：
   echo "$PROMPT" | python3 scripts/lib/llm_runner.py \\
       --provider gemini \\
       --bin /opt/homebrew/bin/gemini \\
       --model gemini-3.1-pro-preview \\
       [--timeout 600] \\
       [--extra-flags "--max-turns 1"]

CLI 成功時 exit 0，輸出寫 stdout；失敗時 exit 1，診斷訊息寫 stderr。

支援的 provider：
  gemini  — echo "$PROMPT" | <bin> --model <model>
  claude  — echo "$PROMPT" | <bin> -p --model <model> [extra_flags...]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 配額錯誤特徵（用於 retry 判斷）
# ---------------------------------------------------------------------------
_GEMINI_QUOTA_PATTERNS = [
    "exhausted your capacity",
    "quota",
    "AbortError",
    "429",
    "rate limit",
    "RESOURCE_EXHAUSTED",
]

_CLAUDE_QUOTA_PATTERNS = [
    "rate_limit",
    "rate limit",
    "429",
    "overloaded",
    "529",
    "too many requests",
]

_GEMINI_STDERR_NOISE = re.compile(
    r"GaxiosError|Attempt.*failed|Keychain|Require stack|FileKeychain|"
    r"Loaded cached|Using FileKeychain|_GaxiosError|at Gaxios|at process|"
    r"at async|config:|response:|headers:|responseURL|data:"
)


def _is_quota_error(provider: str, stderr_text: str) -> bool:
    text = stderr_text.lower()
    patterns = _GEMINI_QUOTA_PATTERNS if provider == "gemini" else _CLAUDE_QUOTA_PATTERNS
    return any(p.lower() in text for p in patterns)


def _clean_stderr(provider: str, stderr_text: str) -> str:
    if provider == "gemini":
        lines = [l for l in stderr_text.splitlines() if not _GEMINI_STDERR_NOISE.search(l)]
        return "\n".join(lines)
    return stderr_text


# ---------------------------------------------------------------------------
# 核心函式
# ---------------------------------------------------------------------------

def run_llm(
    prompt: str,
    *,
    provider: str,
    bin_path: str,
    model: str,
    timeout: int = 600,
    extra_flags: str = "",
    max_retries: int = 5,
    retry_sleep: int = 120,
) -> str:
    """
    送 prompt 給指定 LLM CLI，回傳模型輸出字串。

    失敗時 raise RuntimeError。
    遇到配額 / rate-limit 錯誤時自動 retry（最多 max_retries 次）。

    注意：@ 遮蔽（@→＠）應由呼叫端在使用者內容上做好再傳入；
    本函式不修改 prompt 內容，以保留意圖性的 @pdf_path。
    """
    if not bin_path or not Path(bin_path).is_file():
        raise FileNotFoundError(
            f"找不到 {provider} CLI 執行檔: {bin_path!r}\n"
            f"請安裝並設定 scripts/config.yaml 的 {'gemini' if provider == 'gemini' else 'claude'}.bin"
        )

    # 組合 CLI 命令
    if provider == "gemini":
        cmd = [bin_path, "--model", model]
    elif provider == "claude":
        cmd = [bin_path, "-p", "--model", model]
        if extra_flags:
            cmd.extend(extra_flags.split())
    else:
        raise ValueError(f"不支援的 provider: {provider!r}（可選 'gemini' | 'claude'）")

    env = os.environ.copy()
    env.setdefault("LANG", "en_US.UTF-8")
    env.setdefault("LC_ALL", "en_US.UTF-8")

    last_err = ""
    for attempt in range(1, max_retries + 1):
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到可執行檔: {bin_path}")
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"{provider} CLI 逾時（{timeout}s）")

        if proc.returncode == 0:
            return proc.stdout or ""

        stderr = (proc.stderr or "").strip()
        last_err = _clean_stderr(provider, stderr)

        print(
            f"[llm_runner] {provider} CLI 第 {attempt}/{max_retries} 次失敗 (exit {proc.returncode})",
            file=sys.stderr,
        )

        if attempt < max_retries and _is_quota_error(provider, stderr):
            print(f"[llm_runner] 配額/限流，{retry_sleep}s 後重試…", file=sys.stderr)
            time.sleep(retry_sleep)
            continue

        if last_err:
            print(f"[llm_runner] stderr:\n{last_err[:2000]}", file=sys.stderr)
        raise RuntimeError(f"{provider} CLI 失敗（exit {proc.returncode}）")

    raise RuntimeError(f"{provider} CLI 重試 {max_retries} 次後仍失敗")


# ---------------------------------------------------------------------------
# CLI 介面（供 bash 腳本使用）
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> Any:
    p = argparse.ArgumentParser(
        description="統一 LLM CLI 包裝：stdin 讀 prompt，stdout 輸出回應",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  echo "你好" | python3 llm_runner.py --provider gemini --bin /opt/homebrew/bin/gemini --model gemini-3.1-pro-preview
  echo "你好" | python3 llm_runner.py --provider claude --bin /opt/homebrew/bin/claude --model claude-opus-4-7 --extra-flags "--max-turns 1"
""",
    )
    p.add_argument("--provider", required=True, choices=["gemini", "claude"])
    p.add_argument("--bin", required=True, dest="bin_path", metavar="PATH")
    p.add_argument("--model", required=True)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--extra-flags", default="", dest="extra_flags")
    p.add_argument("--max-retries", type=int, default=5, dest="max_retries")
    p.add_argument("--retry-sleep", type=int, default=120, dest="retry_sleep")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    prompt = sys.stdin.read()
    if not prompt:
        print("[llm_runner] stdin 為空，沒有 prompt 可送出", file=sys.stderr)
        return 1
    try:
        output = run_llm(
            prompt,
            provider=args.provider,
            bin_path=args.bin_path,
            model=args.model,
            timeout=args.timeout,
            extra_flags=args.extra_flags,
            max_retries=args.max_retries,
            retry_sleep=args.retry_sleep,
        )
        sys.stdout.write(output)
        return 0
    except (FileNotFoundError, TimeoutError, RuntimeError, ValueError) as e:
        print(f"[llm_runner] 錯誤: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
