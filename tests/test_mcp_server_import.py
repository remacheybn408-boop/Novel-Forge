"""MCP 服务器导入测试。"""

def test_mcp_server_module_importable():
    """验证 mcp_server.server 可以正常导入。"""
    import mcp_server.server
    assert hasattr(mcp_server.server, "main")
    assert hasattr(mcp_server.server, "mcp")


def test_mcp_tools_module_importable():
    """验证 mcp_server.tools 所有工具函数可导入。"""
    import mcp_server.tools as t
    assert hasattr(t, "novel_menu")
    assert hasattr(t, "novel_status")
    assert hasattr(t, "novel_db_list")
    assert hasattr(t, "novel_outline_list")
    assert hasattr(t, "novel_outline_add")
    assert hasattr(t, "novel_chapters")
    assert hasattr(t, "novel_agents_review")
    assert hasattr(t, "novel_story_health")
    assert hasattr(t, "novel_report")
    assert hasattr(t, "novel_export_txt")


def test_mcp_safety_importable():
    """验证安全模块正确。"""
    from mcp_server.safety import is_allowed_command, is_path_safe, contains_forbidden
    assert callable(is_allowed_command)
    assert callable(is_path_safe)
    assert callable(contains_forbidden)
