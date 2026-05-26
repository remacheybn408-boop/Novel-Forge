"""POST /api/fs/validate-directory — check if a directory path is usable."""
import os
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/fs")

class ValidateRequest(BaseModel):
    path: str

class ValidateResponse(BaseModel):
    exists: bool = False
    is_dir: bool = False
    readable: bool = False
    message: str = ""

@router.post("/validate-directory")
def validate_directory(req: ValidateRequest) -> dict:
    p = Path(req.path)
    if not req.path.strip():
        return {"exists": False, "is_dir": False, "readable": False, "message": "路径为空"}
    if not p.exists():
        return {"exists": False, "is_dir": False, "readable": False, "message": f"目录不存在: {req.path}"}
    if not p.is_dir():
        return {"exists": True, "is_dir": False, "readable": False, "message": f"路径不是文件夹: {req.path}"}
    try:
        os.listdir(req.path)
        return {"exists": True, "is_dir": True, "readable": True, "message": "目录可用"}
    except PermissionError:
        return {"exists": True, "is_dir": True, "readable": False, "message": "没有读取权限"}
