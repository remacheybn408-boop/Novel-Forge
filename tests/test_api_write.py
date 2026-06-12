from pathlib import Path
import sqlite3

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api import main


def test_api_allows_local_web_origin():
    client = TestClient(main.app)
    response = client.options(
        "/api/stability-check",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


@pytest.fixture
def active_slot(tmp_path, monkeypatch):
    chapters = tmp_path / "workspace" / "slot_test" / "chapters"
    chapters.mkdir(parents=True)
    slot = {
        "active_slot": "slot_test",
        "slug": "test-novel",
        "title": "Test Novel",
        "db_path": None,
        "chapters_dir": str(chapters),
    }
    monkeypatch.setattr(main, "_slot_info", lambda: slot)
    monkeypatch.setattr(main, "_ALLOWED_DIRS", [tmp_path])
    return chapters


def test_save_chapter_content_creates_chapter_in_active_slot(active_slot):
    result = main.save_chapter_content(3, content="第一段正文", slug=None)

    chapter = active_slot / "第3章.txt"
    assert chapter.read_text(encoding="utf-8") == "第一段正文"
    assert result["data"]["chapter_no"] == 3
    assert result["data"]["backup"] is None


def test_save_chapter_content_keeps_only_ten_backups(active_slot):
    chapter = active_slot / "第2章.txt"
    chapter.write_text("初稿", encoding="utf-8")

    for index in range(12):
        main.save_chapter_content(2, content=f"版本{index}", slug=None)

    backups = sorted((active_slot.parent / "backups" / "chapter_002").glob("*.txt"))
    assert len(backups) == 10
    assert chapter.read_text(encoding="utf-8") == "版本11"


def test_get_chapter_content_reads_from_active_slot(active_slot):
    (active_slot / "第5章.txt").write_text("活跃档案章节", encoding="utf-8")

    result = main.get_chapter_content(5)

    assert result["data"]["content"] == "活跃档案章节"
    assert result["data"]["novel_slug"] == "test-novel"


def test_ai_action_rejects_unknown_action():
    request = main.AIActionRequest(action="translate", text="正文", chapter_no=1)

    with pytest.raises(HTTPException) as exc:
        main.write_ai_action(request)

    assert exc.value.status_code == 400


def test_ai_action_without_local_executor_returns_clear_error():
    request = main.AIActionRequest(action="polish", text="正文", chapter_no=1)

    with pytest.raises(HTTPException) as exc:
        main.write_ai_action(request)

    assert exc.value.status_code == 503
    assert "本地 AI" in str(exc.value.detail)


def test_scan_entities_empty_text_returns_empty_groups(active_slot):
    result = main.scan_entities(main.EntityScanRequest(text=""))

    assert result["data"] == {"characters": [], "locations": [], "terms": []}


def test_scan_entities_matches_character_and_location(active_slot, monkeypatch):
    db_path = active_slot.parent / "novel.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE characters (
            id INTEGER PRIMARY KEY, novel_id INTEGER, name TEXT, alias TEXT,
            role TEXT, identity TEXT, status TEXT
        );
        CREATE TABLE worldbuilding (
            id INTEGER PRIMARY KEY, novel_id INTEGER, category TEXT, title TEXT,
            content TEXT, importance INTEGER, tags TEXT
        );
        INSERT INTO characters VALUES (1, 1, '林舟', '小舟', '主角', '医生', 'active');
        INSERT INTO worldbuilding VALUES (1, 1, '地点', '雾港', '常年多雾的港口', 5, '港口');
        INSERT INTO worldbuilding VALUES (2, 1, '规则', '潮汐契约', '午夜生效', 4, '契约');
        """
    )
    conn.commit()
    conn.close()
    original_slot = main._slot_info()
    monkeypatch.setattr(main, "_slot_info", lambda: {**original_slot, "db_path": str(db_path)})

    result = main.scan_entities(main.EntityScanRequest(text="林舟抵达雾港。"))

    assert [item["name"] for item in result["data"]["characters"]] == ["林舟"]
    assert [item["title"] for item in result["data"]["locations"]] == ["雾港"]
    assert result["data"]["terms"] == []


def test_novel_agent_review_reuses_existing_review(active_slot, monkeypatch):
    (active_slot / "第6章.txt").write_text("待检查正文", encoding="utf-8")
    captured = {}

    def fake_review(content, chapter_no, mode):
        captured.update(content=content, chapter_no=chapter_no, mode=mode)
        return {
            "status": "PASS",
            "overall_score": 88,
            "summary": {"pass_count": 4, "warn_count": 0, "fail_count": 0},
            "_report_path": "reports/chapter_006_agent_review.json",
        }

    monkeypatch.setattr(main, "_run_existing_agent_review", fake_review)

    result = main.novel_agent_review(main.NovelAgentRequest(chapter_no=6))

    assert captured == {"content": "待检查正文", "chapter_no": 6, "mode": "full"}
    assert result["data"]["status"] == "PASS"
    assert result["data"]["report_path"].endswith("chapter_006_agent_review.json")


def test_novel_agent_review_requires_existing_chapter(active_slot):
    with pytest.raises(HTTPException) as exc:
        main.novel_agent_review(main.NovelAgentRequest(chapter_no=99))

    assert exc.value.status_code == 404


def test_core_response_keeps_legacy_success_and_adds_ok():
    assert main._ok(data={"value": 1}) == {
        "ok": True,
        "success": True,
        "data": {"value": 1},
        "output": "",
    }
    assert main._err("bad") == {
        "ok": False,
        "success": False,
        "error": "bad",
        "output": "",
    }


@pytest.mark.parametrize("slug", ["../outside", r"..\outside", "/absolute", r"C:\outside"])
def test_chapter_directory_rejects_unsafe_slug(slug):
    with pytest.raises(HTTPException) as exc:
        main._resolve_chapter_dir(slug)

    assert exc.value.status_code == 400


def test_safe_upload_filename_rejects_path_segments():
    assert main._safe_upload_filename("chapter.txt") == "chapter.txt"
    with pytest.raises(HTTPException):
        main._safe_upload_filename("../chapter.txt")
    with pytest.raises(HTTPException):
        main._safe_upload_filename("chapter.md")
