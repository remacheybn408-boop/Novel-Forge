"""MCP 工具函数基本功能测试。"""

from mcp_server import tools


def test_novel_menu_returns_chinese():
    """novel_menu 应返回中文菜单。"""
    result = tools.novel_menu()
    assert isinstance(result, str)
    assert len(result) > 50
    # 应包含中文关键词
    keywords = ["小说", "菜单", "选择"]
    assert any(k in result for k in keywords), f"应包含中文关键词: {result[:100]}"


def test_novel_status_returns_string():
    """novel_status 应返回字符串。"""
    result = tools.novel_status()
    assert isinstance(result, str)


def test_outline_add_short_text_refused():
    """大纲正文过短时应被拒绝（预览模式）。"""
    result = tools.novel_outline_add(
        outline_text="短",
        title="测试",
        confirm_action=False,
    )
    assert "太短" in result or "至少" in result


def test_outline_add_preview_returns_hint():
    """大纲预览模式应返回操作提示。"""
    result = tools.novel_outline_add(
        outline_text="这是一个测试大纲，用于验证预览功能是否正常工作。",
        title="测试大纲",
        confirm_action=False,
    )
    assert isinstance(result, str)
    assert len(result) > 20


def test_export_only_txt_md():
    """导出格式仅允许 txt 和 md。"""
    result = tools.novel_export_txt(slug="", format="pdf")
    assert "仅支持" in result or "txt" in result


def test_export_txt_returns_string():
    """导出 txt 格式应返回结果字符串。"""
    result = tools.novel_export_txt(slug="", format="txt")
    assert isinstance(result, str)


def test_report_returns_string():
    """novel_report 应返回字符串。"""
    result = tools.novel_report()
    assert isinstance(result, str)


def test_db_list_returns_string():
    """novel_db_list 应返回字符串。"""
    result = tools.novel_db_list()
    assert isinstance(result, str)
