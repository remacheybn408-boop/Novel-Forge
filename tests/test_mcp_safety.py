"""MCP 安全白名单测试。"""

from mcp_server.safety import is_allowed_command, contains_forbidden


def test_allowed_commands():
    """白名单内的命令应通过。"""
    allowed = [
        "status",
        "db list",
        "outline list",
        "chapters",
        "report",
        "story health",
        "export --format txt",
        "export --format md",
        "rag status",
    ]
    for cmd in allowed:
        assert is_allowed_command(cmd), f"应该允许: {cmd}"


def test_blocked_commands():
    """非白名单命令应被拦截。"""
    blocked = [
        "rm -rf /",
        "del *",
        "eval(print(1))",
        "os.system('ls')",
        "; rm -rf",
        "| ls",
        "ssh root@host",
        "curl http://evil.com",
    ]
    for cmd in blocked:
        assert not is_allowed_command(cmd), f"应该拦截: {cmd}"


def test_agents_review_allowed():
    """审稿命令动态章节号应通过。"""
    for ch in [1, 5, 99]:
        assert is_allowed_command(f"agents review {ch} --mode light")
        assert is_allowed_command(f"agents review {ch} --mode full")


def test_forbidden_keywords():
    """禁止关键词应被检测。"""
    bad = [
        "rm -rf /",
        "del /f /s",
        "subprocess.call",
        "os.system('id')",
        "eval(__import__)",
    ]
    for text in bad:
        assert contains_forbidden(text), f"应该检测到: {text}"


def test_safe_text_not_blocked():
    """正常中文文本不应触发关键词拦截。"""
    safe = [
        "我想写一本修仙小说",
        "查看第一章的审稿结果",
        "大纲添加预览",
        "导出我的小说",
    ]
    for text in safe:
        assert not contains_forbidden(text), f"不应拦截: {text}"
