#!/usr/bin/env python3
"""
Pipeline 設定載入器（供 bash 腳本與 Python 工具共用）。

CLI 用法（供 bash eval）：
  python3 scripts/lib/pipeline_config.py <config_path> <pipeline> <key>

  pipeline: process_note | course_note | keyword_moc | global
  key:
    vault_root | gemini_bin | model | fallback_model |
    cooldown_after_pass1 | cooldown_between_pass2 |
    cooldown_after_step1 | cooldown_between_step2 | retry_cooldown |
    provider | llm_bin | llm_model | llm_fallback_model | llm_extra_flags

範例：
  VAULT_ROOT=$(python3 scripts/lib/pipeline_config.py scripts/config.yaml global vault_root)
  PROVIDER=$(python3 scripts/lib/pipeline_config.py scripts/config.yaml process_note provider)
  LLM_BIN=$(python3 scripts/lib/pipeline_config.py scripts/config.yaml process_note llm_bin)
  MODEL=$(python3 scripts/lib/pipeline_config.py scripts/config.yaml process_note llm_model)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# 內部常數
# ---------------------------------------------------------------------------
_DEFAULT_GEMINI_CANDIDATES = [
    "/opt/homebrew/bin/gemini",
    "/usr/local/bin/gemini",
]

_DEFAULT_CLAUDE_CANDIDATES = [
    "/opt/homebrew/bin/claude",
    "/usr/local/bin/claude",
]


# ---------------------------------------------------------------------------
# 載入與解析
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_vault_root(config_path: Path, cfg: dict[str, Any]) -> Path:
    """vault_root 解析：設定值優先，留空則從 config 位置上兩層推導。"""
    vr = (cfg.get("vault_root") or "").strip()
    if vr:
        return Path(vr).expanduser().resolve()
    # scripts/config.yaml → scripts/ → vault root
    return config_path.resolve().parent.parent.resolve()


def resolve_gemini_bin(cfg: dict[str, Any]) -> str:
    """向後相容：依序尋找可用的 gemini CLI 執行檔。"""
    return resolve_llm_bin(cfg, "gemini")


def resolve_llm_bin(cfg: dict[str, Any], provider: str) -> str:
    """依 provider 找到對應的 CLI 執行檔路徑。"""
    if provider == "gemini":
        g = cfg.get("gemini") if isinstance(cfg.get("gemini"), dict) else {}
        candidate = (g.get("bin") or "").strip()
        if candidate and Path(candidate).is_file():
            return candidate
        for c in _DEFAULT_GEMINI_CANDIDATES:
            if Path(c).is_file():
                return c
        found = shutil.which("gemini")
        return found or ""
    elif provider == "claude":
        c_cfg = cfg.get("claude") if isinstance(cfg.get("claude"), dict) else {}
        candidate = (c_cfg.get("bin") or "").strip()
        if candidate and Path(candidate).is_file():
            return candidate
        for c in _DEFAULT_CLAUDE_CANDIDATES:
            if Path(c).is_file():
                return c
        found = shutil.which("claude")
        return found or ""
    return ""


def resolve_provider(cfg: dict[str, Any], pipeline: str) -> str:
    """解析 LLM 供應商：管線 provider → 全域 llm.provider → 'gemini'。"""
    p = cfg.get(pipeline) if isinstance(cfg.get(pipeline), dict) else {}
    pipeline_provider = (p.get("provider") or "").strip() if p else ""
    if pipeline_provider:
        return pipeline_provider
    llm_cfg = cfg.get("llm") if isinstance(cfg.get("llm"), dict) else {}
    global_provider = (llm_cfg.get("provider") or "").strip() if llm_cfg else ""
    return global_provider or "gemini"


def resolve_model(cfg: dict[str, Any], pipeline: str) -> str:
    """向後相容：解析模型（固定用 gemini provider）。"""
    return resolve_llm_model(cfg, pipeline, resolve_provider(cfg, pipeline))


def resolve_llm_model(cfg: dict[str, Any], pipeline: str, provider: str) -> str:
    """解析 LLM 模型：管線專用 model → provider 全域 model。"""
    p = cfg.get(pipeline) if isinstance(cfg.get(pipeline), dict) else {}
    pipeline_model = (p.get("model") or "").strip() if p else ""
    if pipeline_model:
        return pipeline_model
    provider_cfg = cfg.get(provider) if isinstance(cfg.get(provider), dict) else {}
    return (provider_cfg.get("model") or "").strip() if provider_cfg else ""


def resolve_fallback_model(cfg: dict[str, Any], pipeline: str) -> str:
    """向後相容：解析備援模型。"""
    return resolve_llm_fallback_model(cfg, pipeline, resolve_provider(cfg, pipeline))


def resolve_llm_fallback_model(cfg: dict[str, Any], pipeline: str, provider: str) -> str:
    """解析備援模型：管線專用 fallback_model → provider 全域 fallback_model。"""
    p = cfg.get(pipeline) if isinstance(cfg.get(pipeline), dict) else {}
    pipeline_fb = (p.get("fallback_model") or "").strip() if p else ""
    if pipeline_fb:
        return pipeline_fb
    provider_cfg = cfg.get(provider) if isinstance(cfg.get(provider), dict) else {}
    return (provider_cfg.get("fallback_model") or "").strip() if provider_cfg else ""


def resolve_llm_extra_flags(cfg: dict[str, Any], provider: str) -> str:
    """解析 provider 專用的額外 CLI 旗標（目前只有 claude 用到）。"""
    provider_cfg = cfg.get(provider) if isinstance(cfg.get(provider), dict) else {}
    return (provider_cfg.get("extra_flags") or "").strip() if provider_cfg else ""


def _int(val: Any, default: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def resolve_cooldowns(cfg: dict[str, Any], pipeline: str) -> dict[str, int]:
    """回傳各 cooldown 秒數（pipeline 區塊優先，缺失則用下方預設）。"""
    p = cfg.get(pipeline) if isinstance(cfg.get(pipeline), dict) else {}

    if pipeline == "process_note":
        return {
            "cooldown_after_pass1": _int(p.get("cooldown_after_pass1"), 30),
            "cooldown_between_pass2": _int(p.get("cooldown_between_pass2"), 10),
        }
    if pipeline == "course_note":
        return {
            "cooldown_after_step1": _int(p.get("cooldown_after_step1"), 30),
            "cooldown_between_step2": _int(p.get("cooldown_between_step2"), 15),
            "retry_cooldown": _int(p.get("retry_cooldown"), 60),
        }
    return {}


# ---------------------------------------------------------------------------
# keyword_moc 相容性展開（供 build_keyword_mocs.py 使用）
# ---------------------------------------------------------------------------

def expand_for_keyword_moc(config_path: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """
    將頂層 pipeline config 轉換成 build_keyword_mocs.py 期望的格式：
      { provider, llm: {bin, model, extra_flags}, gemini: {...}, claude: {...},
        vault_root, output_dir, scan_roots, ... }

    若 cfg 不含 keyword_moc 鍵（舊格式 config.yaml），原樣回傳不做轉換。
    """
    if "keyword_moc" not in cfg:
        return cfg  # 舊格式，直接沿用

    km = cfg["keyword_moc"] if isinstance(cfg.get("keyword_moc"), dict) else {}
    vault = str(resolve_vault_root(config_path, cfg))

    provider = resolve_provider(cfg, "keyword_moc")
    model = resolve_llm_model(cfg, "keyword_moc", provider)
    llm_bin = resolve_llm_bin(cfg, provider)
    fallback_model = resolve_llm_fallback_model(cfg, "keyword_moc", provider)
    extra_flags = resolve_llm_extra_flags(cfg, provider)

    return {
        "provider": provider,
        "llm": {
            "bin": llm_bin,
            "model": model,
            "fallback_model": fallback_model,
            "extra_flags": extra_flags,
        },
        # 保留原始 provider 區塊供 resolve_llm_bin 等函式使用
        "gemini": cfg.get("gemini") or {},
        "claude": cfg.get("claude") or {},
        "vault_root": vault,
        "output_dir": km.get("output_dir", "02_Areas/00_MOC_MAP"),
        "scan_roots": km.get("scan_roots", ["02_Areas"]),
        "exclude_path_substrings": km.get("exclude_path_substrings", []),
    }


# ---------------------------------------------------------------------------
# CLI 介面（供 bash 腳本讀取單一值）
# ---------------------------------------------------------------------------

def _cli() -> None:
    if len(sys.argv) < 4:
        print(
            "用法: pipeline_config.py <config_path> <pipeline> <key>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = Path(sys.argv[1])
    pipeline = sys.argv[2]
    key = sys.argv[3]

    if not config_path.is_file():
        print(f"找不到設定檔: {config_path}", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(config_path)
    provider = resolve_provider(cfg, pipeline)

    if key == "vault_root":
        print(resolve_vault_root(config_path, cfg))
    elif key == "gemini_bin":
        # 向後相容
        print(resolve_llm_bin(cfg, "gemini"))
    elif key == "provider":
        print(provider)
    elif key == "llm_bin":
        print(resolve_llm_bin(cfg, provider))
    elif key == "llm_model":
        print(resolve_llm_model(cfg, pipeline, provider))
    elif key == "llm_fallback_model":
        print(resolve_llm_fallback_model(cfg, pipeline, provider))
    elif key == "llm_extra_flags":
        print(resolve_llm_extra_flags(cfg, provider))
    elif key == "model":
        # 向後相容：回傳當前 provider 的模型
        print(resolve_llm_model(cfg, pipeline, provider))
    elif key == "fallback_model":
        # 向後相容
        print(resolve_llm_fallback_model(cfg, pipeline, provider))
    else:
        # cooldown 等其他數值
        cooldowns = resolve_cooldowns(cfg, pipeline)
        if key in cooldowns:
            print(cooldowns[key])
        else:
            print(f"未知的 key: {key}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _cli()
