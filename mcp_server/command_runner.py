"""command_runner.py — 安全执行 novel.py 命令

统一调用 novel.py 命令的入口。
负责超时、错误捕获、输出清理、返回中文摘要。
不暴露终端命令、路径、traceback 给普通用户。

v0.7.1: 支持两种调用方式：
  - run_command(cmd_str)   — 简单命令字符串（向后兼容）
  - run_command_args(args) — 参数列表（推荐，避免 shell 转义问题）
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

from .safety import (
    PROJECT_ROOT,
    is_allowed_command,
    is_allowed_args,
    SAFE_ERROR_MESSAGES,
)


# ── 各工具的超时设置（秒） ──
# key 为命令前缀，匹配 args 列表中前几个元素或 cmd_str 前缀
TIMEOUTS = {
    "status": 30,
    "board": 10,
    "db list": 10,
    "db current": 10,
    "db info": 10,
    "outline list": 10,
    "outline current": 10,
    "chapters": 10,
    "report": 20,
    "guards": 10,
    "agents review": 60,
    "jury": 60,
    "export": 60,
    "story health": 10,
    "voice list": 10,
    "character list": 10,
    "genre list": 10,
    "style list": 10,
    "rag status": 10,
    "outline add": 120,
    "stability-check": 300,
    "default": 30,
}


def _get_timeout(cmd_str: str) -> int:
    """获取命令的超时时间。"""
    for prefix, timeout in TIMEOUTS.items():
        if cmd_str.startswith(prefix):
            return timeout
    return TIMEOUTS["default"]


def _args_to_cmd_str(args: List[str]) -> str:
    """Convert argument list to command string for timeout lookup."""
    return " ".join(args)


def _clean_output(output: str) -> str:
    """清理命令输出，移除多余的空行和调试信息。

    保留中文内容，移除 traceback 等。
    """
    lines = output.split("\n")
    cleaned = []
    skip_traceback = False
    for line in lines:
        if line.startswith("Traceback"):
            skip_traceback = True
            continue
        if skip_traceback:
            if line.strip() == "" or line.startswith(" ") or line.startswith("\t"):
                continue
            skip_traceback = False
        # Filter out command echo from demo
        if line.strip().startswith("$ python novel.py"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def _exec(cmd_parts: List[str]) -> Tuple[bool, str, Optional[int]]:
    """Execute novel.py with the given argument list. Shared backend."""
    novel_py = PROJECT_ROOT / "novel.py"
    python_exe = sys.executable
    cmd_str = _args_to_cmd_str(cmd_parts)
    timeout = _get_timeout(cmd_str)

    try:
        start = time.time()
        result = subprocess.run(
            [python_exe, str(novel_py)] + cmd_parts,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
        duration_ms = (time.time() - start) * 1000

        output = result.stdout + result.stderr
        cleaned = _clean_output(output)

        if result.returncode == 0:
            return True, cleaned, 0
        else:
            if "ModuleNotFoundError" in output or "ImportError" in output:
                return False, SAFE_ERROR_MESSAGES["import_error"], result.returncode
            if cleaned:
                return False, cleaned, result.returncode
            return False, SAFE_ERROR_MESSAGES["execution_failed"], result.returncode

    except subprocess.TimeoutExpired:
        return False, SAFE_ERROR_MESSAGES["timeout"], None
    except Exception:
        return False, SAFE_ERROR_MESSAGES["unknown"], None


def run_command(cmd_str: str) -> Tuple[bool, str, Optional[int]]:
    """安全执行 novel.py 命令（字符串形式，向后兼容）。

    参数：
        cmd_str: 命令字符串，如 "status"、"db list"

    返回：
        (success, output_or_error_message, exit_code)
    """
    if not is_allowed_command(cmd_str):
        return False, SAFE_ERROR_MESSAGES["not_allowed"], None
    return _exec(cmd_str.split())


def run_command_args(args: List[str]) -> Tuple[bool, str, Optional[int]]:
    """安全执行 novel.py 命令（参数列表形式，推荐）。

    参数：
        args: 参数列表，如 ["status"]、["export", "--format", "txt", "--slug", "foo"]

    返回：
        (success, output_or_error_message, exit_code)
    """
    if not is_allowed_args(args):
        return False, SAFE_ERROR_MESSAGES["not_allowed"], None
    return _exec(args)
