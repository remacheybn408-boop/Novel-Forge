from src.cli.commands_diagnostic import _ascii_mark, _utf8_subprocess_options


def test_ascii_mark_is_safe_for_gbk_console():
    for value in (_ascii_mark(True), _ascii_mark(False), _ascii_mark(None)):
        value.encode("gbk")

    assert _ascii_mark(True) == "OK"
    assert _ascii_mark(False) == "FAIL"
    assert _ascii_mark(None) == "WARN"


def test_utf8_subprocess_options_force_child_and_parent_encoding():
    options = _utf8_subprocess_options({"EXISTING": "1"})

    assert options["encoding"] == "utf-8"
    assert options["errors"] == "replace"
    assert options["env"]["EXISTING"] == "1"
    assert options["env"]["PYTHONIOENCODING"] == "utf-8"
