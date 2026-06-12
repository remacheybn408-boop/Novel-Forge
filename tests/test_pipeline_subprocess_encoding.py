from src.cli.commands_pipeline import _utf8_subprocess_options


def test_pipeline_capture_options_are_utf8_safe():
    options = _utf8_subprocess_options({"EXISTING": "1"})

    assert options["encoding"] == "utf-8"
    assert options["errors"] == "replace"
    assert options["env"]["EXISTING"] == "1"
    assert options["env"]["PYTHONIOENCODING"] == "utf-8"
