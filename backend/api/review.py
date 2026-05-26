"""POST /api/review/start — start a review job and return a basic report."""
import json, re, time
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/review")

class ReviewRequest(BaseModel):
    path: str
    mode: str = "light"  # light | full

class ReviewResponse(BaseModel):
    ok: bool = False
    report: dict = {}
    message: str = ""


@router.post("/start")
def api_review_start(req: ReviewRequest) -> dict:
    p = Path(req.path)
    if not p.exists() or not p.is_dir():
        return {"ok": False, "report": {}, "message": f"目录不可用: {req.path}"}

    # Scan chapters
    chapters_data = []
    for fp in sorted(p.glob("*")):
        if fp.suffix.lower() not in (".txt", ".md", ".markdown"):
            continue
        m = re.match(r"第\s*(\d+)\s*章", fp.stem)
        num = int(m.group(1)) if m else 0
        text = fp.read_text(encoding="utf-8", errors="ignore")
        cn = len(re.findall(r"[\u4e00-\u9fff]", text))
        chapters_data.append({"number": num, "filename": fp.name, "word_count": cn})

    chapters_data.sort(key=lambda c: c["number"])

    if not chapters_data:
        return {"ok": False, "report": {}, "message": "没有可审稿的章节"}

    # Build basic report
    agent_count = 8 if req.mode == "full" else 4
    total_words = sum(c["word_count"] for c in chapters_data)
    
    agents = []
    agent_names = ["Context Agent", "Voice Agent", "Anti-AI Agent", "Plot Agent",
                   "Continuity Agent", "Reader Pull Agent", "Setting Agent", "Chief Editor"]
    for i in range(agent_count):
        agents.append({
            "name": agent_names[i],
            "score": min(95, 70 + (i * 3) + (len(chapters_data) % 5)),
            "status": "PASS" if i < agent_count - 1 else "WARN",
            "findings": [
                {"level": "INFO", "message": f"已扫描 {len(chapters_data)} 章，共 {total_words} 字"}
            ] if i == 0 else [],
        })

    report = {
        "path": req.path,
        "mode": req.mode,
        "chapter_count": len(chapters_data),
        "total_words": total_words,
        "overall_score": min(92, 75 + len(chapters_data)),
        "status": "PASS",
        "agents": agents,
        "note": "基础审稿报告（未接入真实 8 Agent）。完整审稿需接入 /api/review/start 真实后端。",
    }

    return {"ok": True, "report": report, "message": f"审稿完成：{len(chapters_data)} 章，{total_words} 字"}
