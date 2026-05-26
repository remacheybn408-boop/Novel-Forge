"""POST /api/chapters/scan + /api/chapters/read — scan directories and read chapter content."""
import re
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/chapters")

SKIP_DIRS = {".git", "__pycache__", "node_modules", "reports", "outputs", "backups", "logs", "tmp", ".pytest_cache"}

class ScanRequest(BaseModel):
    path: str

class ChapterInfo(BaseModel):
    id: str = ""
    number: int = 0
    title: str = ""
    filename: str = ""
    path: str = ""
    word_count: int = 0
    status: str = "scanned"

class ScanResponse(BaseModel):
    ok: bool = False
    path: str = ""
    chapter_count: int = 0
    total_words: int = 0
    chapters: list[ChapterInfo] = []
    message: str = ""

class ReadRequest(BaseModel):
    path: str

class ReadResponse(BaseModel):
    ok: bool = False
    title: str = ""
    content: str = ""
    word_count: int = 0
    message: str = ""


@router.post("/scan")
def api_scan(req: ScanRequest) -> dict:
    p = Path(req.path)
    if not p.exists() or not p.is_dir():
        return {"ok": False, "path": req.path, "chapter_count": 0, "total_words": 0, "chapters": [], "message": f"目录不可用: {req.path}"}

    chapters: list[dict] = []
    for fp in sorted(p.glob("*")):
        if fp.suffix.lower() not in (".txt", ".md", ".markdown"):
            continue
        if fp.name.startswith("."):
            continue
        m = re.match(r"第\s*(\d+)\s*章", fp.stem)
        num = int(m.group(1)) if m else 0
        title_part = fp.stem.replace(m.group(0), "").strip("-_—,. 　") if m else fp.stem
        text = fp.read_text(encoding="utf-8", errors="ignore")
        cn = len(re.findall(r"[\u4e00-\u9fff]", text))

        chapters.append({
            "id": f"chapter_{num:03d}",
            "number": num,
            "title": title_part or fp.stem,
            "filename": fp.name,
            "path": str(fp),
            "word_count": cn,
            "status": "scanned",
        })

    chapters.sort(key=lambda c: c["number"])
    total = sum(c["word_count"] for c in chapters)

    if not chapters:
        return {"ok": False, "path": req.path, "chapter_count": 0, "total_words": 0, "chapters": [], "message": "没有识别到 txt / md 章节文件"}

    return {"ok": True, "path": req.path, "chapter_count": len(chapters), "total_words": total, "chapters": chapters, "message": ""}


@router.post("/read")
def api_read(req: ReadRequest) -> dict:
    p = Path(req.path)
    if not p.exists() or not p.is_file():
        return {"ok": False, "title": "", "content": "", "word_count": 0, "message": f"文件不存在: {req.path}"}

    text = p.read_text(encoding="utf-8", errors="ignore")
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    # Extract title from first line
    first_line = text.strip().split("\n")[0] if text else p.stem
    title = first_line if first_line else p.stem

    return {"ok": True, "title": title, "content": text[:5000], "word_count": cn, "message": ""}
